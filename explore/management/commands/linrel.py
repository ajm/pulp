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
from sklearn.preprocessing import normalize
from explore.models import Article
from explore.utils import *
import numpy as np

class Command(BaseCommand) :
    args = 'no arguments'
    help = 'write LinRel related files'

    def handle(self, *args, **options) :
        v = CountVectorizer(min_df=2, stop_words=get_stop_words(), dtype=np.float64)

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

