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
        v = TfidfVectorizer(min_df=1, stop_words=get_stop_words())

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
        self.stdout.write(progress_string + "0.00%%", ending='')
        self.stdout.flush()

        for aindex,article in enumerate(articles) :
            tfidfs = []
            
            for findex,feature in enumerate(features) :
                value = m[aindex,findex]
                if value :
                    tfidf = ArticleTFIDF()
                    tfidf.article = article
                    tfidf.term    = feature
                    tfidf.value   = value
                    
                    tfidfs.append(tfidf)
            
            ArticleTFIDF.objects.bulk_create(tfidfs)
            self.stdout.write("\r" + progress_string + ("%.2f%%" % ((aindex+1) / progress_divisor)), ending='')
            self.stdout.flush()

        self.stdout.write("\r" + progress_string + "done!  \n")

