#from django.contrib.auth.models import User, Group
from rest_framework import serializers
from explore.models import Article

#class UserSerializer(serializers.HyperlinkedModelSerializer):
#    class Meta:
#        model = User
#        fields = ('url', 'username', 'email', 'groups')

class ArticleSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Article
        fields = ('id', 'title','author','abstract','venue','url')

