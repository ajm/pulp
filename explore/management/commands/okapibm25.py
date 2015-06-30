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

from django.core.management.base import BaseCommand, CommandError
from sklearn.feature_extraction.text import CountVectorizer
from scipy.sparse import csr_matrix
from explore.models import Article
from explore.utils import *

import numpy as np

class Command(BaseCommand) :
    args = 'no arguments'
    help = '(re)builds the okapibm25 matrix'

    def handle(self, *args, **options) :
        articles = Article.objects.all()
        N = len(articles)

        v = CountVectorizer(min_df=10, max_df=0.5, stop_words=get_stop_words())

        self.stdout.write("Running TFIDF on %d articles... " % N, ending='\n')
        self.stdout.flush()

        tf = v.fit_transform(build_corpus())

        self.stdout.write("Running OKAPI BM25 on %d articles... " % N, ending='\n')
        self.stdout.flush()

        # free parameters
        k1 = 1.2 # from [1.2, 2.0]
        b = 0.75

        D = tf.sum(axis=1)

        # TF
        tf_num = (tf * (k1 + 1))

        # make sure everything is CSR
        tf_tmp = csr_matrix(k1 * (1 - b + b * (D / D.mean())))

        # mask to ensure matrix is sparse
        tf_mask = tf.copy()
        tf_mask[tf_mask != 0] = 1
        tf_den = tf + tf_mask.multiply(tf_tmp)
        
        # avoid NaN in element-wise divide
        tf_num.sort_indices()
        tf_den.sort_indices()
        tf_num.data = np.divide(tf_num.data, tf_den.data)

        # IDF
        n = np.bincount(tf.nonzero()[1])
        idf_term = np.log((N - n + 0.5) / (n + 0.5))

        # bm25 should still be sparse
        bm25 = tf_num.multiply(csr_matrix(idf_term))
        print type(bm25), bm25.shape

        self.stdout.write("done\n")

        self.stdout.write("writing to disk...\n")
        features = v.get_feature_names()

        save_sparse_bm25(bm25)
        save_features_bm25(dict([ (y,x) for x,y in enumerate(features) ]))
        
        self.stdout.write("done\n")
