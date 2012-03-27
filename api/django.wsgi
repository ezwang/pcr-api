import os,sys

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

sys.path.append(PROJECT_PATH)

from sandbox_config import *

#Uncomment these two lines to use virtualenv
#activate_this = os.path.join(COURSESAPI_APP_ROOT, "ENV/bin/activate_this.py")
#execfile(activate_this, dict(__file__=activate_this))

sys.path.append(DEV_ROOT)
sys.path.append(COURSESAPI_APP_ROOT)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

