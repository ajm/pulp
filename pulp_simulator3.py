import sys
import numpy
import scipy
import json
import itertools
import random
import os

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

def linrel(articles, feedback, n, data, features, mew=1.0, exploration_rate=0.1) :
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

    mean = A * Y_t
    variance = (exploration_rate / 2.0) * normL2
    I_t = mean + variance 

    linrel_ordered = numpy.argsort(I_t.transpose()[0]).tolist()[0]
    top_n = []

    for i in linrel_ordered[::-1] :
        if i not in articles :
            top_n.append(i)

        if len(top_n) == n :
            break

    return top_n, \
           mean[ numpy.array(top_n) ].transpose().tolist()[0], \
           variance[ numpy.array(top_n) ].transpose().tolist()[0]

def average_distance_to_target(articles, target, distances) :
    return numpy.min(distances[ numpy.array(articles) ])

def main() :
    if len(argv) != 6 :
        print >> stderr, "Usage: %s <output dir> <exploration rate> <documents shown per iteration> <num iterations> <> <article index + keywords>" % argv[0]
        exit(1)

    # parse input
    results_dir = argv[1]
    if not os.path.isdir(results_dir) :
        print >> stderr, "Error, %s is not a directory/does not exist!" % results_dir
        exit(1)

    try :
        test_explore_rate = float(argv[2])
        num_shown = int(argv[3])
        num_iterations = int(argv[4])

    except ValueError :
        print >> stderr, "Error, %s is not a float!" % argv[3]
        exit(1)

    try :
        #experiment_target = int(argv[1]) if argv[1] != 'random' else None
        tmp = argv[5].split()
        experiment_target = int(tmp[0])
        experiment_query = " ".join(tmp[1:])

    except ValueError :
        print >> stderr, "Error, %s is not an integer!" % argv[1]
        exit(1)

    print "test_explore_rate =", test_explore_rate
    print "num_shown =",         num_shown
    print "num_iterations =",    num_iterations
    print "experiment_target =", experiment_target
    print "experiment_query =",  experiment_query

    # constants
#    num_shown = 10
#    num_iterations = 10
    num_selections = range(num_shown + 1)

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

    # test if this has been done before
    out_filename = results_filename(results_dir, experiment_target)
    if os.path.exists(out_filename) :
        print "%s exists, exiting..." % out_filename
        exit(0)

    # precalculate all the distances between all documents and the target 
    print "calculating distances to article %d" % experiment_target
    experiment_distances = euclidean_distances(data, data[experiment_target, :])

    # run an initial query using tfidf
    print "running okapi bm25 with query '%s'" % experiment_query
    experiment_articles = okapi_bm25(experiment_query, num_shown, data, features)
    experiment_exploration_articles = [0] * num_shown # we have not done linrel yet, so none are exploration
    experiment_feedback = []    # these three lists
    experiment_means = []       # will lag behind experiment_articles
    experiment_variances = []   # and experiment_exploration_articles by one iteration

    # run for X iterations
    for iteration in range(num_iterations) :
        remaining_articles = range(num_shown)
        selected_articles = []

        # BASE AVERAGE SHOULD BE WITH NO SELECTIONS
        articles,means,variances = linrel(experiment_articles,
                                          experiment_feedback + ([0.0] * num_shown),
                                          num_shown,
                                          data,
                                          features,
                                          exploration_rate=0.0)

        current_average_distance = average_distance_to_target(articles,
                                                              experiment_target,
                                                              experiment_distances)
        current_returned_articles = articles

        print >> stderr, "test %d: distance=%.3f selections=%s" % (iteration, current_average_distance, str(selected_articles))
        for i in num_selections :

            best_article = None
            best_average_distance = sys.float_info.max
            best_returned_articles = None

            for a in remaining_articles :
                tmp = selected_articles + [a]
                feedback = [ 1.0 if i in tmp else 0.0 for i in range(num_shown) ]

                # run linrel without exploration using generated feedback
                articles,means,variances = linrel(experiment_articles,
                                                  experiment_feedback + feedback,
                                                  num_shown,
                                                  data,
                                                  features,
                                                  exploration_rate=0.0)


                # test if these documents are better than the 'current best feedback' 
                # based on average (?) distance to target
                average_distance = average_distance_to_target(articles,
                                                              experiment_target,
                                                              experiment_distances)

                # keep a note of the article selection that resulted in the min distance to the target
                if average_distance < best_average_distance :
                    best_article = a
                    best_average_distance = average_distance
                    best_returned_articles = articles
                    print >> stderr, "test %d: distance=%.3f selections=%s" % (iteration, best_average_distance, str(selected_articles + [a]))

            # test to see if the best article to add actually increases the distance
            # to the target
            if best_average_distance >= current_average_distance :
                print >> stderr, "stop %d: distance=%.3f selections=%s" % (iteration, current_average_distance, str(selected_articles))
                break

            selected_articles.append(best_article)
            remaining_articles.remove(best_article)
            current_average_distance = best_average_distance
            current_returned_articles = best_returned_articles

        print >> stderr, ""

        best_feedback = [ 1.0 if i in selected_articles else 0.0 for i in range(num_shown) ]
        
        # we now know what to select, run the actual linrel code with 
        # actual exploration rate 
        experiment_feedback += best_feedback
        articles,means,variances = linrel(experiment_articles, 
                                          experiment_feedback, 
                                          num_shown, 
                                          data, 
                                          features, 
                                          exploration_rate=test_explore_rate)
        
        # how many documents were shown due to test_exploration_rate?
        exploration_articles = [ 0 if a in current_returned_articles else 1 for a in articles ]

        true_average_distance = average_distance_to_target(articles,
                                                           experiment_target,
                                                           experiment_distances)

        print >> stderr, "iter %d: distance=%.3f selections=%s" % (iteration, true_average_distance, str(selected_articles))
        print >> stderr, ""

        # store everything
        experiment_articles.extend(articles)
        experiment_means.extend(means)
        experiment_variances.extend(variances)
        experiment_exploration_articles.extend(exploration_articles)

    #print experiment_articles
    #print [ int(i) for i in experiment_feedback ]
    #print experiment_means
    #print experiment_variances

    guff = {
            "out_filename" : out_filename,
            "target" : experiment_target,
            "query" : experiment_query,
            "exploration_rate" : test_explore_rate,
            "num_shown" : num_shown,
            "num_iterations" : num_iterations,
            "num_articles" : num_articles,
            "num_features" : num_features
           }

    # save to file
    write_pulp_results(guff,
                       experiment_articles, 
                       experiment_feedback, 
                       experiment_means, 
                       experiment_variances,
                       experiment_exploration_articles)

    return 0

def results_filename(results_dir, target) :
    return os.path.join(results_dir, "results%d.txt" % target)

def write_pulp_results(settings, articles, feedback, means, variances, is_exploration) :
    delimit = " "
    header = ["iteration", "article", "feedback", "mean", "variance"]
    filename = settings["out_filename"]

    with open(filename, 'w') as f :
        print >> f, "# " + " ".join([ "%s=%s" % (k, '"%s"' % v if isinstance(v, str) else str(v)) for k,v in settings.items() ])
        print >> f, delimit.join(header)
        
        iterations = sorted(range(settings["num_iterations"]) * settings["num_shown"])
        feedback = [ int(i) for i in feedback ]

        for i in zip(iterations, articles, feedback, means, variances, is_exploration) :
            print >> f, "%d %d %d %e %e %d" % i

    print "wrote %s" % filename

if __name__ == '__main__' :
    try :
        exit(main())
    
    except KeyboardInterrupt :
        print >> stderr, "Killed by User...\n"
        exit(1)

