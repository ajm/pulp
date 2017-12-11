import re
from nltk.stem import SnowballStemmer
from exceptions import PulpException
from explore.utils import *

badchars_pat = re.compile("[^a-zA-Z\s]")

# query terms - a list of stemmed query words
# n - the number of articles to return
#@timecall(immediate=True)
def okapi_bm25(query, start_index, num_articles) :
    bm25 = load_sparse_bm25()
    features = load_features_bm25()

    query = badchars_pat.sub(' ', query).lower()

    stemmer = SnowballStemmer('english')
    query_terms = [ stemmer.stem(term) for term in query.split() ]
    query_terms = [ term for term in query_terms if term in features ]

    if not len(query_terms) :
        raise PulpException("query string (\"%s\") contains no query terms" % (query))
   
    tmp = {}
    for qt in query_terms :
        findex = features[qt]

        for aindex in numpy.nonzero(bm25[:, findex])[0] :
            akey = aindex.item()
            if akey not in tmp :
                tmp[akey] = 0.0

            tmp[akey] += bm25[aindex,findex]

    ranking = sorted(tmp.items(), key=lambda x : x[1], reverse=True)

    # find top n articles in date range
    top_ids = []
    for i in ranking :
        top_ids.append(i[0] + 1) # +1 because db is one indexed

        if len(top_ids) == (start_index + num_articles) :
            break

    return top_ids[-num_articles:]

#    id2article = dict([ (a.id, a) for a in Article.objects.filter(pk__in=top_ids) ])
#    top_articles = [ id2article[i] for i in top_ids ]
#    return top_articles

