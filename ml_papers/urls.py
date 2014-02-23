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
    url(r'^end', views.end_search),
)

