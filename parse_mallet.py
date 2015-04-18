from sys import exit, stderr, argv
from collections import defaultdict, Counter
import json
import random


def parse_mallet_topics(fname) :
    tmp = []
    
    with open(fname) as f :
        for line in f :
            tmp.append(line.strip().split('\t')[2:])
    
    return tmp

def parse_mallet_topics_annotated(fname) :
    tmp = []
    
    with open(fname) as f :
        for line in f :
            dat = line.strip().split('\t')
            tmp.append((dat[0], dat[3:]))
    
    return tmp

def parse_mallet_articles(fname) :
    tmp = defaultdict(list)

    with open(fname) as f :
        f.readline() # header
        
        linenum = 2

        for line in f :
            data = line.strip().split("\t")
            article = int(data[0])

            for i in range(2, len(data), 2) :
                try :
                    topic_id = int(data[i])
                    topic_prob = float(data[i+1])

                    tmp[article].append((topic_id, topic_prob))
                
                except ValueError, ve :
                    print >> stderr, "Error on line %d (%s)" % (linenum, str(ve))
                    exit(1)

            linenum += 1

    return tmp

def main() :
    verbose = False

    if len(argv) != 4 :
        print >> stderr, "Usage %s <key file> <composition file> <n>"
        print >> stderr, "\t we assume that the key file has an additional column prepended of human annotations"
        print >> stderr, "\t n = number of docs to print out"
        exit(1)

    key_file = argv[1]
    composition_file = argv[2]
    num_to_print = int(argv[3])

#    arxiv_topics = json.load(open("../linrel_topics.json"))
#    print "read %d arxiv articles+topics" % len(arxiv_topics)
#
#    machine_learning_articles = [ a for a in arxiv_topics if 'stat.ML' in arxiv_topics[a] ]
#    print "\t%d/%d arxiv articles are from stat.ML" % (len(machine_learning_articles), len(arxiv_topics))

    #mallet_topics = parse_mallet_topics("80000keys.txt")
    mallet_topics = parse_mallet_topics_annotated(key_file)
    if verbose :
        print "read %d mallet topics" % len(mallet_topics)

    ambiguous_topics = [ index for index,value in enumerate(mallet_topics) if 'ambiguous' in value[0] ]
    if verbose :
        print "\t%d/%d mallets topics were ambiguous" % (len(ambiguous_topics), len(mallet_topics))
    
    mallet_articles = parse_mallet_articles(composition_file)
    if verbose :
        print "read %d mallet articles" % len(mallet_articles)

#    ml_topics = Counter()
#
#    for mla in machine_learning_articles :
#        topic_id, topic_prob = mallet_articles[mla][0]
#        ml_topics[topic_id] += 1
#
#    print "%d/%d topics are related to articles from stat.ML" % (len(ml_topics), len(mallet_topics))
#    ml_filename = 'machine_learning_topics.txt'
#
#    with open(ml_filename, 'w') as f :
#        for t in ml_topics :
#            print >> f, " ".join([ str(t), str(ml_topics[t]) ] + mallet_topics[t][1])
#
#    print "wrote %s" % ml_filename

    article2topic = {}
    topic_choice = []

    for aid in sorted(mallet_articles.keys()) :
        for index,value in enumerate(mallet_articles[aid]) :
            tid,tprob = value
            if tid not in ambiguous_topics :
                article2topic[aid] = tid
                topic_choice.append(index)
                break

    if verbose :
        for i in sorted(set(topic_choice)) :
            print "\t%d/%d mallet articles were assigned %d-th topic" % (topic_choice.count(i), len(mallet_articles), i)

    
    
    article_and_query = []

    weak_topics = ('probability', 'inference', 'vision', 'theory', 'optimisation', 'dimensionality', 'likelihood', 'speech')

    for article,topic in article2topic.items() :
        topic = mallet_topics[topic][0]

        #print article,topic

        if topic.startswith('ml') and ('generic' not in topic) and ('?' not in topic) :
            query = topic.replace('/', ' ').replace('ml', 'machine learning').replace('nlp', 'natural language processing')
        
            ignore = False
            for wt in weak_topics :
                if wt in query :
                    ignore = True
                    break
            if ignore :
                continue

            article_and_query.append((article, "'%s'" % query))

    random.seed(37)    
    random.shuffle(article_and_query)
    for a,q in article_and_query[:num_to_print] :
        print a,q

    return 0

if __name__ == '__main__' :
    try :
        exit(main())
    except KeyboardInterrupt :
        print >> stderr, "Killed by user"
        exit(1)

