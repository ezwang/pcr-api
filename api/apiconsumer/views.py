import re
from models import APIConsumer
from django.http import HttpResponse
from django.template import Context, loader
from django.views.decorators.cache import never_cache
from json_helpers import JSON
from django.shortcuts import render_to_response
from django.template import RequestContext
from hashlib import sha1
from django.core.mail import EmailMultiAlternatives



@never_cache
def issue(request):
  #consumer = APIConsumer.objects.get(name="David Xu") 

  if request.method == 'POST':
    email = str(request.POST['email'])
    # What emails should I check?
    # the regex is off.
    if not re.match('[a-zA-Z0-9]+@[a-zA-Z0-9]+\.upenn\.edu\S*', email):
        email = None
    else:
        key = secret_key(email)
        subject, from_email, to = 'hello', 'from@example.com', email 
        text_content = 'This is an important message.'
        html_content = render_to_string('apiconsumer/confirmation_email.html', {}) 
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()



    return render_to_response('apiconsumer/access_requested.html', 
        { 'email': email, 'key': key })
  elif request.method == 'GET':
    return render_to_response('apiconsumer/get_access.html', 
        context_instance=RequestContext(request))
  else:
    return HttpResponseNotAllowed(['GET'])



def secret_key(email):
  """Unique key that can be shared so that anyone can view the event."""
  """To use the key append ?key=<key>"""
  if email:
    return sha1(email).hexdigest()
  else:
    return None
