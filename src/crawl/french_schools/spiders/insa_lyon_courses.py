from abc import ABC
import io
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qsl

import pandas as pd
import scrapy
from borb.pdf.pdf import PDF
from borb.toolkit.text.simple_text_extraction import SimpleTextExtraction

from scrapy.utils.project import get_project_settings

settings = get_project_settings()
CRAWLING_OUTPUT_FOLDER = settings.get("CRAWLING_OUTPUT_FOLDER")
YEAR = settings.get("YEAR")

BASE_URL = "https://www.insa-lyon.fr"
PROG_DATA_PATH = Path(f"{CRAWLING_OUTPUT_FOLDER}").joinpath(
    f"insa_lyon_programs_{YEAR}.json"
)

LANGUAGES_DICT = {
    "Français": ["fr"],
}


class InsaLyonCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for Insa Lyon
    """

    name = "insa_lyon_courses"
    custom_settings = {
        "FEED_URI": Path(f"{CRAWLING_OUTPUT_FOLDER}")
        .joinpath(f"insa_lyon_courses_{YEAR}.json")
        .as_uri()
    }

    def start_requests(self):
        programs = pd.read_json(open(PROG_DATA_PATH, "r"))

        for index, program in programs.iterrows():
            program_id = program["id"]
            courses_urls = program["courses_urls"]
            for course_url in courses_urls:
                course_id_prefix = (
                    program_id + "-" + "-".join(course_url.split("/")[-3:])
                )
                yield scrapy.Request(
                    BASE_URL + course_url,
                    self.parse_main,
                    cb_kwargs={
                        "program_id": program_id,
                        "course_id_prefix": course_id_prefix,
                    },
                )

    def parse_main(self, response, program_id, course_id_prefix):
        courses = response.xpath("//table[@class='detail-parcours-table']")
        for course in courses.xpath(".//a"):
            pdf_link = course.xpath("@href").get()
            # on récupère les params de l'url
            q = dict(parse_qsl(urlparse(pdf_link).query))
            # pour obtenir l'id du cours
            course_id = course_id_prefix + "|" + q.get("id")
            name = course.xpath("text()").get()
            yield scrapy.Request(
                pdf_link,
                self.parse_course,
                cb_kwargs={
                    "program_id": program_id,
                    "course_id": course_id,
                    "name": name,
                },
            )

    @staticmethod
    def parse_course(response, program_id, course_id, name):
        print(name)
        s = SimpleTextExtraction()
        pdfdoc = PDF.loads(io.BytesIO(response.body), [s])
        text = s.get_text_for_page(0)
        parsed_text = parse_pdf_text(text)
        pdf_id = detect(parsed_text, ["IDENTIFICATION"])
        goal = detect(parsed_text, ["OBJECTIFS", "ENSEIGNEMENT"])
        program_content = detect(parsed_text, ["PROGRAMME"])
        teachers = detect(parsed_text, ["CONTACT"])
        duration = detect(parsed_text, ["HORAIRES"])

        yield {
            "id": course_id,
            "program_id": program_id,
            "pdf_id": pdf_id,
            "name": name,
            "year": f"{YEAR}",
            "teachers": teachers,
            "url": response.url,
            "goal": goal,
            "program_content": program_content,
            "duration": duration,
        }


"""
Utils
"""


def parse_pdf_text(text):
    split_text = text.split("\n")
    parsed_text = {}
    key = split_text.pop(0)
    for elt in split_text:
        if re.match("^[A-ZÉ' ]+$", elt):
            key = elt
        else:
            if key in parsed_text:
                parsed_text[key] += " " + elt
            else:
                parsed_text[key] = elt
    return parsed_text


def detect(parsed_text, keywords):
    for k in parsed_text.keys():
        if all(keyword in k for keyword in keywords):
            return parsed_text[k]
    return None
