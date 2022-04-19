# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from dataclasses import dataclass
from enum import EnumMeta
from typing import Optional, List

import scrapy


class FrenchSchoolsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


@dataclass
class TeachingUnit:
    id: str
    name: str
    ects: Optional[float]
    courses: List[str]
    semester: Optional[int] = None


@dataclass
class ProgramItem:
    id: str
    name: str
    cycles: List[str]
    url: str
    teaching_units: List[TeachingUnit]
    ects: float


@dataclass
class Teacher:
    name: str
    speciality: Optional[str] = None


class Status(EnumMeta):
    MANDATORY = 'MANDATORY'
    OPTIONAL = 'OPTIONAL'
    SPECIALISATION = 'SPECIALISATION'


@dataclass
class CourseItem:
    id: str
    name: str
    url: str
    cycles: List[str]
    languages: List[str]
    teachers: List[Teacher]
    goal: str
    content: str
    additional_info: Optional[str] = None
    hours: Optional[int] = None
    status: Optional[Status] = None
    ects: Optional[float] = None
