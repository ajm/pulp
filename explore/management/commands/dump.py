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
from explore.models import Experiment, ExperimentIteration, ArticleFeedback
from explore.utils import *

from sys import stderr


class Command(BaseCommand) :
    args = 'no arguments'
    help = 'dump database to stdout'

    def handle(self, *args, **options) :
        delim = ','

        print >> stderr, delim.join([
                    "experiment_id",
                    "participant_id",
                    "experiment_state",
                    "task_type",
                    "study_type",
                    "base_erate",
                    "used_erate",
                    "num_docs",
                    "num_iter",
                    "timestamps"])

        print delim.join([
                    "experiment_id",
                    "iteration",
                    "article_id",
                    "selected",
                    "clicked",
                    "seen",
                    "start",
                    "end"
                    ])
        for e in Experiment.objects.all() :
            iterations = ExperimentIteration.objects.filter(experiment=e)
            timestamps = ":".join([str(e.date)] + [ str(i.date) for i in iterations ])

            print >> stderr, delim.join([ str(x) for x in [
                                e.id,
                                e.user.username,
                                e.state,
                                e.task_type,
                                e.study_type,
                                e.base_exploration_rate,
                                e.exploration_rate,
                                e.number_of_documents,
                                e.number_of_iterations,
                                timestamps
                                ]])

            for i in ExperimentIteration.objects.filter(experiment=e) :
                for a in ArticleFeedback.objects.filter(iteration=i) :
                    if a.selected == None and a.clicked == None :
                        continue
                    
                    print delim.join([ str(x) for x in [ 
                                       e.id, 
                                       i.iteration, 
                                       a.article.id, 
                                       a.selected, 
                                       a.clicked, 
                                       a.seen, 
                                       a.reading_start, 
                                       a.reading_end 
                                       ]])

