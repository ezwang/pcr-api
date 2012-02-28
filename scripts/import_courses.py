#TODO: Figure out a better way to do this
#hack to get scripts to run with django
import os
import sys
sys.path.append("..")
sys.path.append("../api")
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from courses.models import Course
from sandbox_config import IMPORT_DATABASE_NAME, IMPORT_DATABASE_USER, \
    IMPORT_DATABASE_PWD
from extractor import Extractor


def extract_courses(extractor):
    fields = ('course_id', 'paragraph_number', 'course_description')
    # course_id is of form CIS110
    # course_description is split into paragraphs each with a number
    tables = ('TEST_PCR_COURSE_DESC_V',)
    order_by = ('course_id ASC', 'paragraph_number ASC')
    courses = self._select(fields, tables, order_by=order_by)

    def keyfunc(course):
      return course[0]  # id

    for id, paragraphs in groupby(courses, key=keyfunc):
      dept = re.search("[A-Z]*", id).group(0)
      code = re.search("\d+", id).group(0)
      description = "\n".join(paragraph for _, _, paragraph in paragraphs)
      # TODO: Crosslist ID
      crosslist_id = None
      yield id, dept, code, description, crosslist_id


def load(row):
  oldpcr_id, first_name, last_name = row
  Instructor.objects.get_or_create(
    oldpcr_id=oldpcr_id,
    first_name=first_name,
    last_name=last_name
    )


if __name__ == "__main__":
  extractor = Extractor(IMPORT_DATABASE_NAME, IMPORT_DATABASE_USER, IMPORT_DATABASE_PWD)
  for val in extract(extractor):
    load(val)
