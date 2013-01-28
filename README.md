# Setup

- Clone repo.
- Copy `api/sandbox_config.py_default` to `api/sandbox_config.py`
- Edit `DISPLAY_NAME`, `DEV_ROOT`, and `DATABASE_*` appropriately.
  - **Note:** Ensure DISPLAY_NAME begins with a forward slash. (This ensure it is never used relatively.)
  - **Note:** If you cloned the project into anything but `Penn-Course-Review-api`, you will need to change COURSESAPI_APP_ROOT to match.
- Update your apache config file (in `/etc/apache2/sites-available/`:
  - `WSGIScriptAlias /pcrapi /MYPROJECTPATH/api/django.wsgi`

### Local Setup (with mysql)
- Run steps 1-3 from above.
  - Don't run collectstatic
- Install MySQL. Try running it. If you encounter 'No module named MySQLdb', run sudo pip install mysql-python.
 In mysql, create the database you specified in your sandbox_config, and create a user with permissions
  - google "mysql create user with permissions" if you need help. 
  - Update your sandbox config if information has changed.
- python manage.py syncdb
- python manage.py runserver
- Create a token:
  - python manage.py shell
  - from apiconsumer.models import APIConsumer
  - APIConsumer.objects.all() <- this should return []
  - token = APIConsumer(name="public", email="", description="", token="public", permission_level=2)
  - token.save()

#### MAC MySQL Problems:
- brew remove mysql
- brew cleanup
- brew install mysql
- mysql_install_db --verbose --user=`whoami` --basedir="$(brew --prefix mysql)" --datadir=/usr/local/var/mysql --tmpdir=/tmp
- mysql.server start


## Static files
- Update your apache config file:
    - Alias the `STATIC_URL` folder to `STATIC_ROOT` in your Apache config.
        - `WSGIScriptAlias DISPLAY/static/ /MYPROJECTPATH/api/static`
- Run `python manage.py collectstatic -l`

## The API consists of three parts:

- api, a django app that responds to the queries
- scripts, a collection of import scripts that imports the PCR data from the old PCR site (and soon, ISC)
- wrappers, a set of of language wrappers for the API.  Currently, this means only an old PHP one.
