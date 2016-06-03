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

from django.db import models
import datetime


class Topic(models.Model) :
    label     = models.CharField(max_length=512)

#class TopicKeyword(models.Model) :
#    topic    = models.ForeignKey(Topic)
#    keyword  = models.CharField(max_length=128)

class Article(models.Model) :
    title    = models.CharField(max_length=200)
    author   = models.CharField(max_length=200)
    abstract = models.CharField(max_length=4000)
    venue    = models.CharField(max_length=200)
    url      = models.URLField()
    date     = models.DateField()
    arxivid  = models.CharField(max_length=9) # e.g. 0704.0002

    def __unicode__(self) :
        return u'%s %s' % (self.__class__.__name__, self.title)

class ArticleTFIDF(models.Model) :
    article = models.ForeignKey(Article)
    term    = models.CharField(max_length=32)
    value   = models.FloatField(blank=False)

    def __unicode__(self) :
        return u'%s %s %.3f' % (self.__class__.__name__, self.term, self.value)

class TopicWeight(models.Model) :
    topic    = models.ForeignKey(Topic)
    article  = models.ForeignKey(Article)
    weight   = models.FloatField(default=0.0)

class TopicWeights(models.Model) :
    #article  = models.ForeignKey(Article)
    article  = models.PositiveIntegerField() # id of article object

    topic1   = models.CharField(max_length=512)
    weight1  = models.FloatField(default=0.0)
    topic2   = models.CharField(max_length=512)
    weight2  = models.FloatField(default=0.0)
    topic3   = models.CharField(max_length=512)
    weight3  = models.FloatField(default=0.0)
    topic4   = models.CharField(max_length=512)
    weight4  = models.FloatField(default=0.0)
    topic5   = models.CharField(max_length=512)
    weight5  = models.FloatField(default=0.0)

class User(models.Model) :
    username = models.CharField(max_length=100, blank=False)

    def __unicode__(self) :
        return u'%s %s' % (self.__class__.__name__, self.username) 

class Experiment(models.Model) :
    RUNNING = 'R'
    COMPLETE = 'C'
    ERROR = 'E'
    EXPERIMENT_STATES = (
                (RUNNING,   'Running'),
                (COMPLETE,  'Complete'),
                (ERROR,     'Error'),
            )

    LOOKUP = 'L'
    EXPLORATORY = 'E'
    EXPERIMENT_TYPES = (
                (LOOKUP,        'Lookup'),
                (EXPLORATORY,   'Exploratory')
            )

    user                 = models.ForeignKey(User, blank=False)
    date                 = models.DateTimeField(auto_now=True)
    base_exploration_rate = models.FloatField(blank=False) # i.e. exploration_rate set in setup
    exploration_rate     = models.FloatField(default=0.0) # i.e. exploration_rate used in linrel
    classifier           = models.BooleanField(default=False)
    task_type            = models.CharField(max_length=1, choices=EXPERIMENT_TYPES, blank=False)
    study_type           = models.PositiveIntegerField()
    #sessionid            = models.CharField(max_length=32)

    number_of_documents  = models.PositiveIntegerField()
    number_of_iterations = models.PositiveIntegerField(default=0)
    state                = models.CharField(max_length=1,
                                            choices=EXPERIMENT_STATES,
                                            default=RUNNING)
    query                = models.CharField(max_length=1000)
    
    from_date            = models.DateField(default=datetime.date(1900,1,1))
    to_date              = models.DateField(default=datetime.date(2100,12,31))

    def __unicode__(self) :
        return u'%s %s %s (%s)' % (self.__class__.__name__, self.id, self.user.username, self.state)

class ExperimentIteration(models.Model) :
    experiment         = models.ForeignKey(Experiment)
    iteration          = models.PositiveIntegerField()
    date               = models.DateTimeField(auto_now=True)
    #shown_documents    = models.ManyToManyField(Article, related_name="shown")
    #selected_documents = models.ManyToManyField(Article, related_name="selected")

    def __unicode__(self) :
        return u'%s %s %s' % (self.__class__.__name__, self.experiment.id, self.iteration)

class ArticleFeedback(models.Model) :
    article     = models.ForeignKey(Article)             # to associate with the article
    iteration   = models.ForeignKey(ExperimentIteration) # to search for articles to apply feedback to
    experiment  = models.ForeignKey(Experiment)          # to help perform linrel
    selected    = models.NullBooleanField(default=None)
    clicked     = models.NullBooleanField(default=None)
    seen        = models.NullBooleanField(default=None)
    reading_start   = models.FloatField(default=0)
    reading_end     = models.FloatField(default=0)

    def __unicode__(self) :
        return u'%s %s %s' % (self.__class__.__name__, self.article.id, self.selected)


