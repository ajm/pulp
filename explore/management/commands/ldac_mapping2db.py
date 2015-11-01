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

import xml.sax 
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from explore.models import Topic, Article, TopicWeight
from sys import stderr, exit

class Command(BaseCommand) :
    args = '<gamma file>'
    help = 'loads document to topic mapping file into DB'

    def handle(self, *args, **options) :

        NUM_TOPICS_TO_STORE = 5

        topic_count = Topic.objects.count()
        if topic_count == 0 :
            print >> stderr, "Error, topic table must be built first!"
            exit(1)

        article_count = Article.objects.count()
        if article_count == 0 :
            print >> stderr, "Error, article table must be built first!"
            exit(1)

        if TopicWeight.objects.count() != 0 :
            print >> stderr, "Deleting %d TopicWeight objects" % TopicWeight.objects.count()
            TopicWeight.objects.all().delete()
            print >> stderr, "done!"

        topics = Topic.objects.all()
        articles = Article.objects.all()

        expected_number_of_fields = topic_count

        print >> stderr, "reading %s ..." % args[0]

        # arxiv_cs_example/doc-topics.txt
        with open(args[0]) as f :
            linenum = -1

            with transaction.atomic() :
                for line in f :
                    linenum += 1

                    line = line.strip()
                    if not line or line.startswith('#') :
                        continue
                
                    data = line.split()

                    if len(data) != expected_number_of_fields :
                        print >> stderr, "Error, line %d: expected %d fields, read %d fields" % \
                            (linenum, expected_number_of_fields, len(data))
                        continue

                    a = articles[linenum]

                    for topic,weight in sorted(enumerate([ float(d) for d in data ]), reverse=True, key=lambda x : x[1])[:NUM_TOPICS_TO_STORE] :
                
                        tw = TopicWeight()

                        tw.article  = a
                        tw.topic    = topics[topic]
                        tw.weight   = weight

                        tw.save()

                    if (linenum % 1000) == 0 :
                        self.stderr.write("saved topic weights for %s articles" % linenum)


        expected_weights = NUM_TOPICS_TO_STORE * article_count
        print >> stderr, "Wrote %d topic weight objects. I was expecting %d (%d articles x %d topics)" \
                % (TopicWeight.objects.count(), expected_weights, article_count, NUM_TOPICS_TO_STORE)

