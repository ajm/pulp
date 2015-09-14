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
from explore.models import Topic
from sys import stderr

class Command(BaseCommand) :
    args = '<topic file>'
    help = 'loads topics from txt file into DB'

    def handle(self, *args, **options) :

        # arxiv_cs_example/topic_top_keywords
        with open(args[0]) as f :
            linenum = 0

            for line in f :
                linenum += 1

                line = line.strip()
                if not line :
                    continue

                try :
                    name,keywords = line.split()

                except ValueError :
                    print >> stderr, "Error: too many tokens, line %d" % linenum
                    continue

                keywords = keywords.split(',')

                with transaction.atomic() :
                    t = Topic()
                    t.label = ','.join(keywords[:3])
                    t.save()

                    #for k in keywords :
                    #    kw = TopicKeyword()
                    #    kw.topic = t
                    #    kw.keyword = k
                    #    kw.save()

                #print >> stderr, "saved topic %s" % name


        print >> stderr, "added %d topics" % (Topic.objects.count())

