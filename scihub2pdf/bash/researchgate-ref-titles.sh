#!/usr/bin/env bash
# get references titles in an article by the given article's references url on researchgate.
#
# "--url", "-u", "article's references url on researchgate"
# "--filepath", "-f", "titles will be save in the file"

cd ..
python researchgate.py -u "https://researchgate.net/publication/312483664_National-scale_soybean_mapping_and_area_estimation_in_the_United_States_using_medium_resolution_satellite_imagery_and_field_survey/references" -f "input/titles-researchgate.txt"