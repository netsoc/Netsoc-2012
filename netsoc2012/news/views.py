from django.http import HttpResponse, HttpResponseRedirect as redirect, Http404
from utilities.genutils import AJAX_View
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#@AJAX_View
def view_news_article(request, **kwargs):
		context = RequestContext(request)
		pages = None
		article = None
		try:
				article_id = kwargs['article_id']
				article = Article.objects.get(id=article_id)
		
		except KeyError:
				article_id=None
				all_articles = Article.objects.all()
		except Article.DoesNotExist:
				raise Http404

		try:
				page_id = kwargs['page_id']
		except KeyError:
				page_id=None
		
		if page_id is not None:
				pages = Paginator(all_articles, 5)
				try:
						article = pages.page(page_id).object_list
				except EmptyPage:
						return HttpResponse("", status=200)
				except PageNotAnInteger:
						return HttpResponse("", status=400)

		if page_id is None and article_id is None:
				return redirect('/news/1')
		context['article'] = article
		context['user']  = request.user
		if len(article) is 1:
				return render_to_response('news/view-news-item.html', context_instance=context)
		else:
				return render_to_response('news/news-query-results.html', context_instance=context)
