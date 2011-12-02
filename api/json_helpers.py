import sandbox_config
import datetime
import json
from django.http import HttpResponse

def JSON(x, valid=True, httpstatus=200):
  jsonstr = json.dumps(
    {"result": x, "valid": valid, "version": "0.3", "nyan": "cats",
     "retrieved": str(datetime.datetime.now())},
    sort_keys=True,
    indent=3)
  if sandbox_config.USE_DJANGO_DEBUG_TOOLBAR:
    jsonstr = "<html><body>%s</body></html>" % jsonstr
  return HttpResponse(status=httpstatus, content=jsonstr)

