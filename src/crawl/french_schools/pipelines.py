# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import dataclasses
import json
from pathlib import Path

from crawl.french_schools.items import CourseItem, ProgramItem
from crawl.french_schools.settings import CRAWLING_OUTPUT_FOLDER, YEAR


class FrenchSchoolsPipeline:
    def process_item(self, item, spider):
        return item


class CoursePipeline(object):
    is_file_empty = True

    def open_spider(self, spider):
        self.file = open(
            Path(f"{CRAWLING_OUTPUT_FOLDER}").joinpath(f"{spider.name}_courses_{YEAR}.json"),
            'w'
        )
        self.file.write('[')

    def close_spider(self, spider):
        self.file.write(']')
        self.file.close()

    def process_item(self, item, spider):
        if isinstance(item, CourseItem):
            line = json.dumps(dataclasses.asdict(item))
            if not self.is_file_empty:
                self.file.write(',')
            else:
                self.is_file_empty = False
            self.file.write(line)
        return item


class ProgramPipeline(object):
    is_file_empty = True

    def open_spider(self, spider):
        self.file = open(
            Path(f"{CRAWLING_OUTPUT_FOLDER}").joinpath(f"{spider.name}_programs_{YEAR}.json"),
            'w'
        )
        self.file.write('[')

    def close_spider(self, spider):
        self.file.write(']')
        self.file.close()

    def process_item(self, item, spider):
        if isinstance(item, ProgramItem):
            line = json.dumps(dataclasses.asdict(item))
            if not self.is_file_empty:
                self.file.write(',')
            else:
                self.is_file_empty = False
            self.file.write(line)
        return item
