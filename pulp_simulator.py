import sys
import numpy
import scipy
import json
import itertools
import random

from sys import stderr, exit, argv
from scipy.sparse.linalg import spsolve
from sklearn.metrics.pairwise import euclidean_distances
from nltk.stem import SnowballStemmer

def load_data_sparse(prefix) :
    return scipy.sparse.csr_matrix((numpy.load(prefix + '.data.npy'),
                                    numpy.load(prefix + '.indices.npy'),
                                    numpy.load(prefix + '.indptr.npy')),
                                    shape=tuple(numpy.load(prefix + '.shape.npy')))

def load_data() :
    return load_data_sparse('linrel')

def load_features_json(fname) :
    with open(fname) as f :
        return json.load(f)

def load_features() :
    return load_features_json('linrel_features.json')

def order_keys_by_value(d) :
    return [ i[0] for i in sorted(d.items(), key=lambda x : x[1], reverse=True) ]

def okapi_bm25(query, n, data, features) :
    stemmer = SnowballStemmer('english')
    query_terms = [ stemmer.stem(term) for term in query.lower().split() ]

    tmp = {}

    for qt in query_terms :
        if qt not in features :
            continue

        findex = features[qt]

        for aindex in numpy.nonzero(data[:, findex])[0] :
            akey = aindex.item()
            if akey not in tmp :
                tmp[akey] = 1.0

            tmp[akey] *= data[aindex,findex]

    return order_keys_by_value(tmp)[:n]

def linrel(articles, feedback, n, data, features, mew=1.0, exploration_rate=0.05) :
    assert len(articles) == len(feedback), "articles and feedback are not the same length"

    X = data

    num_articles = X.shape[0]
    num_features = X.shape[1]

    X_t = X[ numpy.array(articles) ]
    X_tt = X_t.transpose()

    I = mew * scipy.sparse.identity(num_features, format='dia')

    W = spsolve((X_tt * X_t) + I, X_tt)
    A = X * W

    Y_t = numpy.matrix(feedback).transpose()

    tmpA = numpy.array(A.todense())
    normL2 = numpy.matrix(numpy.sqrt(numpy.sum(tmpA * tmpA, axis=1))).transpose()

    # W * Y_t is the keyword weights
    K = W * Y_t

    tmp = (A * Y_t)
    I_t = tmp + (exploration_rate * normL2)

    linrel_ordered = numpy.argsort(I_t.transpose()[0]).tolist()[0]
    top_n = []

    for i in linrel_ordered[::-1] :
        if i not in articles :
            top_n.append(i)

        if len(top_n) == n :
            break

    return top_n

def average_distance_to_target(articles, target, distances) :
    return numpy.min(distances[ numpy.array(articles) ])

def main() :
    # constants
    num_shown = 10
    num_iterations = 10
    num_selections = [0,1,2] #= range(num_shown + 1)
    test_explore_rate = 0.05

    # load the data
    data = load_data()
    num_articles = data.shape[0]
    num_features = data.shape[1]

    print "loaded %d articles x %d features" % (num_articles, num_features)
    features = load_features()
    print "loaded %d features" % len(features)

    # make sure the data is consistent
    assert len(features) == num_features, \
            "the number of features differed in the matrix vs the feature list"

    # pick a target document 
    experiment_query = "machine learning"
    experiment_target = random.randint(0, num_articles-1)

    # precalculate all the distance between all documents and the target 
    print "calculating distances to article %d" % experiment_target
    experiment_distances = euclidean_distances(data, data[experiment_target, :])

    # run an initial query using tfidf
    print "running okapi bm25 with query '%s'" % experiment_query
    experiment_articles = okapi_bm25(experiment_query, num_shown, data, features)
    experiment_feedback = []

    # run for X iterations
    for iteration in range(num_iterations) :
        count = 0
        print >> stderr, "iter %d - %d" % (iteration, count),

        # do the first one outside of the loop so we can 
        best_feedback = None
        best_average_distance = sys.float_info.max
        best_version = -1

        # user can pick 0 -> 10 articles
        for i in num_selections :
            # go through all possible combinations of feedback
            # to select what the user does
            for selections in itertools.combinations(range(num_shown), i) :
                feedback = [ 1.0 if i in selections else 0.0 for i in range(num_shown)]
                
                # run linrel without exploration using generated feedback
                linrel_articles = linrel(experiment_articles, 
                                         experiment_feedback + feedback, 
                                         num_shown, 
                                         data, 
                                         features, 
                                         exploration_rate=0.0)
                
                # test if these documents are better than the 'current best feedback' 
                # based on average (?) distance to target
                average_distance = average_distance_to_target(linrel_articles, 
                                                              experiment_target, 
                                                              experiment_distances)
                
                if average_distance < best_average_distance :
                    best_version = count
                    best_feedback = feedback
                    best_average_distance = average_distance

                count += 1
                print >> stderr, "\riter %d - %d (best = %d, distance = %f)" % (iteration, count, best_version, best_average_distance),

        print >> stderr, ""
        experiment_feedback += best_feedback
        experiment_articles += linrel(experiment_articles, 
                                      experiment_feedback, 
                                      num_shown, 
                                      data, 
                                      features, 
                                      exploration_rate=test_explore_rate)

    # calculate some dependent variable to summarise this run of the simulator XXX 
    print experiment_articles

    return 0

if __name__ == '__main__' :
    try :
        exit(main())
    
    except KeyboardInterrupt :
        print >> stderr, "Killed by User...\n"
        exit(1)

