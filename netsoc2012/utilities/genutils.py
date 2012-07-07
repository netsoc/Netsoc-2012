from django.shortcuts import redirect
from django.contrib.sites.models import Site
def site_url(view):
		return Site.objects.get_current().domain


def AJAX_View(view):
		def decorated(*args, **kwargs):

				if not args[0].is_ajax():
						return redirect('/')
				else:
						return view(*args, **kwargs)
		return decorated
