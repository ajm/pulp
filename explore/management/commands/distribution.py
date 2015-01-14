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
from explore.models import Article
from explore.utils import *

from sys import stdout, stderr

class Command(BaseCommand) :
    args = 'no arguments'
    help = 'prints out the word count distribution'

    def handle(self, *args, **options) :
        v = CountVectorizer(min_df=1, stop_words=None) #get_stop_words())
        m = v.fit_transform(build_corpus())
 
        #print >> sys.stderr, "writing file..."

        features = v.get_feature_names()
        stopwords = set(get_stop_words())
        num_articles = float(len(Article.objects.all()))

        for findex,feature in enumerate(features) :
            fout = stderr if feature in stopwords else stdout

            print >> fout, feature, m[:,findex].sum(), len(m[:,findex].nonzero()[0]) / num_articles

