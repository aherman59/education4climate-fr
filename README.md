# education4climate-fr
Tool for crawling and analysis data from french higher education schools

This repository is inspired by the Shifters Belgium work. You found the initial project at : https://github.com/Education4Climate/Education4Climate


## Start

```
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Crawl

### Usage

To run a spider from the directory *src/crawl/french_schools/spiders* : 

```
cd src/crawl
scrapy crawl NAME_OF_SPIDER
```

###  Example for a school

```
scrapy crawl insa_lyon_programs
```

The output file will be *data/crawling-output/insa_lyon_programs_2021.json*

```
scrapy crawl insa_lyon_courses
```

The output file will be *data/crawling-output/insa_lyon_courses_2021.json*

### Crawl Settings

You can adapt settings in *src/crawl/french_schools/settings.py*

## Score

### Scoring for courses

```
cd src/score
python courses.py --school SCHOOL --year YEAR
```

Output files will be *data\scoring-output\SCHOOL_courses_scoring_YEAR.csv* and *data\scoring-output\SCHOOL_matches_YEAR.json*

### Scoring for programs

```
cd src/score
python programs.py --school SCHOOL --year YEAR
```

The output file will be *data\scoring-output\SCHOOL_programs_scoring_YEAR.csv*

