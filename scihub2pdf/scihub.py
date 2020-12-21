# from __future__ import unicode_literals, print_function, absolute_import

import sys
from base64 import b64decode as b64d

import requests
from PIL import Image
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from six import string_types

from tool import norm_url, download_pdf

try:
    from StringIO import StringIO
    from io import BytesIO
except ImportError:
    from io import StringIO, BytesIO

import tool
import config
import logging

logger = logging.getLogger(__name__)


class SciHub(object):
    def __init__(self,
                 headers,
                 ):

        self.driver_path = config.driver_path
        self.location = config.location

        self.xpath_captcha = config.xpath_captcha
        self.xpath_input = config.xpath_input
        self.xpath_form = config.xpath_form
        self.xpath_pdf = config.xpath_pdf
        self.domain_scihub = config.domain_scihub

        self.headers = headers
        self.driver = None
        self.sci_url = None
        self.el_captcha = None
        self.el_iframe = None
        self.el_form = None
        self.el_input_text = None
        self.has_captcha = False
        self.has_iframe = False
        self.pdf_url = None
        self.doi = None
        self.pdf_file = None
        self.s = None

    def start(self):
        try:
            self.s = requests.Session()
            self.driver = webdriver.PhantomJS()
            # driver_path = "C:\\Portable\\chromedriver_win32\\chromedriver.exe"
            # for windows
            # self.driver = tool.get_driver(self.driver_path)
        except Exception as e:
            logger.error("get driver error")
            logger.exception(e)
            sys.exit(1)

    def exit(self):
        if self.driver is not None:
            logger.info("close and quit driver")
            self.driver.close()
            self.driver.quit()

    def get_session(self):
        cookies = self.driver.get_cookies()
        for cookie in cookies:
            self.s.cookies.set(cookie['name'], cookie['value'])

        return self.s

    def download(self):
        found, r = download_pdf(
            self.s,
            self.pdf_file,
            self.pdf_url,
            self.headers)

        if not found:
            self.driver.save_screenshot(self.pdf_file + ".png")

        return found, r

    def navigate_to(self, doi, pdf_file):
        self.doi = doi
        self.pdf_file = pdf_file
        self.sci_url = self.domain_scihub + doi
        logger.info("DOI: %s", doi)
        logger.info("Sci-Hub Link: %s", self.sci_url)
        logger.info("pdf_file: %s", pdf_file)
        r = requests.get(self.sci_url)
        found = r.status_code == 200
        if found:
            self.driver.get(self.sci_url)
            self.driver.set_window_size(1120, 550)
        else:
            logger.error("status_code: %s, something is wrong with sci-hub", r.status_code)
        return found, r

    def get_captcha_img(self):
        self.driver.execute_script("document.getElementById('content').style.zIndex = 9999;")
        self.driver.switch_to.frame(self.el_iframe)
        self.driver.execute_script("document.getElementById('captcha').style.zIndex = 9999;")
        location = self.el_captcha.location
        size = self.el_captcha.size
        captcha_screenshot = self.driver.get_screenshot_as_base64()
        image_b64d = b64d(captcha_screenshot)
        if isinstance(image_b64d, string_types):
            image = Image.open(StringIO(image_b64d))
        else:
            image = Image.open(BytesIO(image_b64d))

        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        image = image.crop((left, top, right, bottom))
        self.driver.switch_to.default_content()
        return image

    def solve_captcha(self, captcha_text):

        # self.driver.save_screenshot(self.pdf_file+"before_solve.png")
        self.driver.switch_to.frame(self.el_iframe)
        self.el_input_text.send_keys(captcha_text)
        # self.driver.save_screenshot(self.pdf_file+"send_keys.png")
        self.el_form.submit()

        self.driver.switch_to.default_content()
        # with self.wait_for_page_load(timeout=10):
        found, r = self.navigate_to(self.doi, self.pdf_file)
        # self.driver.save_screenshot(self.pdf_file+"after_submit.png")
        return self.check_captcha()

    def get_iframe(self):
        self.driver.get(self.sci_url)
        # frame = self.driver.find_element_by_tag_name("iframe")
        # self.driver.switch_to.frame(frame)
        # find = self.driver.find_element_by_xpath('//*[@id="pdf"]')
        self.has_iframe, self.el_iframe = self.get_el(self.xpath_pdf)
        if self.has_iframe:
            self.pdf_url = norm_url(self.el_iframe.get_attribute("src"))
        else:
            self.driver.save_screenshot(self.pdf_file + ".png")

        return self.has_iframe

    def get_el(self, xpath):
        try:
            el = self.driver.find_element_by_xpath(
                xpath
            )
            found = True
        except NoSuchElementException:
            el = None
            found = False

        return found, el

    def check_captcha(self):
        logger.info("checking if has captcha...")
        has_iframe = self.get_iframe()
        if has_iframe is False:
            logger.info("Current url: %s" % self.driver)
            logger.error("No pdf found. Maybe, the sci-hub dosen't have the file. "
                         "Please try to open the link in your browser.")
            return False, has_iframe

        # self.driver.save_screenshot(self.pdf_file+"check_captcha.png")
        self.driver.switch_to.frame(self.el_iframe)
        self.has_captcha, self.el_captcha = self.get_el(self.xpath_captcha)
        if self.has_captcha:
            found, self.el_input_text = self.get_el(self.xpath_input)
            found, self.el_form = self.get_el(self.xpath_form)

        self.driver.switch_to.default_content()

        return self.has_captcha, has_iframe
