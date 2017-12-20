import re
import numpy as np
from nltk.stem import SnowballStemmer
from exceptions import PulpException
from explore.utils import *
from scipy.sparse import vstack


badchars_pat = re.compile("[^a-zA-Z\s]")

def get_query_terms(query, features) :
    query = badchars_pat.sub(' ', query).lower()

    stemmer = SnowballStemmer('english')
    query_terms = [ stemmer.stem(term) for term in query.split() ]
    query_terms = [ term for term in query_terms if term in features ]

    if not len(query_terms) :
        raise PulpException("query string (\"%s\") contains no query terms" % (query))

    return query_terms

def okapi_bm25(query, start_index, num_articles, bm25, bm25_features, linrel, max_corpus=10000, use_subset=False) :
    _okapi_bm25 = okapi_bm25_subset if use_subset else okapi_bm25_nosubset
    return _okapi_bm25(query, start_index, num_articles, bm25, bm25_features, linrel, max_corpus)

def okapi_bm25_subset(query, start_index, num_articles, bm25, bm25_features, linrel, max_corpus=10000) :
    #bm25 = load_sparse_bm25()
    #bm25_features = load_features_bm25()

    query_terms = get_query_terms(query, bm25_features)

    tmp = {}
    for qt in query_terms :
        findex = bm25_features[qt]

        for aindex in numpy.nonzero(bm25[:, findex])[0] :
            akey = aindex.item()
            if akey not in tmp :
                tmp[akey] = 0.0

            tmp[akey] += bm25[aindex,findex]

    ranking = sorted(tmp.items(), key=lambda x : x[1], reverse=True)
    print "ranked %d documents" % len(ranking)

    top_ids = []
    for i in ranking :
        top_ids.append(i[0])

        if len(top_ids) == (start_index + num_articles) :
            break

    # make subset of the data
    submatrix = []
    mapping = {}
    for index,docid_score in enumerate(ranking[:max_corpus]) :
        docid,score = docid_score
        submatrix.append(linrel[docid,:])
        mapping[index] = docid
    submatrix = vstack(submatrix, "csr")
    save_sparse(submatrix, query.replace(' ', '_'))
    save_features(mapping, "%s_mapping.json" % query.replace(' ', '_'))

    return top_ids[-num_articles:]

def okapi_bm25_nosubset(query, start_index, num_articles, bm25, bm25_features, linrel, max_corpus=10000) :
    #bm25 = load_sparse_bm25()
    #bm25_features = load_features_bm25()

    query_terms = get_query_terms(query, bm25_features)

    tmp = {}
    for qt in query_terms :
        findex = bm25_features[qt]

        for aindex in numpy.nonzero(bm25[:, findex])[0] :
            akey = aindex.item()
            if akey not in tmp :
                tmp[akey] = 0.0

            tmp[akey] += bm25[aindex,findex]

    ranking = sorted(tmp.items(), key=lambda x : x[1], reverse=True)
    print "ranked %d documents" % len(ranking)

    top_ids = []
    for i in ranking :
        top_ids.append(i[0])

        if len(top_ids) == (start_index + num_articles) :
            break

    return top_ids[-num_articles:]

