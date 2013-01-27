# Setup

- Clone repo.
- Copy `api/sandbox_config.py_default` to `api/sandbox_config.py`
- Edit `DISPLAY_NAME`, `DEV_ROOT`, and `DATABASE_*` appropriately.
    - **Note:** Ensure DISPLAY_NAME begins with a forward slash. (This ensure it is never used relatively.)
    - **Note:** If you cloned the project into anything but `Penn-Course-Review-api`, you will need to change COURSESAPI_APP_ROOT to match.
- Update your apache config file (in `/etc/apache2/sites-available/`:
    - `WSGIScriptAlias /pcrapi /MYPROJECTPATH/api/django.wsgi`

## Static files
- Update your apache config file:
    - Alias the `STATIC_URL` folder to `STATIC_ROOT` in your Apache config.
        - `WSGIScriptAlias DISPLAY/static/ /MYPROJECTPATH/api/static`
- Run `python manage.py collectstatic -l`

## The API consists of three parts:

- api, a django app that responds to the queries
- scripts, a collection of import scripts that imports the PCR data from the old PCR site (and soon, ISC)
- wrappers, a set of of language wrappers for the API.  Currently, this means only an old PHP one.
