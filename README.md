
# PennCourseReview API

API for Penn Course Review Data.

Used by the PennCourseReview frontend and others.

# Architecture

The PCR API is composed of two parts. The scripts which pull the course data from the registrar and the legacy PCR database, and the site which powers the API itself.

## api
The api itself consists of five apps-- apiconsumer, course_descriptions, courses, static_content, and testconsole.

### apiconsumer
Sets permission levels for developers who wish to use our API. This is mainly in place because the data should only be accessible to Penn students and faculty.

### course_descriptions
Parses the course register. (Probably should be moved to /scripts)

### courses
Powers the actual API.

### static_content
Responsible for powering the static pages on the PCR site. It's basically a very simple version of a CMS and exists solely so that admins only have to manage one admin site.

### testconsole
testconsole is a simple javascript interface for the api.

## scripts
Responsible for scraping new data from the registrar and grabbing old data from the legacy PCR site.

### PCR Daemon User
Username: pcr-daemon
Password: laurenspringer

### Instructions to update the PCR API database

1. Change your directory to Penn-Course-API/scripts
2. Run "python download.py"
    * This scrapes the registrar, cleans up the data, and dumps it into /registrardata.
3. Run "python uploadcourses.py YEAR SEMESTER registrardata/*.txt"
   * uploadcourses.py [YEAR] [SEMESTER] [*FILES] parses the data scraped from download.py and uses it to update the PCR API database.
   * SEMESTER accepts either 'a', 'b', or 'c'
   * (ie, run "python uploadcourses.py 2009 a registrardata/econ.txt")
   * Since the registrar data changes every year, YEAR should be the current year, and SEMESTER the current semester.
4. Run "python import_from_pcr.py YEAR SEMESTER"
   * import_from_pcr.py [YEAR] [SEMESTER] reads from an external database-- assumed to have the original PCR records --and creates or updates course and review data in the new PCR API database.
   * (This can take a while.)
