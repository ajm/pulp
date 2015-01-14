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
from sklearn.feature_extraction.text import TfidfVectorizer
from explore.models import Article, ArticleTFIDF
from explore.utils import *

class Command(BaseCommand) :
    args = 'no arguments'
    help = '(re)builds the ArticleTFIDF table'

    def handle(self, *args, **options) :
        # delete previous
        tfidfs = ArticleTFIDF.objects.all()
        if len(tfidfs) :
            self.stdout.write("Deleting ArticleTFIDF table... ", ending='')
            self.stdout.flush()

            tfidfs.delete()

            self.stdout.write("deleted!\n")

        articles = Article.objects.all()

        # run tfidf
        v = TfidfVectorizer(min_df=2, stop_words=get_stop_words())

        self.stdout.write("Running TFIDF on %d articles... " % \
                len(articles), ending='')
        self.stdout.flush()

        m = v.fit_transform(build_corpus())

        self.stdout.write("done!\n")

        # build ArticleTFIDF table
        features = v.get_feature_names()
        progress_divisor = float(len(articles)) / 100.0
        progress_string = "Writing ArticleTFIDF table (%d documents, %d features)... " % \
            (len(articles), len(features))
        
        
        print progress_string
        

        save_sparse_tfidf(m)
        save_features_tfidf(dict([ (y,x) for x,y in enumerate(features) ]))
        
        self.stdout.write("done\n")
        return
        

#        self.stdout.write(progress_string + "0.00%%", ending='')
#        self.stdout.flush()
#
#        #tfidfs = []
#        for aindex,article in enumerate(articles) :
#            tfidfs = []
#            
#            for findex,feature in enumerate(features) :
#                value = m[aindex,findex]
#                if value :
#                    tfidf = ArticleTFIDF()
#                    tfidf.article = article
#                    tfidf.term    = feature
#                    tfidf.value   = value
#                    
#                    tfidfs.append(tfidf)
#            
#            ArticleTFIDF.objects.bulk_create(tfidfs)
#            self.stdout.write("\r" + progress_string + ("%.2f%%" % ((aindex+1) / progress_divisor)), ending='')
#            self.stdout.flush()
#
#        #self.stdout.write("\nthis might take a while...\n")
#        #self.stdout.flush()
#        #ArticleTFIDF.objects.bulk_create(tfidfs)
#
#        self.stdout.write("\r" + progress_string + "done!  \n")

