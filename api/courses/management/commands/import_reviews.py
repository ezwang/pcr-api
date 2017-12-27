import os
import json

from django.core.management.base import BaseCommand, CommandError

from ...models import Review, Semester, Alias, Section, Department, Instructor


class Command(BaseCommand):
    help = "Imports reviews from the pcr-reviewer application."

    def add_arguments(self, parser):
        parser.add_argument("file", nargs="?", type=str, default="reviews.json")

    def handle(self, *args, **options):
        if options["file"]:
            filename = os.path.abspath(options["file"])
        else:
            raise CommandError("You need to specify a file to load from!")

        if not os.path.isfile(filename):
            raise CommandError("The file '{}' does not exist!".format(filename))

        self.stdout.write("Loading from '{}'".format(filename))

        with open(filename, "r") as f:
            data = json.load(f)

        count = 0

        for section in data:
            if section["comments"] or section["tags"]:
                dept, course, sect = section["section"][:-6], int(section["section"][-6:-3]), int(section["section"][-3:])
                dept = Department.objects.get(code=dept)
                semester = Semester(section["term"])
                alias = Alias.objects.get(department=dept, coursenum=course, semester=semester)
                sect = Section.objects.get(course=alias.course, sectionnum=sect)
                last, first = [x.strip() for x in section["instructor"]["name"].split(",")]
                first = first.split(" ", 1)[0]
                inst = Instructor.objects.get(last_name=last, first_name__startswith=first)
                review = Review.objects.get(section=sect, instructor=inst)
                # TODO: modify review object

                count += 1
            else:
                self.stdout.write(self.style.WARNING("Skipping {}, no comments or tags found...".format(section["section"])))

        self.stdout.write(self.style.SUCCESS("{} reviews processed!".format(count)))
