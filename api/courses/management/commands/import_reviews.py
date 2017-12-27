import os
import json

from django.core.management.base import BaseCommand, CommandError

from ...models import Review


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
                count += 1
                # TODO: add comments and tags to database

        self.stdout.write(self.style.SUCCESS("{} reviews processed!".format(count)))
