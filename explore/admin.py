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
