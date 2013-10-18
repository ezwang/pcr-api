import datetime
import json

from django.http import HttpResponse

import settings


def JSON(x, valid=True, httpstatus=200):
  jsonstr = json.dumps(
    {"result": x, "valid": valid, "version": "0.3",
     "retrieved": str(datetime.datetime.now())},
    sort_keys=True,
    indent=3)
  if 'debug_toolbar' in settings.INSTALLED_APPS:
    jsonstr = "<html><body>%s</body></html>" % jsonstr
  return HttpResponse(status=httpstatus, content=jsonstr)

