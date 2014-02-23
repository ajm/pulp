import xml.sax 
from django.core.management.base import BaseCommand, CommandError
from explore.models import Article

class ArticleParser(xml.sax.ContentHandler) :
    def __init__(self) :
        self.identity = None
        self.content = None
        self.article = None

    def cleaned(self) :
        return self.content.replace('\n', ' ').strip()
    #xml.sax.saxutils.escape(self.content.replace('\n', ' ').strip())

    def startElement(self, name, attrs) :
        self.content = ""

        if name == 'Article' :
            self.article = Article()

    def characters(self, c) :
        self.content += c

    def endElement(self, name) :
        if name == 'Article' : 
            if self.article :
                if self.identity == 420 :
                    print self.article.author

                self.article.save()
                self.article = None
        
        elif name == 'title'    : self.article.title = self.cleaned()
        elif name == 'author'   : self.article.author = self.cleaned()
        elif name == 'abstract' : self.article.abstract = self.cleaned()
        elif name == 'venue'    : self.article.venue = self.cleaned()
        elif name == 'url'      : self.article.url = self.cleaned()
        elif name == 'id'       : self.identity = int(self.cleaned())
        else : pass

        #print self.content

class Command(BaseCommand) :
    args = '<XML file> <XML file> ...'
    help = 'loads the articles from XML file into DB'

    def handle(self, *args, **options) :
        parser = xml.sax.make_parser()
        parser.setContentHandler(ArticleParser())

        initial_count = Article.objects.count()

        for xmlfile in args :
            pre_count = Article.objects.count()

            try :
                parser.parse(open(xmlfile))

            except IOError, ioe :
                raise CommandError(str(ioe))
            except xml.sax.SAXParseException, spe :
                raise CommandError(str(spe))
        
            post_count = Article.objects.count()
            self.stdout.write("added %d articles from %s" % (post_count - pre_count, xmlfile))

        self.stdout.write("\nDone! added %d articles total from %d file%s" % \
                (Article.objects.count() - initial_count, len(args), "" if len(args) == 1 else "s"))

