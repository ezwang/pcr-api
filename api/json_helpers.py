"""
This module contains helper functions for responding with JSON data.
"""
import datetime
import json

from django.http import HttpResponse, JsonResponse

from django.conf import settings


def JSON(result, valid=True, httpstatus=200):
    """
    Return a JsonResponse whose content is filled with `result` and standard meta-data.
    """

    content = {
        "result": result,
        "valid": valid,
        "version": "0.3",
        "retrieved": str(datetime.datetime.now())
    }

    # return HTML response if debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        content = json.dumps(content, sort_keys=True, indent=4)
        content = "<html><body>{}</body></html>".format(content)
        return HttpResponse(status=httpstatus, content=content)

    return JsonResponse(content, status=httpstatus, json_dumps_params={'indent': 4, 'sort_keys': True})
