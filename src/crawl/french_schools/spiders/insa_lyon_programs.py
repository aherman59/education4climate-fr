# -*- coding: utf-8 -*-
from pathlib import Path
from urllib.parse import urlparse, parse_qsl
from lxml import etree
from abc import ABC

import requests
import scrapy
from scrapy.utils.project import get_project_settings

settings = get_project_settings()
CRAWLING_OUTPUT_FOLDER = settings.get("CRAWLING_OUTPUT_FOLDER")
YEAR = settings.get("YEAR")

BASE_URL = "https://www.insa-lyon.fr"
CURSUS_URL = BASE_URL + "/fr/formation/diplomes/{0}"

CURSUS_CODE = {
    "ARCHI": "CP architecte-ingénieur",
    "DE": "Diplome d'Etablissement",
    "ECH": "Echange",
    "HUMAS": "Gestion Centre des Humanités",
    "ING": "Ingénieur",
    "M": "Master",
    "MS": "Mastère Spécialisé",
}


class InsaLyonProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Insa Lyon
    """

    name = "insa_lyon_programs"
    custom_settings = {
        "FEED_URI": Path(f"{CRAWLING_OUTPUT_FOLDER}")
        .joinpath(f"insa_lyon_programs_{YEAR}.json")
        .as_uri()
    }

    def start_requests(self):
        for cursus_id, cursus_name in CURSUS_CODE.items():
            url = CURSUS_URL.format(cursus_id)
            yield scrapy.Request(
                url,
                self.parse_main,
                cb_kwargs={"cursus_id": cursus_id},
            )

    def parse_main(self, response, cursus_id):
        programs = response.xpath("//div[@class='diplome']")
        print(programs)
        for program in programs:
            program_id = program.xpath("@id").get()
            name = program.xpath(".//h3//a/text()").get()
            courses_urls = self.get_courses_urls(program)
            parcours = {}
            for parcours_name, url in courses_urls:
                parcours_number = self.get_parcours_number(url)
                if parcours_number in parcours.keys():
                    parcours[parcours_number]["courses_url"] += [url]
                    parcours[parcours_number]["courses"] += self.get_courses_id(
                        BASE_URL + url, program_id
                    )
                else:
                    parcours[parcours_number] = {
                        "name": name + " - " + parcours_name,
                        "cursus_id": cursus_id,
                        "program_id": program_id,
                        "id": program_id + "-" + str(parcours_number),
                        "url": response.url,
                        "courses_url": [url],
                        "courses": self.get_courses_id(BASE_URL + url, program_id),
                    }
            for num, parc in parcours.items():
                yield parc

    def get_courses_urls(self, program):
        """Return urls for access courses details"""
        courses_link = program.xpath(".//div[@class='contenu']//a")
        courses_urls = []
        for c in courses_link:
            url = c.xpath("@href").get()
            parcours_name = c.xpath("text()").get()
            courses_urls.append(
                (
                    parcours_name,
                    url,
                )
            )
        return courses_urls

    def get_parcours_number(self, url):
        """detect number of a parcours in the url"""
        return int(url.split("/")[4])

    def get_courses_id(self, url, program_id):
        """read the courses url build courses ids"""
        response = etree.HTML(requests.get(url).text)
        courses = response.xpath("//table[@class='detail-parcours-table']")
        links = []
        for course in courses:
            pdf_links = course.xpath(".//a/@href")
            if pdf_links:
                links += pdf_links
        ids = []
        for link in links:
            q = dict(parse_qsl(urlparse(link).query))
            id = q.get("id")
            if id:
                ids.append(id)
        return [
            program_id + "-" + "-".join(url.split("/")[-3:]) + "|" + course_id
            for course_id in ids
        ]
