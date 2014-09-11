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

from django.contrib import admin
from explore.models import Article, ArticleTFIDF, Experiment, ExperimentIteration, ArticleFeedback

class ArticleAdmin(admin.ModelAdmin) :
    fieldsets = [
        ('Title',       {'fields': ['title']}),
        ('Author',      {'fields': ['author']}),
        ('Abstract',    {'fields': ['abstract']}),
        ('Venue',       {'fields': ['venue']}),
        ('URL',         {'fields': ['url']})
    ]

admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleTFIDF)
admin.site.register(Experiment)
admin.site.register(ExperimentIteration)
admin.site.register(ArticleFeedback)
