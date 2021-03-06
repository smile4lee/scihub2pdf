# from __future__ import unicode_literals, print_function, absolute_import

import logging

import requests
from lxml import html
from lxml.etree import ParserError

from tool import norm_url, download_pdf

logger = logging.getLogger("scihub")


class LibGen(object):
    def __init__(self,
                 headers={},
                 libgen_url="http://libgen.io/scimag/ads.php",
                 xpath_pdf_url="/html/body/table/tr/td[3]/a"):

        self.libgen_url = libgen_url
        self.xpath_pdf_url = xpath_pdf_url
        self.headers = headers
        self.s = None
        self.doi = None
        self.pdf_file = None
        self.pdf_url = None
        self.page_url = None
        self.html_tree = None
        self.html_content = None

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
            self.headers,
            filetype="application/octet-stream")

        return found, r

    def navigate_to(self, doi, pdf_file):

        params = {"doi": doi, "downloadname": ""}
        r = self.s.get(
            self.libgen_url,
            params=params,
            headers=self.headers
        )
        self.page_url = r.url
        self.pdf_file = pdf_file
        logger.info("DOI: %s, LibGen Link: %s", doi, self.page_url)
        found = r.status_code == 200
        if not found:
            logger.error("Maybe libgen is down. Try to use sci-hub instead.")
            return found, r

        self.html_content = r.content
        return found, r

    def generate_tree(self):

        try:
            self.html_tree = html.fromstring(self.html_content)
            success = True
        except ParserError:
            logger.error("The LibGen page has a strange behaviour. Please try open in browser to check: %s",
                         self.page_url)
            success = False

        return success, self.html_tree

    def get_pdf_url(self):
        html_a = self.html_tree.xpath(self.xpath_pdf_url)
        if len(html_a) == 0:
            logger.error("PDF link for not found: %s", self.page_url)
            found = False
            self.pdf_url = None
        else:
            self.pdf_url = norm_url(html_a[0].attrib["href"])
            found = True

        return found, self.pdf_url
