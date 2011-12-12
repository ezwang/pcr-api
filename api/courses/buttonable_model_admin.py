# taken from http://djangosnippets.org/snippets/1016/
from django.contrib import admin

class ButtonableModelAdmin(admin.ModelAdmin):
  """
  A subclass of this admin will let you add buttons (like history) in the
  change view of an entry.

  ex.
  class FooAdmin(ButtonableModelAdmin):
    ...

    def bar(self, obj):
      obj.bar()
    bar.short_description='Example button'

    buttons = [ bar ]

  you can then put the following in your admin/change_form.html template:

    {% block object-tools %}
    {% if change %}{% if not is_popup %}
    <ul class="object-tools">
    {% for button in buttons %}
      <li><a href="{{ button.func_name }}/">{{ button.short_description }}</a></li>
    {% endfor %}
    <li><a href="history/" class="historylink">History</a></li>
    {% if has_absolute_url %}<li><a href="../../../r/{{ content_type_id }}/{{ object_id }}/" class="viewsitelink">View on site</a></li>{% endif%}
    </ul>
    {% endif %}{% endif %}
    {% endblock %}

  """
  buttons=[]

  def change_view(self, request, object_id, extra_context={}):
    extra_context['buttons']=self.buttons
    return super(ButtonableModelAdmin, self).change_view(request, object_id, extra_context)

  def __call__(self, request, url):
    if url is not None:
      import re
      res=re.match('(.*/)?(?P<id>\d+)/(?P<command>.*)', url)
      if res:
        if res.group('command') in [b.func_name for b in self.buttons]:
          obj = self.model._default_manager.get(pk=res.group('id'))
          getattr(self, res.group('command'))(obj)
          return HttpResponseRedirect(request.META['HTTP_REFERER'])

    return super(ButtonableModelAdmin, self).__call__(request, url)
