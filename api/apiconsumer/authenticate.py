from django.http import HttpResponse
from apiconsumer.models import APIConsumer

class Authenticate(object):
  """Looks up the token (passed as a GET parameter) in the token database.
  Ensures that it is a valid token, and passes the APIConsumer (i.e. user) to
  the view via request.consumer so the view knows what access level the consumer
  has."""

  def process_request(self, request):

    # We use status=404 for errors. Is this accurate? There are HTTP status
    # codes for authentication failure, but I think those are reserved
    # for errors in HTTP-standard authentication.

    old_path = request.path_info
    
    if old_path[:7] == "/admin/":   
      return None
    
    try:
      token = request.GET['token']
    except:
      return HttpResponse("No token provided.", status=404)
    
    try:
      consumer = APIConsumer.objects.get(token=token)
    except APIConsumer.DoesNotExist:
      consumer = None
      
    if consumer is not None and consumer.valid:
      # The found consumer is added to the request object, in request.consumer.
      request.consumer = consumer
      return None # continue rendering
    else:
      return HttpResponse("Invalid token.", status=404)
