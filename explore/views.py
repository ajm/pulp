# This file is part of PULP.
#
# PULP is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PULP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PULP.  If not, see <http://www.gnu.org/licenses/>.
import random
import json  
import time
import os.path
from math import log

from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view

from explore.models import Article, ArticleTFIDF, Experiment, ExperimentIteration, ArticleFeedback, User, TopicWeight
from explore.serializers import ArticleSerializer
from explore.utils import *
from explore.exceptions import PulpException
from explore.reinforcementlearning import linrel
from explore.informationretrieval import okapi_bm25


print "loading sparse linrel..."
X = load_sparse_linrel()
DEFAULT_NUM_ARTICLES = 20

class GetArticle(generics.RetrieveAPIView) :
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

@api_view(['GET'])
def logout_view(request):
    #logout(request)
    return Response(status=status.HTTP_200_OK)

def get_documents(articles_npid, correction=0) :
    articles_dbid = [ i + correction for i in articles_npid ] # database is 1-indexed, numpy is 0-indexed
    id2article = dict([ (a.id, a) for a in Article.objects.filter(pk__in=articles_dbid) ])
    return [ id2article[i] for i in articles_dbid ]

def get_top_articles_linrel(e, start, count) :
    global X

    articles_obj = ArticleFeedback.objects.filter(experiment=e).exclude(selected=None)
    articles_npid = [ a.article.id - 1 for a in articles_obj ] # database is 1-indexed, numpy is 0-indexed
    feedback = [ 1.0 if a.selected else 0.0 for a in articles_obj ]
    data = X

    articles_npid = linrel(articles_npid,
                           feedback,
                           data,
                           start,
                           count,
                           exploration_rate=e.exploration_rate)

    return get_documents(articles_npid, 1)

def get_top_articles_okapibm25(e, start, count) :
    return get_documents(okapi_bm25(e.query, start, count))

def classifier(e, post) :
    query_length = len(e.query.strip().split())

    if query_length >= 5 :
        return 0.0

    reading_time = 0.0
    cumulative_clicks = 0
    for c in post['clicked'] :
        reading_time += (c['reading_ended'] - c['reading_started'])
        cumulative_clicks += 1

    print "query length =", query_length
    print "reading time =", reading_time, "seconds"
    print "cumulative clicks =", cumulative_clicks

    if reading_time > 131 :
        if query_length > 3 :
            return 0.0 if cumulative_clicks > 2 else 1.0
        else :
            return 1.0
    else :
        return 0.0 if cumulative_clicks > 0 else 1.0

def regression(e, ei, post) :
    iteration_time = (timezone.now() - ei.date).total_seconds()
    reading_time = 0.0
    for c in post['clicked'] :
        reading_time += (c['reading_ended'] - c['reading_started'])
    interface_time = (iteration_time - reading_time) / 60.0 # minutes
    number_clicked = len(post['clicked'])

    is_kl_3 = e.knowledge_level == 3
    is_kl_4 = e.knowledge_level == 4

    print "interface time =", interface_time, "minutes"
    print "reading time =", reading_time / 60.0, "minutes"
    print "clicked documents =", number_clicked
    print "knowledge level =", e.knowledge_level

    exploration_rate = (0.29 * log(interface_time + 1)) + (0.22 * log(number_clicked + 1)) - (0.44 * is_kl_3) - (0.29 * is_kl_4) + 0.06

    return exploration_rate if exploration_rate > 0.0 else 0.0

def get_running_experiments(user) :
    return Experiment.objects.filter(user=user, state=Experiment.RUNNING)

def get_experiment(user) :
    e = get_running_experiments(user)

    if len(e) != 1 :
        e.update(state=Experiment.ERROR)
        return None

    return e[0]

def create_iteration(experiment, articles) :
    ei = ExperimentIteration()
    ei.experiment = experiment
    ei.iteration = experiment.number_of_iterations
    ei.save()

    for article in articles :
        afb = ArticleFeedback()
        afb.article = article
        afb.experiment = experiment
        afb.iteration = ei
        afb.save()

    return ei

def get_last_iteration(e) :
    return ExperimentIteration.objects.get(experiment=e, iteration=e.number_of_iterations-1)

def add_feedback(ei, articles, clickdata, seendata) :
    feedback = ArticleFeedback.objects.filter(iteration=ei)

    clicks = dict([ (c['id'], (c['reading_started'], c['reading_ended'])) for c in clickdata ])

    for fb in feedback :
        print "saving clicked=%s for %s" % (str(fb.article.id in articles), str(fb.article.id))
        fb.selected = fb.article.id in articles
        fb.clicked = fb.article.id in clicks
        fb.seen = fb.article.id in seendata

        if fb.clicked :
            fb.reading_start, fb.reading_end = clicks[fb.article.id]

        fb.save()

def store_feedback(e, post) :
    ei = get_last_iteration(e)
    selected_documents = [ int(i) for i in post['selected'] ]
    print selected_documents

    if ei.iteration == 0 :
        if e.experiment_type == Experiment.LOOKUP :
            e.exploration_rate = 0.0
        elif e.experiment_type == Experiment.EXPLORATORY :
            e.exploration_rate = 1.0
        elif e.experiment_type == Experiment.CLASSIFIER :
            e.exploration_rate = classifier(e, post)   
        elif e.experiment_type == Experiment.REGRESSION :
            e.exploration_rate = regression(e, ei, post)

    print "exploration rate set to %.2f" % e.exploration_rate

    # add selected documents to previous experiment iteration
    add_feedback(ei, selected_documents, post['clicked'], post['seen'])

@api_view(['GET'])
def textual_query(request) :
    if request.method == 'GET' :
        # experiments are started implicitly with a text query
        # and experiments are tagged with the session id
        print json.dumps(request.GET, sort_keys=True, indent=4, separators=(',', ': '))

        # get parameters from url
        if 'q' not in request.GET : #or 'participant_id' not in request.GET :
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
        query_string = request.GET['q']
        
        # auto-user [1/3]
        if ('participant_id' in request.GET) and request.GET['participant_id'] :
            participant_id = request.GET['participant_id']
        else :
            request.session.flush()
            participant_id = request.session.session_key

        # get user object
        try :
            user = User.objects.get(username=participant_id)

        except User.DoesNotExist :
            # auto-user [2/3]
            print "creating user '%s' ..." % participant_id
            user = User()
            user.username = participant_id
            user.save()

        # get experiment object
        e = get_experiment(user)

        if not e :
            # auto-user [3/3]
            e = Experiment()
            e.user                  = user
            e.experiment_type       = Experiment.EXPLORATORY
            e.knowledge_level       = 1
            e.exploration_rate      = 1.0
            e.number_of_documents   = int(request.GET['article-count'])
            e.query                 = query_string
            e.max_iterations        = 0
            e.save()
            #return Response(status=status.HTTP_400_BAD_REQUEST)

        num_articles = e.number_of_documents

        try :
            # get documents with okapi bm25-based ranking
            documents = get_top_articles_okapibm25(e, 0, num_articles)
        
        except PulpException, pe :
            print "error:", str(pe)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        # add random articles if we don't have enough
        fill_count = num_articles - len(documents)
        if fill_count :
            print "only %d articles found, adding %d random ones" % (len(articles), fill_count)
            documents += random.sample(Article.objects.all(), fill_count)

        # create new experiment iteration
        # save new documents to current experiment iteration
        create_iteration(e, documents)
        e.number_of_iterations += 1
        e.save()

        serializer = ArticleSerializer(documents, many=True)
        return Response({ 'articles' : serializer.data })

@api_view(['POST'])
def selection_query(request) :

    if request.method == 'POST' :
        post = json.loads(request.body)

        print json.dumps(post, sort_keys=True, indent=4, separators=(',', ': '))

        start_time = time.time()

        # auto-user
        if ('participant_id' in post) and post['participant_id'] :
            participant_id = post['participant_id']
        else :
            participant_id = request.session.session_key

        try :
            user = User.objects.get(username=participant_id)

        except User.DoesNotExist :
            print "user does not exist (%s) ..." % (participant_id)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # get experiment object
        e = get_experiment(user)

        #try :
        store_feedback(e, post)
        #except Exception :
        #    return Response(status=status.HTTP_400_BAD_REQUEST)


        # ver.3
        try :
            documents = get_top_articles_linrel(e, 0, e.number_of_documents)

        except PulpException, pe :
            print "error:", str(pe)
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
        print "%d articles (%s)" % (len(documents), ','.join([str(a.id) for a in documents]))

        # create new experiment iteration
        # save new documents to current experiment iteration
        create_iteration(e, documents)
        e.number_of_iterations += 1
        e.save()

        # response to client
        serializer = ArticleSerializer(documents, many=True)

        print "time elapsed:", time.time() - start_time, "seconds"

        return Response({'articles' : serializer.data })

@api_view(['GET'])
def system_state(request) :
    return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def end_search(request) :
    if request.method == 'POST' :
        post = json.loads(request.body)

        if ('participant_id' in post) and post['participant_id'] :
            participant_id = post['participant_id']
        else :
            participant_id = request.session.session_key

        try :
            user = User.objects.get(username=participant_id)
        except User.DoesNotExist :
            return Response(status=status.HTTP_400_BAD_REQUEST)

        e = get_experiment(user)

        try :
            store_feedback(e, post)
        except :
            return Response(status=status.HTTP_400_BAD_REQUEST)

        e.state = Experiment.COMPLETE
        e.save()

        return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
def index(request) :
    return render(request, 'index.html')

@api_view(['GET'])
def visualization(request) :
    return render(request, 'visualization.html')

@api_view(['GET'])
def setup_experiment(request) :
    # /setup?participant_id=1234&task_type=0&exploration_rate=1&task_order=1

    print json.dumps(request.GET, sort_keys=True, indent=4, separators=(',', ': '))

    try :
        participant_id      = request.GET['participant_id']
        num_documents       = int(request.GET['article_count'])
        num_iterations      = int(request.GET['iteration_count'])
        query               = request.GET['q']
        experiment_type     = request.GET['model']
        knowledge_level     = int(request.GET['knowledge_level'])

    except :
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if experiment_type not in ('lookup', 'exploratory', 'classifier', 'regression') :
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if num_documents < 1 or query == "" or num_iterations < 1 :
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if knowledge_level not in (2,3,4) :
        return Response(status=status.HTTP_400_BAD_REQUEST)

    try :
        user = User.objects.get(username=participant_id)

    except User.DoesNotExist :
        user = User()
        user.username = participant_id
        user.save()

    # check if there are any running experiments
    # and set them to ERROR
    Experiment.objects.filter(user=user, state=Experiment.RUNNING).update(state=Experiment.ERROR)

    # create experiment
    e = Experiment()
    e.user = user
    e.number_of_documents = num_documents
    e.max_iterations = num_iterations
    e.query = query
    e.knowledge_level = knowledge_level
    
    if experiment_type == 'lookup' :
        e.experiment_type = Experiment.LOOKUP
    elif experiment_type == 'exploratory' :
        e.experiment_type = Experiment.EXPLORATORY
    elif experiment_type == 'classifier' :
        e.experiment_type = Experiment.CLASSIFIER
    elif experiment_type == 'regression' :
        e.experiment_type = Experiment.REGRESSION

    e.save()

    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def experiment_ratings(request) :
    return Response(status=status.HTTP_404_NOT_FOUND)

    # old code
    ratings = json.loads(request.body)

    if('participant_id' not in ratings or 'task_type' not in ratings or 'study_type' not in ratings or 'ratings' not in ratings or 'classifier_value' not in ratings or 'query' not in ratings):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    ratings_file = open(os.path.dirname(__file__) + '/../ratings.json', 'r')
    ratings_arr = ratings_file.read()
    ratings_file.close()

    ratings_file = open(os.path.dirname(__file__) + '/../ratings.json', 'w')

    if(not ratings_arr):
        ratings_arr = []
    else:
        ratings_arr = json.loads(ratings_arr)

    ratings_arr.append({
        'participant_id': ratings['participant_id'],
        'task_type': ratings['task_type'],
        'study_type': ratings['study_type'],
        'classifier_value': ratings['classifier_value'],
        'query': ratings['query'],
        'ratings': ratings['ratings']
    })

    ratings_file.write(json.dumps(ratings_arr))
    ratings_file.close()

    return Response(status=status.HTTP_200_OK)

