########################################################################
##  SETTINGS FOR THE PROJECT
########################################################################

from pathlib import Path

ACCEPTED_LANGUAGES = ["fr"]

CRAWLING_OUTPUT_FOLDER = Path(__file__).parent.parent.parent.joinpath(
    "data", "crawling-output"
)
SCORING_OUTPUT_FOLDER = Path(__file__).parent.parent.parent.joinpath(
    "data", "scoring-output"
)
