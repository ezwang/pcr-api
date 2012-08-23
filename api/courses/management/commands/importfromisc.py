"""
A Django-specific command for importing course and review data from
ISC's data dumps.

This command (`./manage.py importfromisc`) should be run after ISC's
data dumps have been turned into SQL and loaded into a database.
It will NOT import the qualitative reviews from PCR, that must be done
separately (and after).
"""
__author__ = 'Kyle Hardgrave (kyleh@sas.upenn.edu)'

from optparse import make_option
import time
import traceback

import MySQLdb as db
from django.core.management.base import BaseCommand, CommandError

from courses.models import (Alias, Course, CourseHistory, Department,
                            Instructor, Review, ReviewBit, Section, Semester)
from sandbox_config import (IMPORT_DATABASE_NAME, IMPORT_DATABASE_USER,
                            IMPORT_DATABASE_PWD)


class Command(BaseCommand):
  """A manage.py command to import review data from ISC's DBs.
  We import things in semester-wise chunks so that, if there's an error,
  you hopefully only have to redo one semester. Within each semester,
  we import in three stages:

  1. **Main stage**. The main table has _almost_ everything we need.
     We go through each row that represents a PRIMARY LISTING of a section
     and (or find) everything from that.
  2. **Aliasing**. After we have all the primary listings, we make another
     pass through the main table and look at every row where the
     PRI_SECTION and SECTION_ID key don't match - i.e., a crosslisting.
     Here we only add the Alias and nothing else - we expect the
     course to exist already.
       Since we were provided with a separate database of crosslistings,
     we make a pass over that as well (`alt_import_aliases`). This one
     tends to have a few cross-listings that weren't covered in the first.
     Even MORE fun, it has DOZENS of crosslistings for courses that don't
     appear to exist. We ignore these. YAY!
  3. **Descriptions**. Because descriptions are stored by course ID ONLY,
     and in a different table, we dot these last. These are batch added to
     any Course that doesn't already
  """
  args = '[all | <semester semester ...>]'
  help = 'Imports the given semesters from the ISC database dumps to Django'

  option_list = (
    make_option('-e', '--catcherrors', action='store_true',
                help='Log errors instead of interrupting the import'),
    make_option('-d', '--db', help='Use an alternate database (uses ' \
                  'the IMPORT_DATABASE in sandbox_config by default)'),
    make_option('-u', '--user', help='Alternate database username'),
    make_option('-p', '--passwd', help='Alternate database password'),
    ) + BaseCommand.option_list

  SUMMARY_TABLE = 'TEST_PCR_SUMMARY_HIST_V'
  RATING_TABLE = 'TEST_PCR_RATING_V'
  CROSSLIST_TABLE = 'TEST_PCR_CROSSLIST_SUMMARY_V'
  DESC_TABLE = 'TEST_PCR_COURSE_DESC_V'

  depts = {}
  num_created = {
    'Alias': 0,
    'Course': 0,
    'CourseHistory': 0,
    'Department': 0,
    'Instructor': 0,
    'Review': 0,
    'ReviewBit': 0,
    'Section': 0,
    }
  num_errors = 0


  def handle(self, *args, **opts):
    """Handle command line arguments."""
    try:
      self.verbosity = int(opts['verbosity']) if opts['verbosity'] else 1
      self.catch_errors = opts['catcherrors']

      # Set database
      db_name = opts['db'] if opts['db'] else IMPORT_DATABASE_NAME
      db_user = opts['user'] if opts['user'] else IMPORT_DATABASE_USER
      db_pw = opts['passwd'] if opts['passwd'] else IMPORT_DATABASE_PWD
      # TODO(kyleh): Prompt for password, don't accept at command line
      self.log('Using database %s and user %s' % (db_name, db_user))
      self.db = db.connect(db=db_name, user=db_user, passwd=db_pw)

      # Set the semesters; this also validates the input
      if not args or args == 'all':
        self.log('Importing all available semesters.')
        terms = self.select(['term'], [self.SUMMARY_TABLE],
                             conditions=['term > "2002A"'],
                             group_by=['term'], order_by=['term'])
        semesters = [Semester(term[0]) for term in terms]
      else:
        semesters = [Semester(sem_arg) for sem_arg in set(args)]

      # Do the magic
      for sem in semesters:
        self.log('Importing %s' % sem)
#        self.import_reviews(sem)
#        self.import_aliases(sem)
        # self.alt_import_aliases(sem)
        self.log('--------------------------------------------------')
      self.import_descriptions() # Done in aggregate since not sem-specific

    except KeyboardInterrupt:
      self.err('Aborting...')
      self.db.close()

    # Some helpful info before we leave
    self.print_stats()


  def import_descriptions(self):
    """Import all the Course descriptions."""
    courses_updated = 0

    fields = ['course_id', 'paragraph_number', 'course_description']
    tables = [self.DESC_TABLE]
    order_by = ['course_id ASC', 'paragraph_number ASC']
    descriptions = self.select(fields, tables, order_by=order_by)

    def commit_courses(course_id, courses, desc):
      self.log('--------------------')
      self.log('Adding description for %s to %d courses.' % (
          course_id, courses.count()))
      for course in courses:
        self.log('-> %s: %s...' % (course, desc), 2)
        course.description = desc
        try:
          course.save()
        except Exception:
          self.handle_err('Error processing %s:' % course_id)
      
    full_desc = ''
    courses = None
    last_course_id = ''
    for course_id, graph_num, desc in descriptions:
      graph_num = int(graph_num) # Why is this a string? I don't know
      dept_code, course_code, _ = self.parse_sect_str(course_id)
      try:
        dept = Department.objects.get(code=dept_code)
      except Department.DoesNotExist:
        continue

      if graph_num == 1: # The beginning of a new sequence
        if full_desc: # We have the full previous description; save:
          commit_courses(last_course_id, courses, full_desc)
          courses_updated += 1
        # Start anew
        full_desc = '%s\n\n' % desc
        last_course_id = course_id
        courses = Course.objects.filter(primary_alias__department=dept,
                                        primary_alias__coursenum=course_code,
                                        description='')
      else:
        # This is the second (or third or w/e) part of a description - go on
        full_desc += '%s\n\n' % desc

    # Add remaining courses
    commit_courses(last_course_id, courses, full_desc)
    courses_updated += 1

    self.log('Updated %d course descriptions.' % courses_updated)


  def import_reviews(self, sem):
    """Import the given semesters' courses and reviews.

    The main entry-point for importing everything. Note that this only
    imports primary listings, `import_aliases` must be called to handle
    crosslistings.

    Args:
      sem: A Semester object to import, like `Semester(2011, 'A')`.
        If `None`, imports all available semesters.
    """

    main_fields = [ # All fields are strings unless otherwise indicated
      'title', 'pri_section', 'subject_area_desc',
      'instructor_penn_id', 'instructor_fname', 'instructor_lname',
      'enrollment', 'responses', 'form_type', # <- numbers
      ]
    review_fields = [ # The many rating vectors - all numbers, or null
      'rInstructorQuality', 'rCourseQuality', 'rDifficulty',
      'rCommAbility', 'rStimulateInterest', 'rInstructorAccess',
      'rReadingsValue', 'rAmountLearned', 'rWorkRequired',
      'rRecommendMajor', 'rRecommendNonMajor', 'rArticulateGoals',
      'rSkillEmphasis', 'rHomeworkValuable', 'rExamsConsistent',
      'rAbilitiesChallenged', 'rClassPace', 'rOralSkills',
      'rInstructorConcern', 'rInstructorRapport',
      'rInstructorAttitude', 'rInstructorEffective',
      'rGradeFairness', 'rNativeAbility', 'rTAQuality',
      ]
    tables = [self.SUMMARY_TABLE]
    # Prevents a few duplicates where the number of responses or from type
    # has changed.
    group_by = ['pri_section',  'instructor_penn_id']
    # We always take the first review with the highest number of responses.
    order_by = ['pri_section ASC', 'instructor_penn_id ASC', 'responses DESC']
    conditions = ['pri_section = section_id', 'term = "%s"' % sem.code()]
    reviews = self.select(main_fields + review_fields, tables,
                          conditions=conditions, order_by=order_by,
                          group_by=group_by)
    r = {} # The dictionary holding all the scores on each iteration

    # Take care to keep this megatuple in sync with the queried fields
    # described above.
    for (title, pri_sect, subj_name,
         prof_id, prof_fname, prof_lname,
         size, responses, form_type,
         r['rInstructorQuality'], r['rCourseQuality'], r['rDifficulty'],
         r['rCommAbility'], r['rStimulateInterest'], r['rInstructorAccess'],
         r['rReadingsValue'], r['rAmountLearned'], r['rWorkRequired'],
         r['rRecommendMajor'], r['rRecommendNonMajor'], r['rArticulateGoals'],
         r['rSkillEmphasis'], r['rHomeworkValuable'], r['rExamsConsistent'],
         r['rAbilitiesChallenged'], r['rClassPace'], r['rOralSkills'],
         r['rInstructorConcern'], r['rInstructorRapport'],
         r['rInstructorAttitude'], r['rInstructorEffective'],
         r['rGradeFairness'], r['rNativeAbility'], r['rTAQuality']
         ) in reviews:

      full_row_str = '%s @ %s (%s, %s)' % (pri_sect, sem.code(),
                                           prof_lname, prof_fname)
      self.log('--------------------')
      self.log('Loading %s' % full_row_str)

      try:
        # Fix types
        subj_code, course_code, sect_code = self.parse_sect_str(pri_sect)
        prof_id = int(prof_id)
        # A rare few courses have NULL titles
        title = '' if title is None else title

        # Departments.
        dept = self.get_or_create(Department, code=subj_code)
        if not dept.name: # Only set dept.name if not already set
          dept.name = subj_name
          dept.save()

        # CourseHistories. We use the history of the _most recent_
        # course that has the same primary listing.
        try:
          hist = CourseHistory.objects.filter(
            course__primary_alias__department=dept,
            course__primary_alias__coursenum=course_code
            ).order_by('-course__semester')[0]
          self.log('Reused CourseHistory: %s' % hist, 2)
        except IndexError: # Returned empty QuerySet
          hist = CourseHistory(notes='Created from PCR Course %s-%3d: %s' % (
              subj_code, course_code, title))
          hist.save()
          self.log('Created new CourseHistory: %s' % hist, 2)
          self.num_created['CourseHistory'] += 1

        # Course + Primary Alias.
        course = self.get_or_create(Course, semester=sem, history=hist)
        alias = self.get_or_create(
          Alias, course=course, department=dept, coursenum=course_code,
          semester=sem)
        course.primary_alias = alias # Resave with non-null primary_alias
        if not course.name: # Only set course.name if not already set
          course.name = title
        course.save()

        # Instructor, Section, Review.
        # These are all fairly self-explanatory.
        prof = self.get_or_create(
          Instructor, first_name=prof_fname, last_name=prof_lname,
          oldpcr_id=prof_id)
        sect = self.get_or_create(
          Section, course=course, name=title, sectionnum=sect_code)
        sect.instructors.add(prof) # Many-to-many field

        # Reviews. Ignore review data from reviews with no responses,
        # as some have 0's (instead of NULL).
        if responses > 0:
          review = self.get_or_create(
            Review, section=sect, instructor=prof, forms_returned=responses,
            forms_produced=size, form_type=form_type)

          # ReviewBit. Log these in aggregate - too annoying otherwise.
          bits_added = 0
          bits_existing = 0
          for field in review_fields:
            if r[field] is not None: # Many of the review vectors are NULL
              bit, bit_created = ReviewBit.objects.get_or_create(
                review=review, field=field, score=r[field])
              if bit_created:
                bits_added += 1
              else:
                bits_existing += 1
          self.log('Created %d new ReviewBits. Reused %d.' % (
              bits_added, bits_existing), 2)
          self.num_created['ReviewBit'] += bits_added

      except Exception:
        self.handle_err('Error processing %s:' % full_row_str)

    self.print_stats()


  def import_aliases(self, sem):
    """Import the given semesters' crosslistings.

    After calling `import_primary`, this simply makes a second pass
    over the summary table and imports all the crosslistings.

    Args:
      sem: A Semester object to import, like `Semester(2011, 'A')`.
        If `None`, imports all available semesters.
    """
    fields = ['section_id', 'pri_section']
    tables = [self.SUMMARY_TABLE]
    order_by = ['pri_section ASC']
    conditions = ['pri_section != section_id', 'term = "%s"' % sem.code()]
    aliases = self.select(fields, tables, conditions=conditions,
                          order_by=order_by)

    for sect_id, pri_sect in aliases:
      full_row_str = '%s -> %s @ %s' % (pri_sect, sect_id, sem.code())
      self.log('--------------------')
      self.log('Crosslisting %s' % (full_row_str))

      try:
        pri_dept_code, pri_coursenum, _ = self.parse_sect_str(pri_sect)
        xlist_dept_code, xlist_coursenum, _ = self.parse_sect_str(sect_id)
        pri_dept = self.get_or_create(Department, code=pri_dept_code)
        xlist_dept = self.get_or_create(Department, code=xlist_dept_code)

        course = Course.objects.get(
          semester=sem, primary_alias__department=pri_dept,
          primary_alias__coursenum=pri_coursenum)

        alias = self.get_or_create(
          Alias, course=course, department=xlist_dept,
          coursenum=xlist_coursenum, semester=sem)

      except Exception:
        self.handle_err('Error cross-listing %s:' % full_row_str)

    self.print_stats()


  def alt_import_aliases(self, sem):
    """Import Aliases for a given semester, using the CROSSLIST_SUMMARY table.

    This does effectively the same thing as `import_aliases`, except
    with the table specific to crosslisting. AFAICT, there are only a
    small number of crosslistings that *only* exist in this table, e.g.,
    six in 2011A.

    Note: This table bizarrely includes crosslistings for a number of
    courses that *don't* appear in the summary table. We avoid these on
    principle (and count/log them at the end).

    There may be a faster way to use both tables using some JOIN magic,
    but for simplicity I've left this as its own function.

    Args:
      sem: A Semester object to import, like `Semester(2011, 'A')`.
        If `None`, imports all available semesters.
    """
    fields = ['section_id', 'xlist_section_id_1', 'xlist_section_id_2',
              'xlist_section_id_3', 'xlist_section_id_4', 'xlist_section_id_4']
    tables = [self.CROSSLIST_TABLE] # Note the difference
    order_by = ['section_id']
    # Ignore sections without any crosslistings:
    conditions = ['xlist_section_id_1 is not null', 'term = "%s"' % sem.code()]
    aliases = self.select(fields, tables, conditions=conditions,
                          order_by=order_by)

    xlist_ids = {} # Store the (up to five) crosslistings from each row
    num_nonexist = 0
    for (sect_id, xlist_ids[1], xlist_ids[2], xlist_ids[3], xlist_ids[4],
         xlist_ids[5]) in aliases:
      self.log('--------------------')
      self.log('Crosslistng %s @ %s' % (sect_id, sem.code()))

      try:
        # Fix types
        pri_dept_code, pri_coursenum, _ = self.parse_sect_str(sect_id)
        pri_dept = self.get_or_create(Department, code=pri_dept_code)

        try: # Ignore courses that weren't in the main import
          course = Course.objects.get(
            semester=sem, primary_alias__department=pri_dept,
            primary_alias__coursenum=pri_coursenum)
        except Course.DoesNotExist:
          self.err('Tried to crosslist with a course that does not exist!')
          num_nonexist += 1
          continue

        for xlist_id in xlist_ids.itervalues():
          if xlist_id is None: # Don't waste time when we run out of xlists
            break
          self.log('--> Aliasing %s' % xlist_id)

          xlist_dept_code, xlist_coursenum, _ = self.parse_sect_str(xlist_id)
          xlist_dept = self.get_or_create(Department, code=xlist_dept_code)

          alias = self.get_or_create(
            Alias, course=course, department=xlist_dept,
            coursenum=xlist_coursenum, semester=sem)

      except Exception:
        self.handle_err('Error cross-listing % @ %s:' % (sect_id, sem.code()))

    if num_nonexist: # Report the number of nonexistant at the end.
      self.err('Tried to crosslist with %d nonexist courses.' % num_nonexist)
    self.print_stats()



  # Helpers
  def handle_err(self, msg):
    """Log unknown errors and print stack trace. That way a random DB error
    won't ruin a long import."""
    if self.catch_errors:
      self.err('--------------------------------------------------')
      self.err(msg)
      self.err(traceback.format_exc())
      self.num_errors += 1
    else:
      raise


  def print_stats(self):
    """Print the info on what we've done so far."""
    self.log('--------------------------------------------------')
    self.log('New objects: %s' % (
        ', '.join(['%d %s' % (num, model)
                   for model, num in self.num_created.iteritems()])))
    self.log('Uncaught errors: %d' % self.num_errors)


  def get_or_create(self, model, **kwargs):
    """A wrapper for Django's Model.objects.get_or_create() that does
    some logging. In the case of Department, it hits the cache first
    and updates it if necessary.

    Args:
      model: The Django model, e.g., `Instructor`.
      kwargs: The same keyword args passed to the original.

    Returns:
      A Model instance.
    """
    is_dept = model == Department
    if is_dept: # For departments, check the cache
      dept_code = kwargs['code']
      try:
        dept = self.depts[dept_code]
        self.log('Reused cached Department %s: %s' % (dept.code, dept.name), 2)
        return dept
      except KeyError:
        pass

    name = model.__name__
    obj, created = model.objects.get_or_create(**kwargs)
    if created:
      self.log('Created new %s: %s' % (name, obj), 2)
      self.num_created[name] += 1
    else:
      self.log('Reused existing %s: %s' % (name, obj), 2)

    if is_dept: # Update Department cache
      self.depts[obj.code] = obj

    return obj


  def parse_sect_str(self, section_str):
    """Turn a DB section or course string into a nice tuple.
    'CIS 120001' -> ('CIS', 125, 1). 'CIS 099' -> ('CIS', 99, None)

    In the DB, the strings are always 10 characters (or 7 for courses),
    and padded with spaces based on the length of the deparment code.
    """
    try:
      sect_code = int(section_str[7:10])
    except ValueError:
      sect_code = None
    return (section_str[0:4].strip(), int(section_str[4:7]), sect_code)


  def query(self, query_str, args=None):
    """A simple wrapper for our MySQL queries."""
    start = time.time()
    self.log('Executing query: "%s"' % query_str, 2)
    cursor = self.db.cursor()
    cursor.execute(query_str, args)
    results = cursor.fetchall()
    self.log('Took: %s' % (time.time() - start), 2)
    self.log('Founds %s results.' % len(results), 2)
    return results


  def select(self, fields, tables, conditions=None, group_by=None,
        order_by=None):
    """A wrapper for MySQL SELECT queries.

    Args:
      fields: List of database row names
      tables: List of database table names
      conditions: Map of field-value pairs to filter by
      group_by: List of fields to group (aggregate) by
      order_by: List of fields to order by
    """
    query = ["SELECT", ", ".join(fields), "FROM", ", ".join(tables)]

    if conditions:
      query.extend(["WHERE", " AND ".join(conditions)])

    if group_by:
      query.extend(["GROUP BY", ", ".join(group_by)])

    if order_by:
      query.extend(["ORDER BY", ", ".join(order_by)])

    return self.query(" ".join(query))


  def log(self, msg, v=1):
    """Log messages to standard out, depending on the verbosity."""
    if self.verbosity >= v:
      self.stdout.write('%s\n' % msg)


  def err(self, msg):
    """Log errors to stderr, regardless of verbosity."""
    self.stderr.write('ERR: %s\n' % msg)
