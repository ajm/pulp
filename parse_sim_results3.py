from sys import stderr, argv, exit
from glob import glob

import os
import numpy
import scipy

from collections import defaultdict
from sklearn.metrics.pairwise import euclidean_distances


def load_data_sparse(prefix) :
    return scipy.sparse.csr_matrix((numpy.load(prefix + '.data.npy'),
                                    numpy.load(prefix + '.indices.npy'),
                                    numpy.load(prefix + '.indptr.npy')),
                                    shape=tuple(numpy.load(prefix + '.shape.npy')))

def load_data(directory) :
    return load_data_sparse(os.path.join(directory, 'linrel'))

def _parse_tokens(param_str) :
    
    in_quote = False
    token = ""

    for s in param_str :
        if s.isspace() and not in_quote and token :
            if token == '#' :
                token = ""

            elif token.count('=') == 1 :
                yield tuple([ t.strip() for t in token.split('=') ])
                token = ""

            else :
                raise Exception("bad token %s" % token)

            continue

        if s == '"' :
            in_quote = not in_quote
            continue

        token += s

def _attempt_value_casts(key, value) :
    for datatype in (int, float) :
        try :
            value = datatype(value)
            break

        except ValueError :
            continue

    return key,value

def parse_params(param_str) :
    return dict([ _attempt_value_casts(*kv) for kv in _parse_tokens(param_str) ])

def average(x) :
    return sum(x) / float(len(x))

def var(x, mean) :
    return average([ (i - mean) ** 2 for i in x ])

def cast_numeric(x) :
    try :
        return int(x)
    except ValueError :
        pass

    return float(x)

def cast_away(x) :
    return [ cast_numeric(i) for i in x ]

def finish(d, target) :
    for key in d :
        if target in [ a for a,m,v in d[key]] :
            return key
    
    return max(d.keys()) + 1

def dispersal(articles, data) :
    distances = euclidean_distances(data[ numpy.array(sorted(articles)), : ]).tolist()

    tmp = []
    for i in range(len(distances)) :
        for j in range(len(distances[i])) :
            if i != j and j > i :
                tmp.append(distances[i][j])

    m = average(tmp)
    return m, var(tmp, m), max(tmp)

def main() :
    FINISH_ONLY = False

    data = load_data('..')    

    #print "article iteration exploration distance mean variance"
    print "article iteration exploration avgdist mindist avgmean avgvar avgdisp vardisp maxdisp numexpdocs"

    for exploration_rate in [ i / 10.0 for i in range(0, 11, 2) ] :
        er = "%.1f" % exploration_rate
        #er = "%d" % exploration_rate
        dirname = "results3_%s" % er

        print >> stderr, "reading %s" % dirname

        for filename in glob("%s/results*txt" % dirname) :
            f = open(filename)

            params = parse_params(f.readline().strip())
            header = f.readline().strip().split()

            #print params

            distance = euclidean_distances(data, data[params['target'], :])
            distance = distance.transpose().tolist()[0]

            #print distances

            experiment = defaultdict(list)

            for line in f :
                iteration,article,feedback,mean,variance,from_exploration = cast_away(line.split())

                experiment[iteration].append((article, mean, variance, from_exploration))
                
                if not ((iteration == (params['num_iterations'] - 1)) and (len(experiment[iteration]) == params['num_shown'])) :
                    continue
                
                # ----------

                if FINISH_ONLY :
                    last_iter = finish(experiment, params['target'])
                
                    if last_iter == params['num_iterations'] :
                        experiment.clear()
                        continue
                else :
                    last_iter = params['num_iterations']

                # ----------

                for i in sorted(experiment.keys()) :
                    if i <= last_iter :
                        articles = []
                        distances = []
                        means = []
                        variances = []
                        from_exploration_count = 0

                        for a,m,v,e in experiment[i] :
                            articles.append(a)
                            distances.append(distance[a])
                            means.append(m)
                            variances.append(v)
                            from_exploration_count += e

                        
                        avgdisp, vardisp, maxdisp = dispersal(articles, data)

                        print params['target'], \
                                i, \
                                er, \
                                average(distances), \
                                min(distances), \
                                average(means), \
                                average(variances), \
                                avgdisp, \
                                vardisp, \
                                maxdisp, \
                                from_exploration_count

                experiment.clear()

            f.close()

    return 0

if __name__  == '__main__' :
    try :
        exit(main())
    except KeyboardInterrupt :
        print >> stderr, "Killed by user..."
        exit(1)

