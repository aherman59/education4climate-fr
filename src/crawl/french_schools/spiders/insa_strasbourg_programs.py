import re

from abc import ABC
from pathlib import Path

import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "http://www.insa-strasbourg.fr/fr/programme-des-etudes/"
PROGRAM_URL = "http://www.insa-strasbourg.fr/fr/programmes-des-etudes/{}/{}"

remove_spaces = re.compile('\s+')
titre = re.compile('>(.*)<')

class InsaStrasbourgSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Insa Strasbourg
    """

    name = 'INSAStrasbourg-programs'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}insa_strasbourg_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(
            url=BASE_URL,
            callback=self.parse_main
        )

    def parse_main(self, response):

        links = response.xpath("//article//li|//article//h2|//article//strong").getall()
        nom_formation = ""
        programs = []
        for link in links:
            if link[:4] in ['<h2>', '<str']:
                find = titre.search(link)
                if find is not None:
                    nom_formation = find.groups()[0]
                else:
                    a =0
            if 'contenu' in link:
                if link.find('–') >= 0:
                    programs.append((nom_formation, link[link.find('–')+2:link.find(':')-1]))
                else:
                    programs.append((nom_formation, link[4:link.find(':') - 1]))
        #program_ids = [link[link.find('–')+2:link.find(':')-1] if '–' in link else link[4:link.find(':')-1]
        #               for link in links if 'contenu' in link]
        links = response.xpath("//article//li//a[contains(text(), 'contenu')]").getall()
        links = [link[9:link[9:].find('"')+9] for link in links]
        for program, link in zip(programs, links):
            yield scrapy.Request(url=link,
                                 callback=self.parse_program,
                                 cb_kwargs={'program_id': program[1],
                                            'nom_formation': program[0]})

    @staticmethod
    def parse_program(response, program_id, nom_formation):

        courses = [(course.attrib['title'], PROGRAM_URL.format(program_id, course.attrib['href'])) for course in response.xpath("//a[@title]")]

        poids = [remove_spaces.sub("", p.root.text) for p in response.xpath('//a[@title]/parent::td/following-sibling::td')]
        heures = poids[0::2]
        ECTS = poids[1::2]
        courses = courses[-len(heures):]
        yield {
            "formation": nom_formation,
            "id": program_id,
            "name": program_id,
            "url": response.url,
            "courses": courses,
            "heures": heures,
            "ETCS": ECTS
        }
