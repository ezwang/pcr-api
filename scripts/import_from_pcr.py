from collections import defaultdict
import itertools
import string

import MySQLdb as db
from django.core.exceptions import ObjectDoesNotExist

#TODO: Figure out a better way to do this
#hack to get scripts to run with django
import os
import sys
sys.path.append("..")
sys.path.append("../api")
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from sandbox_config import IMPORT_DATABASE_NAME, IMPORT_DATABASE_USER, \
    IMPORT_DATABASE_PWD
from courses.models import Department, Instructor, Course, Section, Review, \
    ReviewBit, Semester, CourseHistory


class Importer(object):
  def __init__(self, db):
    self.db = db
    self._depts = {}

  def _run_query(self, query_str, args=None):
    print query_str
    cursor = self.db.cursor()
    cursor.execute(query_str, args)
    while cursor.nextset() is not None: pass
    return cursor.fetchall()

  def _select(self, fields, tables, conditions=None,
      group_by=None, order_by=None):
    query = ["SELECT", ", ".join(fields), "FROM", ", ".join(tables)]
    if conditions:
      query.extend(["WHERE", " AND ".join(conditions)])
    if group_by:
      query.extend(["GROUP BY", ", ".join(group_by)])
    if order_by:
      query.extend(["ORDER BY", ", ".join(order_by)])
    return self._run_query(" ".join(query))

  @property
  def departments(self):
    fields = ('dept_ID', 'dept_code', 'dept_title')
    return self._select(fields, ('coursereview_tbldepts',))

  @property
  def instructors(self):
    fields = ('lecturer_ID', 'first_name', 'last_name')
    return self._select(fields, ('coursereview_tbllecturers',))

  @property
  def courses(self):
    fields = ('course_ID', 'dept_ID', 'course_code', 'course_description',
        'crosslist_ID')
    tables = ('coursereview_tblcourses',)
    order_by = ('course_ID ASC',)
    return self._select(fields, tables, order_by=order_by)

  @property
  def course_histories(self):
    fields = ('c.course_ID', 's.year', 's.semester', 's.section_title')
    tables = ('coursereview_tblcourses as c', 'coursereview_tblsections as s')
    conditions = ('c.course_ID = s.course_ID',)
    group_by = ('s.course_ID', 's.year', 's.semester')
    order_by = ('s.course_ID',)
    return self._select(fields, tables, conditions, group_by, order_by)

  def sections(self, year, semester):
    fields = ('year', 'semester', 'course_ID', 'section_code', 'lecturer_ID',
        'section_ID', 'section_title')
    conditions = ('year="%s"' % year, 'semester="%s"' % semester)
    return self._select(fields, ('coursereview_tblsections',), conditions)

  def reviews(self, year, semester):
    fields = ('num_forms_returned', 'num_forms_produced', 'form_type',
        'course_ID', 'year', 'semester', 'section_code', 'section_ID',
        'lecturer_id')
    conditions = ('year="%s"' % year, 'semester="%s"' % semester)
    return self._select(fields, ('coursereview_tblsections',), conditions)

  def comments(self, year, semester):
    fields = ['review', 'lecturer_ID', 'course_ID']
    conditions = ['year="%s"' % year, 'semester="%s"' % str(semester).upper()]
    comments = {}
    for review, lecturer_id, course_id in self._select(fields, \
        ('coursereview_tbllecturerreviews',), conditions):
      if review is not None:
        review = review.decode('cp1252', "ignore").encode(
            'utf-8', 'ignore')
      comments[course_id, lecturer_id] = review
    return comments

  @property
  def _review_bit_fields(self):
    return ('rInstructorQuality', 'rCourseQuality', 'rDifficulty',
        'rCommAbility', 'rInstructorAccess', 'rReadingsValue',
        'rAmountLearned', 'rWorkRequired', 'rRecommendMajor',
        'rRecommendNonMajor', 'rArticulateGoals', 'rSkillEmphasis',
        'rHomeworkValuable', 'rExamsConsistent', 'rAbilitiesChallenged',
        'rClassPace', 'rStimulateInterest', 'rOralSkills',
        'rInstructorConcern', 'rInstructorRapport', 'rInstructorAttitude',
        'rInstructorEffective', 'rGradeFairness', 'rNativeAbility',
        'rTAQuality', 'section_ID')

  def review_bits(self, year, semester):
    conditions = ('year="%s"' % year, 'semester="%s"' % semester)
    return self._select(self._review_bit_fields, \
        ('coursereview_tblsections',), conditions)

  def import_departments(self):
    for dept_id, code, title in self.departments:
      dept, _ = Department.objects.get_or_create(code=code.strip())
      dept.name = string.capwords(title)
      dept.save()
      # a bit of a hack-- We can't later uniquely identify departments by
      # their old ids in future references, so we need to store their ids
      # it's possible there exists a more efficient way to store these
      self._depts[dept_id] = dept


  def import_instructors(self):
    for oldpcr_id, first_name, last_name in self.instructors:
      Instructor.objects.get_or_create(oldpcr_id=oldpcr_id,
        first_name=first_name,
        last_name=last_name
        )

  def import_courses(self):
    # requires department was called first
    course_names = {}
    sems_taught = defaultdict(list)
    for course_id, year, semester, name in self.course_histories:
      course_names[course_id] = name
      sems_taught[course_id].append(Semester(year, semester))

    for course_id, dept_id, course_num, description, crosslist_id \
        in self.courses:
      name = course_names[course_id]
      oldpcr_id = crosslist_id or course_id
      dept = self._depts[dept_id]

      courses = set()
      for semester in sems_taught[course_id]:
        course, _ = Course.objects.get_or_create(
            oldpcr_id=oldpcr_id,
            semester=semester,
            defaults={
              "name": name or "%s %d" % (dept.code, int(course_num)),
              "description": description,
              "history": None
              }
            )
        courses.add(course)

      histories = set(course.history for course in courses if course.history)
      if len(histories) > 1:
        raise "Course %d is already tied to multiple course_histories!" \
            % (course_id,)
      else:
        if histories:
          history = histories.pop()
          for course in courses:
            course.history = history
            course.save()
        else:
          for course in courses:
            course.history = CourseHistory.objects.create(
                notes="Created from PCR ID: %s" % course_id)
            course.save()

  def import_sections(self, year, semester):
    for _, _, course_id, sectionnum, lecturer_id, oldpcr_id, name \
        in self.sections(year, semester):
      section, _ = Section.objects.get_or_create(
          course=Course.objects.get(id=course_id),
          sectionnum=sectionnum,
          defaults={
            "oldpcr_id": oldpcr_id,
            "group": None,
            "sectiontype": None,
            "name": name or ""
            }
          )
      try:
        section.instructors.add(Instructor.objects.get(oldpcr_id=lecturer_id))
      except ObjectDoesNotExist:
        section.instructors.add(
            Instructor.objects.get_or_create(oldpcr_id=lecturer_id))
      section.save()

  def import_reviews(self, year, semester):
    for forms_returned, forms_produced, form_type, course_id, year, \
        semester, section_num, oldpcr_id, lecturer_id in self.reviews(year, \
        semester):
      try:
        instructor = Instructor.objects.get(id=lecturer_id)
        try:
          comments = self.comments(year, semester)[course_id, lecturer_id]
        except KeyError:
          comments = None
        section = Section.objects.get(course__oldpcr_id=course_id)
        Review.objects.get_or_create(section=section,
         instructor=instructor,
         defaults={"forms_returned": forms_returned,
                     "forms_produced": forms_produced,
                     "form_type": form_type,
                     "comments": comments
                     }
         )
      except ObjectDoesNotExist:
        print "Can't find instructor ID: %d for review %s" \
            % (lecturer_id, section_num)

  def import_review_bits(self, year, semester):
    for review_bit_raw in self.review_bits(year, semester):
      # a review bit is a bunch of scores followed by the section id
      section_id = review_bit_raw[-1]
      review = Review.objects.get(section__id=section_id)
      if review:
        for field, score in itertools.izip(self._review_bit_fields[:-1], \
            review_bit_raw[:-1]):
          if score:
            ReviewBit.objects.get_or_create(
                review=review,
                field=field,
                score=score
                )
      else:
        print "Missing review for section: %d" % (section_id,)


if __name__ == "__main__":
  importer = Importer(db.connect(db=IMPORT_DATABASE_NAME, \
      user=IMPORT_DATABASE_USER, passwd=IMPORT_DATABASE_PWD))
  importer.import_departments()
  importer.import_instructors()
  importer.import_courses()

  years = range(2002, 2012)
  for year, semester in itertools.product(years, ('a', 'b', 'c')):
    importer.import_sections(year, semester)
    importer.import_reviews(year, semester)
    importer.import_review_bits(year, semester)
