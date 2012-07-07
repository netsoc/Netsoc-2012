from django.conf.urls.defaults import *
from views import *
# Uncomment the next two lines to enable the admin:

urlpatterns = patterns('',
    # Example:

    # Uncomment the admin/doc line below to enable admin documentation:
	(r'^(?P<page_id>[0-9]+)$', view_news_article),
	(r'^(?P<article_id>[0-9]+)/$', view_news_article),
	(r'^$', view_news_article),
)
