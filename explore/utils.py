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

import numpy
import scipy
import os
import string
import json

from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

from explore.models import Article

from django.conf import settings 


#
# saving and load this big matrix of all articles
#
def save_sparse(m, prefix) :
    numpy.save(prefix + '.data.npy',     m.data)
    numpy.save(prefix + '.indices.npy',  m.indices)
    numpy.save(prefix + '.indptr.npy',   m.indptr)
    numpy.save(prefix + '.shape.npy',    m.shape)

def load_sparse(prefix) :
    return scipy.sparse.csr_matrix((numpy.load(prefix + '.data.npy'), 
                                    numpy.load(prefix + '.indices.npy'), 
                                    numpy.load(prefix + '.indptr.npy')), 
                                    shape=tuple(numpy.load(prefix + '.shape.npy')))

articles_prefix =   os.path.join(settings.BASE_DIR, 'articles')
tfidf_prefix =      os.path.join(settings.BASE_DIR, 'tfidf')
features_file =     os.path.join(settings.BASE_DIR, 'features.dat')

def save_sparse_articles(m) :
    save_sparse(m, articles_prefix)

def load_sparse_articles() :
    return load_sparse(articles_prefix)

def save_sparse_tfidf(m) :
    save_sparse(m, tfidf_prefix)

def load_sparse_tfidf() :
    return load_sparse(tfidf_prefix)

def save_features(m) :
    with open(features_file, 'w') as f :
        json.dump(m, f)
    #    print >> f, ','.join(m)

def load_features() :
    with open(features_file) as f :
        return json.load(f)
    #    return f.read().strip().split(',')

#
# corpus related functions
#
def build_corpus() :
    #return [ a.title + ' ' + a.abstract for a in Article.objects.all() ]

    stemmer = SnowballStemmer('english')

    corpus = []

    bad_chars = set(string.digits + string.punctuation)

    for a in Article.objects.all() :
        s = a.title + ' ' + a.abstract
        s = s.lower().strip()
        s = ''.join([ i if i not in bad_chars else ' ' for i in s ])

        corpus.append(' '.join([ stemmer.stem(word) for word in s.split() ]))

    return corpus

def get_stop_words() :
    try :
        return stopwords.words('english')

    except LookupError :
        from nltk import download as nltk_download
        import warnings

        # christ this is verbose...
        with warnings.catch_warnings() :
            warnings.simplefilter("ignore")
            nltk_download('stopwords')
            
    return stopwords.words('english')

#
# article helpers
#
def get_unseen_articles(e) :
    all_shown_articles = []
    
    for i in ExperimentIteration.objects.filter(experiment=e) :
        all_shown_articles += [ j.id for j in i.shown_documents.all() ]
    
    return Article.objects.exclude(pk__in=all_shown_articles)

