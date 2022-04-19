import re
import tempfile
from abc import ABC
from typing import Tuple, Optional

import scrapy
from pdfminer.high_level import extract_text
from scrapy import Selector
from scrapy.utils.project import get_project_settings

from crawl.french_schools.items import ProgramItem, TeachingUnit, CourseItem, Status, Teacher


settings = get_project_settings()
CRAWLING_OUTPUT_FOLDER = settings.get("CRAWLING_OUTPUT_FOLDER")
YEAR = settings.get("YEAR")

BASE_URL_PROGRAM = "https://www.insa-rennes.fr/{0}.html"
BASE_URL_COURSE = "https://applisjava.insa-rennes.fr{0}"


CURSUS_CODE = {
    "filiere-classique-stpi": "Filière classique / années 1 & 2",
    "EII": "Électronique et Informatique Industrielle",
    "MA": "Mathématiques Appliquées",
    "INFO": "Informatique",
    "ET": "Électronique et Télécommunications",
    "CDTI": "Électronique - Conception et Développement de Technologies Innovantes - APPRENTISSAGE",
    "GCU": "Génie Civil et Urbain",
    "GMA": "Génie Mécanique et Automatique - possibilité apprentissage",
    "GPM": "Génie Physique et Matériaux",
}


class InsaRennesSpider(scrapy.Spider, ABC):
    """
    Crawler for Insa Rennes - programs and courses
    """

    name = "insa_rennes"
    custom_settings = {
        "ITEM_PIPELINES": {
            'src.crawl.french_schools.pipelines.CoursePipeline': 100,
            'src.crawl.french_schools.pipelines.ProgramPipeline': 200,
        }
    }

    def start_requests(self):
        for cursus_id, cursus_name in CURSUS_CODE.items():
            url = BASE_URL_PROGRAM.format(cursus_id.lower())
            yield scrapy.Request(
                url,
                self.parse_main,
                cb_kwargs={"cursus_id": cursus_id},
            )

    def parse_main(self, response, cursus_id):
        program = response.xpath(f"//a[contains(@href, 'applisjava.insa-rennes.fr/OffreFormationWeb/main?action=RECHERCHE_MAQUETTE')]")
        if len(program) != 1:
            raise ValueError(f'No program found for cursus {cursus_id}')
        yield scrapy.Request(
            program.xpath("@href").get(),
            self.parse_program,
            cb_kwargs={"cursus_id": cursus_id},
        )

    @staticmethod
    def parse_program(response, cursus_id):
        program = ProgramItem(
            id=cursus_id,
            name=CURSUS_CODE[cursus_id],
            cycles=[],
            url=response.url,
            teaching_units=[],
            ects=0,
        )
        semester_and_spes = response.xpath("//h3[not(contains(@role, 'heading'))]/text()[1]")
        nb_previous_tu = 0
        for i in range(len(semester_and_spes)):
            semester, spe = InsaRennesSpider.parse_semester_and_spe(
                semester_and_spes[i].get().strip()
            )
            teaching_units = response.xpath(f"//h4[count(preceding-sibling::h3)={i+1}]/text()[1]")
            for j in range(len(teaching_units)):
                id, name, ects = InsaRennesSpider.parse_raw_tu_title(
                    teaching_units[j].get().strip()
                )
                teaching_unit = TeachingUnit(
                    id, name, ects, [], semester
                )
                courses = response.xpath(f"//ul[count(preceding-sibling::h4)={nb_previous_tu + 1}]/li")
                for c in courses:
                    course_item = InsaRennesSpider.parse_course(c)
                    teaching_unit.courses.append(course_item.id)
                    yield scrapy.Request(
                        course_item.url,
                        InsaRennesSpider.parse_course_pdf,
                        cb_kwargs={'course_item': course_item}
                    )

                program.teaching_units.append(teaching_unit)
                program.ects += teaching_unit.ects
                nb_previous_tu += 1

        yield program

    @staticmethod
    def parse_course(course_selector: Selector) -> CourseItem:
        raw_title = course_selector.xpath("./text()[1]").get().strip()
        url = BASE_URL_COURSE.format(
            course_selector.xpath("./a[1]").attrib['href']
        )
        id, name, ects, status = \
            InsaRennesSpider.parse_raw_course_title(raw_title)

        return CourseItem(
            id=id,
            name=name,
            url=url,
            cycles=[],
            languages=[],
            teachers=[],
            goal='',
            content='',
            additional_info=None,
            hours=None,
            status=status,
            ects=ects,
        )

    @staticmethod
    def parse_semester_and_spe(raw_title: str) -> Tuple[int, str]:
        try:
            semester, spe = raw_title.split(' - ', 1)
            return int(semester.split()[1]), spe.strip()
        except ValueError:
            print(f'Not able to parse semester and spe: {raw_title}')

    @staticmethod
    def parse_raw_tu_title(raw_title: str) -> Tuple[str, str, float]:
        m = re.search(
            '([a-zA-Z0-9\-\s]*)\s-\s(.*)\s\(\s*([0-9]+\.[0-9][0-9])\sects\)',
            raw_title,
        )
        try:
            return (
                m.group(1).strip(),
                m.group(2).strip(),
                float(m.group(3)),
            )
        except ValueError:
            print(f'Not able to parse teaching unit raw title: {raw_title}')

    @staticmethod
    def parse_raw_course_title(raw_title: str) -> Tuple[str, str, float, Status]:
        m = re.search(
            '([a-zA-Z0-9\-\s]*)\s-\s(.*)\s\(([A-Z])\s-\s+([0-9]+\.[0-9][0-9])\sects\)',
            raw_title,
        )
        try:
            return (
                m.group(1).strip(),
                m.group(2).strip(),
                float(m.group(4)),
                InsaRennesSpider.get_status(m.group(3)),
            )
        except ValueError:
            print(f'Not able to parse course raw title: {raw_title}')

    @staticmethod
    def get_status(raw_info: str) -> Optional[Status]:
        if raw_info.strip() == 'O':
            return Status.MANDATORY
        elif raw_info.strip() == 'C':
            return Status.SPECIALISATION
        elif raw_info.strip() == 'F':
            return Status.OPTIONAL
        else:
            return None

    @staticmethod
    def parse_course_pdf(response, course_item: CourseItem):
        f = tempfile.NamedTemporaryFile(suffix='.pdf', delete=True)
        f.write(response.body)
        text = extract_text(f.name)

        regex = re.search(
            'Volume horaire total : ([0-9]+.[0-9]{2})[\s\S]*' +
            'Responsable\(s\) :([a-zA-ZÀ-ÿ\- ]*)[\s\S]*' +
            'Objectifs, finalités :([\s\S]*)' +
            'Contenu :([\s\S]*)' +
            '(Bibliographie :[\s\S]*)[0-9]{2}/[0-9]{2}/[0-9]{4}',
            text,
        )
        try:
            hours = regex.group(1)
            course_item.hours = hours
            raw_teacher = regex.group(2)
            course_item.teachers = [Teacher(raw_teacher.strip())]
            goal = regex.group(3)
            course_item.goal = goal
            content = regex.group(4)
            course_item.content = content
            additional_info = regex.group(5)
            course_item.additional_info = additional_info

            yield course_item

        except ValueError:
            print(f'Not able to find elements in pdf: {response.url}')
