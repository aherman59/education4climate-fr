# -*- coding: utf-8 -*-
from pathlib import Path

import scrapy
from abc import ABC

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://www.insa-toulouse.fr"

class InsaToulouseProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Insa Toulouse
    """

    name = "insa-toulouse-programs"
    custom_settings = {
        "FEED_URI": Path(f"{CRAWLING_OUTPUT_FOLDER}")
        .joinpath(f"insa_toulouse_programs_{YEAR}.json")
        .as_uri()
    }


    def start_requests(self):
        url = BASE_URL + "/fr/formation/ingenieur/offre-de-formation-ects/sciences-technologies-sante-STS/formation-d-ingenieur-FI.html"#.format(cursus_id)
        yield scrapy.Request(
            url,
            self.parse_main,
        )

    def parse_main(self, response):
        # cadre 'Offre de formation"
        offre_de_formation = response.xpath("//div[@class='ametys-cms-service sitemap  wrapper no-title']")
        cursus_names = offre_de_formation.xpath(".//a[@title]/text()").getall()
        cursus_urls = offre_de_formation.xpath(".//a[@title]/@href").getall()

        # on itere sur les liens de chaque cursus pour extraire les noms des cours:
        # pour chaque tuple (cursus_name, cursus_url), on appelle parse_program
        for cursus_name, cursus_url in zip(cursus_names, cursus_urls):
            yield scrapy.Request(url=BASE_URL + cursus_url,
                                 callback=self.parse_cursus,
                                 cb_kwargs={'cursus_name': cursus_name})

    @staticmethod
    def parse_cursus(response, cursus_name):
        # Cadre contenant les liens vers les cours (onglet "Programme")
        program_details = response.xpath("//div[@class='program-details']")
        # liens vers les cours
        # on selectionne les liens HTML uniquement (il existe des liens redondants vers des pdf)
        courses_urls = [x for x in program_details.xpath(".//a//@href").getall() if x[-5:] == '.html']
        # Chaque lien est de la forme
        # /fr/formation/ingenieur/.../ingenierie-et-enjeux-ecologiques-semestre-2-I3CCIE21.html
        # on extrait l'ID placé à la fin juste avant '.html'
        courses_ids = [x.split('.html')[0].split('-')[-1] for x in courses_urls]

        courses_names = program_details.xpath(".//a//text()").getall()

        yield {
            "cursus_name": cursus_name,
            "program_url": response.url,
            "courses_ids": courses_ids,
            "courses_names": courses_names,
            "courses_urls": courses_urls,
        }
