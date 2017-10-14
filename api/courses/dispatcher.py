from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings


API_ROOT = settings.DISPLAY_NAME
ACC_HEADERS = {'Access-Control-Allow-Origin': '*',
               'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
               'Access-Control-Max-Age': 1000,
               'Access-Control-Allow-Headers': '*'}

# allows cross-domain AJAX calls
# https://gist.github.com/1308865
def cross_domain_ajax(func):
  """ Sets Access Control request headers. """
  def wrap(request, *args, **kwargs):
    # Firefox sends 'OPTIONS' request for cross-domain javascript call.
    if request.method != "OPTIONS":
      response = func(request, *args, **kwargs)
    else:
      response = HttpResponse()
    for k, v in ACC_HEADERS.iteritems():
      response[k] = v
    return response
  return wrap

def redirect(path, request, extras=[]):
  query = '?' + request.GET.urlencode() if request.GET else ''
  fullpath = "%s/%s/%s%s" % (API_ROOT, path, '/'.join(extras), query)
  return HttpResponseRedirect(fullpath)

def dead_end(fn):
  def wrapped(request, path, variables):
    if path:
      return dispatch_404(message="Past dead end!")(request, path, variables)
    else:
      return fn(request, path, variables)
  return wrapped


# FNAR 337 Advanced Orange (Jaime Mundo)
# Explore the majesty of the color Orange in its natural habitat,
# and ridicule other, uglier colors, such as Chartreuse (eww).

# MGMT 099 The Art of Delegating (Alexey Komissarouky)
# The Kemisserouh delegates teaching duties to you. Independent study.

class API404(Exception):
  def __init__(self, message=None, perhaps=None):
    self.message = message
    self.perhaps = perhaps
