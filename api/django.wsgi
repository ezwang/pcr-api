import os,sys

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

sys.path.append(PROJECT_PATH)

from django.conf import settings

#Uncomment these two lines to use virtualenv
#activate_this = os.path.join(BASE_DIR, "ENV/bin/activate_this.py")
#execfile(activate_this, dict(__file__=activate_this))

sys.path.append(settings.BASE_DIR)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

