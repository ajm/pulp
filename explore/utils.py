import numpy
import scipy
import os

from nltk.corpus import stopwords
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

articles_prefix = os.path.join(settings.BASE_DIR, 'articles')

def save_sparse_articles(m) :
    save_sparse(m, articles_prefix)

def load_sparse_articles() :
    return load_sparse(articles_prefix)

#
# corpus related functions
#
def build_corpus() :
    return [ a.title + ' ' + a.abstract for a in Article.objects.all() ]

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

