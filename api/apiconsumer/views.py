from django.forms import ModelForm
from models import APIConsumer

class TokenForm(ModelForm):
  class Meta:
    model = APIConsumer
    exclude = ('token',)


def token_form(request):
  if request.method == 'POST':
    form = TokenForm(request.POST)
    if form.is_valid():
      form.save()
      # TODO
  else:
    form = TokenForm()

  return render(request, 'token-form.html', {'form': form})
