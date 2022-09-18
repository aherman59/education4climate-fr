# -*- coding: utf-8 -*-
from pathlib import Path

import scrapy
from abc import ABC

from settings import YEAR, CRAWLING_OUTPUT_FOLDER
from scrapy.utils.project import get_project_settings

import pandas as pd


settings = get_project_settings()
CRAWLING_OUTPUT_FOLDER = settings.get("CRAWLING_OUTPUT_FOLDER")
YEAR = settings.get("YEAR")

BASE_URL = "https://www.insa-toulouse.fr"
PROG_DATA_PATH = Path(f"{CRAWLING_OUTPUT_FOLDER}").joinpath(
    f"insa_toulouse_programs_{YEAR}.json"
)

LANGUAGES_DICT = {
    "Français": ["fr"],
}

class InsaToulouseCourseSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Insa Toulouse
    """

    name = "insa_toulouse_courses"
    custom_settings = {
        "FEED_URI": Path(f"{CRAWLING_OUTPUT_FOLDER}")
        .joinpath(f"insa_toulouse_courses_{YEAR}.json")
        .as_uri()
    }

    def start_requests(self):
        # Recup des URLs des cursus ingénieurs
        programs = pd.read_json(open(PROG_DATA_PATH, "r"))

        for (index, program_row) in programs.iterrows():
            cursus_name = program_row['cursus_name']
            courses_ids = program_row['courses_ids']
            courses_names = program_row['courses_names']
            courses_urls = program_row['courses_urls']
            for course_id, course_name, course_url in zip(courses_ids, courses_names, courses_urls):
                yield scrapy.Request(
                    url=BASE_URL + course_url,
                    callback=self.parse_course,
                    cb_kwargs={"cursus_name": cursus_name,
                               "course_id": course_id,
                               "course_name": course_name}
                )


    @staticmethod
    def parse_course(response, cursus_name, course_id, course_name):
        # Titre du cours
        name = response.xpath("//span[@class='ametys-page-title']/text()").get()
        # Objectif
        if 'Objectifs' in response.xpath("//div[@class='col-md-9 col-sm-9 col-xs-9']/h2//text()").getall():
            goal = ''.join(response.xpath("//div[@class='col-md-9 col-sm-9 col-xs-9']/p/text()").getall())
        else:
            goal = ''
        # Nbre de credits ECTS et nbre d'heures (s'ils sont affichés)
        if len(response.xpath("//div[@class='bloc brief']//text()").getall()) == 10:
            ects = response.xpath("//div[@class='bloc brief']//text()").getall()[6]
            nb_heures = response.xpath("//div[@class='bloc brief']//text()").getall()[9]
        else:
            ects = ""
            nb_heures = ""

        yield {
            "id": course_id,
            "program_id": cursus_name,
            "name": name,
            "year": f"{YEAR}",
            "languages": ['fr'],
            "teachers": "",
            "url": response.url,
            "goal": goal,
            "program_content": "",
            "ects" : ects,
            "duration" : nb_heures
        }