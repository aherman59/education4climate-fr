# -*- coding: utf-8 -*-
from pathlib import Path

import scrapy
from abc import ABC

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://www.insa-toulouse.fr/fr/formation/ingenieur/offre-de-formation-ects/sciences-technologies-sante-STS/formation-d-ingenieur-FI/{0}"


CURSUS_CODE = {
    "ingenieur-insa-de-toulouse-annees-1-2-et-3-IUDT2UV2.html": "INGENIEUR INSA DE TOULOUSE ANNEES 1, 2 et 3",
    "ingenieur-specialite-automatique-electronique-IUDWX3YG.html": "INGENIEUR spécialité AUTOMATIQUE, ELECTRONIQUE",
    "ingenieur-specialite-genie-biologique-IUDWUH8V.html": "INGENIEUR spécialité GENIE BIOLOGIQUE",
    "ingenieur-specialite-genie-civil-IUDX2KTY.html": "INGENIEUR spécialité GENIE CIVIL",
    "ingenieur-specialite-genie-des-procedes-et-environnement-IUDXH274.html": "INGENIEUR spécialité GENIE DES PROCEDES ET ENVIRONNEMENT",
    "ingenieur-specialite-genie-mecanique-IUDX5IS1.html": "INGENIEUR spécialité GENIE MECANIQUE",
    "ingenieur-specialite-genie-physique-IUDX8CMI.html": "INGENIEUR spécialité GENIE PHYSIQUE",
    "ingenieur-specialite-informatique-et-reseaux-IUDXBO80.html": "INGENIEUR spécialité INFORMATIQUE ET RESEAUX",
    "ingenieur-specialite-mathematiques-appliquees-IUDXEJLC.html": "INGENIEUR spécialité MATHEMATIQUES APPLIQUEES"
}


class InsaToulouseProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Insa Toulouse
    """

    name = "insa-toulouse-programs"
    custom_settings = {
        "FEED_URI": Path(__file__)
        .parent.absolute()
        .joinpath(f"../../../../{CRAWLING_OUTPUT_FOLDER}insa_toulouse_programs_{YEAR}.json")
        .as_uri()
    }

    def start_requests(self):
        for cursus_id, cursus_name in CURSUS_CODE.items():
            url = BASE_URL.format(cursus_id)
            yield scrapy.Request(
                url,
                self.parse_main,
                cb_kwargs={"cursus_id": cursus_id},
            )

    @staticmethod
    def parse_main(response, cursus_id):
        programs = response.xpath("//div[@class='program-details']")

        courses_names = programs.xpath(".//a//text()").getall()
        courses_urls = programs.xpath(".//a/@href").getall()
        courses_ids = [c.split('/')[-1].split('.html')[0] for c in courses_urls]
        yield {
            "id": cursus_id,
            "courses": courses_ids,
            "courses_names": courses_names,
            "program_url": response.url,
            "courses_urls": courses_urls,
        }
