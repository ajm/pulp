from django.core.management.base import BaseCommand, CommandError
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
from explore.models import Article
from explore.utils import *
import numpy as np

class Command(BaseCommand) :
    args = 'no arguments'
    help = 'write LinRel related files'

    def handle(self, *args, **options) :
        v = CountVectorizer(min_df=1, stop_words=get_stop_words(), dtype=np.float64)

        self.stdout.write("Building matrix from %d articles... " % Article.objects.count(), ending='')
        self.stdout.flush()

        m = v.fit_transform(build_corpus())
        self.stdout.write("done!\n")

        self.stdout.write("Normalising... ", ending='')
        self.stdout.flush()

        if not scipy.sparse.isspmatrix_csr(m) :
            m = m.tocsr()

        normalize(m, norm='l2', copy=False)
        self.stdout.write("done!\n")

        self.stdout.write("Writing LinRel file...", ending='')
        self.stdout.flush()

        save_sparse_articles(m)

        self.stdout.write("Writing out %d keyword features..." % len(v.get_feature_names()), ending='')
        self.stdout.flush()
        with open('keywords.txt', 'w') as f :
            for index,feature in enumerate(v.get_feature_names()) :
                print >> f, index, ''.join([i for i in feature if ord(i) < 128])

        self.stdout.write("done!\n")

