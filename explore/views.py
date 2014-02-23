#from django.contrib.auth.models import User #, Group
#from django.contrib.auth import logout
from django.db.models import Q
#from rest_framework import viewsets
#from explore.serializers import UserSerializer

from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView # class-based views
from rest_framework.decorators import api_view # for function-based views

from explore.models import Article, ArticleTFIDF, Experiment, ExperimentIteration, ArticleFeedback
from explore.serializers import ArticleSerializer
from explore.utils import *

from sklearn.preprocessing import normalize

from scipy.sparse.linalg import spsolve

import sys
import random
import operator
import numpy


DEFAULT_NUM_ARTICLES = 10

#class UserViewSet(viewsets.ModelViewSet):
#    queryset = User.objects.all()
#    serializer_class = UserSerializer

class GetArticle(generics.RetrieveAPIView) :
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

#class GetArticleOld(APIView) :
#    def get(self, request, article_id) :
#        try :
#            article = Article.objects.get(id=article_id)
#
#        except Article.DoesNotExist :
#            return Response(status=status.HTTP_404_NOT_FOUND)
#
#        serializer = ArticleSerializer(article)
#        return Response(serializer.data)


@api_view(['GET'])
def logout_view(request):
    #logout(request)
    return Response(status=status.HTTP_200_OK)

def get_top_articles(tfidfs, n) :
    """
    return top n articles using tfidf terms,
    ranking articles using okapi_bm25
    """
    tmp = {}

    for tfidf in tfidfs :
        if tfidf.article not in tmp :
            tmp[tfidf.article] = 1.0

        tmp[tfidf.article] *= tfidf.value

    ranking = sorted(tmp.items(), key=lambda x : x[1], reverse=True)

    return [ r[0] for r in ranking[:n] ]

def get_top_articles_linrel(e) :
    X = load_sparse_articles()
    print "X %s" % str(X.shape)
    num_articles = X.shape[0]
    num_features = X.shape[1]

    seen_articles = ArticleFeedback.objects.filter(experiment=e)

    X_t = X[ numpy.array([ a.article.id for a in seen_articles ]) ]
    X_tt = X_t.transpose()

    print "X_t %s\nX_tt %s" % (str(X_t.shape), str(X_tt.shape))

    mew = 0.5
    I = mew * scipy.sparse.identity(num_features, format='dia')
    
    print "I %s" % str(I.shape)

    #A = (X * ((X_tt * X_t) + I).todense().getI()) * X_tt
    #A = X * (((X_tt * X_t) + I).todense().getI() * X_tt)
    A = X * spsolve((X_tt * X_t) + I, X_tt)

    print "A %s" % str(A.shape)

    Y_t = numpy.matrix([ 1.0 if a.selected else 0.0 for a in seen_articles ]).transpose()

    print "Y_t %s" % str(Y_t.shape)

    #tmpA = numpy.array(A.todense()) 
    #print "tmpA %s" % str(tmpA.shape)
    #normL2 = numpy.matrix(numpy.sqrt(numpy.sum(tmpA * tmpA, axis=1))).transpose()
    #normalize(A, norm='l2', copy=False)

    #print "normL2 %s" % str(normL2.shape)

    tmp = (A * Y_t)
    normalize(A, norm='l2', copy=False)
    I_t = tmp + (0.05 * A)
    print "I_t %s" % str(I_t.shape)
    
    #top_n = sorted(zip(I_t.transpose().tolist()[0], range(num_articles)), reverse=True)[:e.number_of_documents]
    seen_ids = [ a.article.id for a in seen_articles ]
    linrel_ordered = sorted(zip(I_t.transpose().tolist()[0], range(num_articles)), reverse=True)
    top_n = []

    for i in linrel_ordered :
        if i[1] not in seen_ids :
            top_n.append(i[1])
        if len(top_n) == e.number_of_documents :
            break

    #print "top_n %s" % str(top_n)
    #top_n = [ i[1] for i in top_n ]
    #return Article.objects.filter(pk__in=top_n)

    id2articles = dict([ (a.id, a) for a in Article.objects.filter(pk__in=top_n) ])
    print top_n
    print id2articles
    return [ id2articles[i] for i in top_n ]



def get_running_experiments(sid) :
    return Experiment.objects.filter(sessionid=sid, state=Experiment.RUNNING)

def create_experiment(sid, user, num_documents) :
    get_running_experiments(sid).update(state=Experiment.ERROR)

    e = Experiment()

    e.sessionid = sid
    e.number_of_documents = num_documents
    #e.user = user

    e.save()

    return e

def get_experiment(sid) :
    e = get_running_experiments(sid)

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

def add_feedback(ei, articles) :
    feedback = ArticleFeedback.objects.filter(iteration=ei)

    for fb in feedback :
        print "saving clicked=%s for %s" % (str(fb.article.id in articles), str(fb.article.id))
        fb.selected = fb.article.id in articles
        fb.save()

def get_unseen_articles(e) :
    return Article.objects.exclude(pk__in=[ a.article.id for a in ArticleFeedback.objects.filter(experiment=e) ])

@api_view(['GET'])
def textual_query(request) :
    if request.method == 'GET' :
        # experiments are started implicitly with a text query
        # and experiments are tagged with the session id
        request.session.flush()
        #print request.session.session_key

        # get parameters from url
        # q : query string
        if 'q' not in request.GET :
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        query_string = request.GET['q']
        query_terms = query_string.lower().split()

        print "query: %s" % str(query_terms)

        if not len(query_terms) :
            return Response(status=status.HTTP_404_NOT_FOUND)

        # article-count : number of articles to return
        num_articles = int(request.GET.get('article-count', DEFAULT_NUM_ARTICLES))

        print "article-count: %d" % (num_articles)

        # create new experiment
        e = create_experiment(request.session.session_key, None, num_articles) #request.user, num_articles)

        # get documents with TFIDF-based ranking 
        try :
            tfidf_query = reduce(operator.or_, [ Q(term=t) for t in query_terms ])
            tfidfs = ArticleTFIDF.objects.select_related('article').filter(tfidf_query)
            articles = get_top_articles(tfidfs, num_articles)
            print "%d articles found (%s)" % (len(articles), ','.join([str(a.id) for a in articles]))

        except ArticleTFIDF.DoesNotExist :
            print "no articles found containing search terms"
            articles = []
        
        # add random articles if we don't have enough
        fill_count = num_articles - len(articles)
        if fill_count :
            print "only %d articles found, adding %d random ones" % (len(articles), fill_count)
            articles += random.sample(Article.objects.all(), fill_count)
        
        # create new experiment iteration
        # save new documents to current experiment iteration 
        create_iteration(e, articles)
        e.number_of_iterations += 1
        e.save()

        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def selection_query(request) :
    if request.method == 'GET' :
        # get experiment object
        e = get_experiment(request.session.session_key)
        # get previous experiment iteration
        try :
            ei = get_last_iteration(e)

        except ExperimentIteration.DoesNotExist :
            return Response(status=status.HTTP_404_NOT_FOUND)

        # get parameters from url
        # ?id=x&id=y&id=z
        try :
            selected_documents = [ int(i) for i in request.GET.getlist('id') ]
        except ValueError :
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        print selected_documents

        # add selected documents to previous experiment iteration
        add_feedback(ei, selected_documents)

        # get documents with ML algorithm 
        # remember to exclude all the articles that the user has already been shown
        all_articles = get_unseen_articles(e)
        #rand_articles = random.sample(all_articles, e.number_of_documents)
        rand_articles = get_top_articles_linrel(e)

        print "%d articles left to choose from" % len(all_articles)
        print "%d articles found (%s)" % (len(rand_articles), ','.join([str(a.id) for a in rand_articles]))

        # create new experiment iteration
        # save new documents to current experiment iteration
        create_iteration(e, rand_articles)
        e.number_of_iterations += 1
        e.save()

        # response to client
        serializer = ArticleSerializer(rand_articles, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def end_search(request) :
    if request.method == 'GET' :
        e = get_experiment(request.session.session_key)
        e.state = Experiment.COMPLETE
        e.save()
        return Response(status=status.HTTP_200_OK)

