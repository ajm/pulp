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

from django.conf.urls import patterns, url, include
from rest_framework import routers
from explore import views


from django.contrib import admin
admin.autodiscover()

#router = routers.DefaultRouter()
#router.register(r'users', views.UserViewSet)
#router.register(r'groups', views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns('',
    #url(r'^admin/', include(admin.site.urls)),
    #url(r'^', include(router.urls)),
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # e.g. /article/1/
    url(r'^article/(?P<pk>\d+)/$', views.GetArticle.as_view()),
    #url(r'^logout', views.logout_view),
    url(r'^query', views.textual_query),
    url(r'^next', views.selection_query),
    url(r'^state', views.system_state),
    url(r'^end', views.end_search),
    url(r'^search', views.index),
    url(r'^visualization', views.visualization),
    url(r'^setup', views.setup_experiment),
    url(r'^ratings', views.experiment_ratings)
)

