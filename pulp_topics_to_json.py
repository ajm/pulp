from sys import argv, stderr, exit

import xml.sax
import json


articles = []

class Article(object) :
    def __init__(self) :
        self.title = None
        self.author = None
        self.abstract = None
        self.venue = None
        self.url = None
        self.identity = None
        self.topics = None

class ArticleParser(xml.sax.ContentHandler) :
    def __init__(self) :
        self.identity = None
        self.content = None
        self.article = None
        self.count = 0

    def cleaned(self) :
        return self.content.replace('\n', ' ').strip()

    def startElement(self, name, attrs) :
        self.content = ""

        if name == 'article' :
            self.article = Article()

    def characters(self, c) :
        self.content += c

    def endElement(self, name) :
        global articles

        if name == 'article' :
            if self.article :
                articles.append(self.article)
                self.article = None
                self.count += 1

                if (self.count % 1000) == 0 :
                    print >> stderr, "read in %d articles" % self.count

        elif name == 'title'    : self.article.title = self.cleaned()
        elif name == 'author'   : self.article.author = self.cleaned()
        elif name == 'abstract' : self.article.abstract = self.cleaned()
        elif name == 'venue'    : self.article.venue = self.cleaned()
        elif name == 'url'      : self.article.url = self.cleaned()
        elif name == 'id'       : self.identity = int(self.cleaned())
        elif name == 'categories' : self.article.topics = self.cleaned().replace(' ', '').split(',')
        else : pass


def main() :
    global articles

    xmlfile = 'arxiv_cs_categories.xml'
    topic_json_fname = 'arxiv_topics.json'
    num_articles = 78129

    parser = xml.sax.make_parser()
    parser.setContentHandler(ArticleParser())
    parser.parse(open(xmlfile))

    print >> stderr, "read %d articles" % len(articles)

    with open(topic_json_fname, 'w') as f :
        json.dump(dict([ (i, a.topics[0]) for i,a in enumerate(articles[:num_articles]) ]), f)

    print >> stderr, "done"

    return 0

if __name__ == '__main__' :
    try :
        exit(main())
    except KeyboardInterrupt :
        print >> stderr, "Killed by User...\n"
        exit(1)

