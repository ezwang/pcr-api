
# PennCourseReview API

Provides the PennCourseReview API.

# Setup

(Linux) Make sure you have the `libmysqlclient-dev` library installed:

```
sudo apt-get install libmysqlclient-dev
```

Install requirements with:

```
pip install -r requirements.txt
```

## MySQL Setup

The PennCourseReview API relies on MySQL for a database.

To install and setup MySQL on a Mac, use [Homebrew][1]:

```
brew remove mysql
brew cleanup
brew install mysql
mysql_install_db --verbose --user=whoami --basedir="$(brew --prefix mysql)" --datadir=/usr/local/var/mysql --tmpdir=/tmp
mysql.server start
```

## Configuration

Configuration variables are stored in `sandbox_config.py`.

Copy the defaults via: `cp sandbox_config.py_default sandbox_config.py`

Next, edit `sandbox_config.py` as necessary.

For local development, you may need to create a database.

1. Open the mysql shell with `mysql --user=root mysql`.
2. Create the database `CREATE DATABASE <DATABASE_NAME>;` where `<DATABASE_NAME>` is the value of `sandbox_config.DATABASE_NAME`.

Finally, sync the database with `python ./manage.py syncdb`.

## Static files

run: `python manage.py collectstatic -l`

# Usage

To run the server:

```
python ./manage.py runserver
```

You may want to create a token to access data. Run `python ./manage.py maketoken` to create a token called "public".

Finally hit `http://localhost:8000/?token=public` to check that everything worked.

[1]: http://brew.sh/

# Testing

To test the server:

```
python ./manage.py test apiconsumer courses
```

At the time of writing, there are no failures in the test suite, but coverage is
relatively minimal.
