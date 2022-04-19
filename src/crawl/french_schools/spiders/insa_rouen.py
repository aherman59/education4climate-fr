# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy
from scrapy.utils.project import get_project_settings

from crawl.french_schools.items import ProgramItem, TeachingUnit, CourseItem, Teacher


settings = get_project_settings()
CRAWLING_OUTPUT_FOLDER = settings.get("CRAWLING_OUTPUT_FOLDER")
YEAR = settings.get("YEAR")

BASE_URL = "https://www.insa-rouen.fr{0}"


class InsaRouenProgramSpider(scrapy.Spider, ABC):
    """
    Crawler for Insa Rouen - programs and courses
    """

    name = "insa_rouen"

    custom_settings = {
        "ITEM_PIPELINES": {
            'src.crawl.french_schools.pipelines.CoursePipeline': 100,
            'src.crawl.french_schools.pipelines.ProgramPipeline': 200,
        }
    }

    def start_requests(self):
        yield scrapy.Request(
            BASE_URL.format('/formation/specialites-ingenieurses'),
            self.parse_main,
        )
        yield scrapy.Request(
            BASE_URL.format('/formation/premier-cycle-ingenieur/programme-de-la-specialite'),
            self.parse_program,
            cb_kwargs={
                'program_name': 'Premier cycle ingénieur',
                'program_page_url': BASE_URL.format(
                    '/formation/premier-cycle-ingenieur/programme-de-la-specialite'
                ),
            },
        )

    def parse_main(self, response):
        education_menu = response.xpath(f"//ul[@id='accordion']")
        programs = education_menu.xpath(
            f"//a[@href='/formation/specialites-ingenieurses' and @role='button']/following-sibling::ul/li/a"
        )
        for i, p in enumerate(programs):
            yield scrapy.Request(
                BASE_URL.format(p.attrib['href']),
                self.parse_speciality,
                cb_kwargs={
                    'program_name': p.xpath('text()').get().strip(),
                    'program_page_url': BASE_URL.format(p.attrib['href']),
                },
            )

    def parse_speciality(self, response, program_name, program_page_url):
        program = response.xpath(
            f"//a[@href='/formation/specialites-ingenieurses' and @role='button']/following-sibling::ul/li[contains(@class, 'lvl-3')]/a"
        )
        if 'href' in program.attrib and '/formation/specialites-ingenieurses' in program.attrib['href']:
            yield scrapy.Request(
                BASE_URL.format(program.attrib['href']),
                self.parse_program,
                cb_kwargs={
                    'program_name': program_name,
                    'program_page_url': program_page_url,
                },
            )
        else:
            print(program.get())

    def parse_program(self, response, program_name, program_page_url):
        semesters = response.xpath('//h3')
        teaching_units = []
        for s in semesters:
            semester = int(s.xpath('text()').get().split()[1])
            tus = s.xpath(f'following-sibling::table[1]/tr[not(@id)]')
            for tu in tus:
                courses = self.parse_courses(
                    response,
                    tu.xpath(f'td[1]/a').attrib['href'][1:]
                )
                raw_ects = tu.xpath(f'td[3]/text()').get()
                teaching_units.append(TeachingUnit(
                    id=tu.xpath(f'td[2]//text()').get(),
                    name=tu.xpath(f'td[1]/a/text()').get().strip(),
                    ects=int(raw_ects) if raw_ects else None,
                    courses=[c.id for c in courses],
                    semester=semester,
                ))
                for c in courses:
                    yield c

        yield ProgramItem(
            id=program_name,
            name=program_name,
            cycles=['L3', 'M1', 'M2'],
            url=program_page_url,
            teaching_units=teaching_units,
            ects=sum([tu.ects for tu in teaching_units if tu.ects is not None]),
        )

    @staticmethod
    def parse_courses(response, tr_id):
        course_selectors = response.xpath(f'//tr[@id="{tr_id}"]//table/tr')
        courses = []
        for c_selector in course_selectors:
            goal, content, teachers = InsaRouenProgramSpider.parse_course(
                response,
                c_selector.xpath('./td[1]/a[1]').attrib['href'][1:]
            )
            name = c_selector.xpath('./td[1]/a[2]/text()').get()
            cycles = c_selector.xpath('./td[2]//a[contains(@class, "btn-danger")]/span/text()').getall()
            language = c_selector.xpath('./td[4]//a/text()').get()
            id = c_selector.xpath('./td[5]//text()').get()
            hours = c_selector.xpath('./td[6]//text()').get()

            courses.append(
                CourseItem(
                    id,
                    name,
                    '',
                    cycles,
                    [language],
                    teachers,
                    goal,
                    content,
                    hours=int(hours) if hours else None,

                )
            )

        return courses

    @staticmethod
    def parse_course(response, course_description_id):
        course_description = response.xpath(f'//div[@id="{course_description_id}"]')
        goal = ''.join(
            course_description.xpath('.//div[@class="lead"]/p[2]/text()').getall()
        )
        content = ''.join(course_description.xpath('.//dl[@class="dl-horizontal"]/dd[1]//p/text()').getall())
        teacher_selectors = course_description.xpath(
            './/h4[contains(text(), "intervenants")]/' +
            'following-sibling::dl/dd'
        )
        teachers = [
            Teacher(
                t.xpath('./text()').get()[:-3],
                t.xpath('./small//text()').get(),
            ) for t in teacher_selectors
        ]

        return goal, content, teachers
