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
import numpy as np

class Command(BaseCommand) :
    args = '<topic mapping file>'
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


        expected_number_of_fields = (topic_count * 2) + 2

        print >> stderr, "reading %s ..." % args[0]

        topics = []
        weights = []

        # arxiv_cs_example/doc-topics.txt
        with open(args[0]) as f :
            linenum = 0

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

                topics.append([    int(data[i]) for i in range(2, (NUM_TOPICS_TO_STORE * 2) + 1, 2) ])
                weights.append([ float(data[i]) for i in range(3, (NUM_TOPICS_TO_STORE * 2) + 2, 2) ])


                if (linenum % 1000) == 0 :
                    self.stderr.write("read topic weights for %d articles" % linenum)


        topics = np.array(topics)
        weights = np.array(weights)

        self.stdout.write("Writing topics file...", ending='')
        self.stdout.flush()

        save_sparse_topics(topics)
        save_sparse_weights(weights)

        self.stdout.write("done!\n")

