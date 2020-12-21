# from __future__ import unicode_literals, print_function, absolute_import
import requests
from arxivcheck.arxiv import get_arxiv_pdf_link
from tool import download_pdf

import logging

logger = logging.getLogger("scihub")


class Arxiv(object):
    def __init__(self, headers={}):
        self.headers = headers
        self.s = None
        self.pdf_file = None
        self.pdf_url = None

    def start(self):
        self.s = requests.Session()

    def exit(self):
        if self.s is not None:
            self.s.close()

    def download(self):
        found, r = download_pdf(
            self.s,
            self.pdf_file,
            self.pdf_url,
            self.headers)

        return found, r

    def navigate_to(self, value, pdf_file, field="id"):
        self.pdf_file = pdf_file
        found, self.pdf_url = get_arxiv_pdf_link(value, field)
        logger.info("navigate to, value: %s, link: %s", value, self.pdf_url)
        if not found:
            logger.error("Arxiv not found, value: %s, link: %s", value, self.pdf_url)
        return found, self.pdf_url
