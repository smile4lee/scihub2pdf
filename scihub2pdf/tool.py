# from __future__ import unicode_literals, print_function, absolute_import
from selenium import webdriver

import glob
import os
import shutil
import logging

logger = logging.getLogger("scihub")


def download_pdf(s, pdf_file, pdf_url, headers, filetype="application/pdf"):
    r = s.get(
        pdf_url,
        headers=headers
    )
    found = r.status_code == 200
    is_right_type = r.headers["content-type"] == filetype

    if found and is_right_type:
        pdf = open(pdf_file, "wb")
        pdf.write(r.content)
        pdf.close()
        logger.info("Download: ok")
    else:
        logger.error("Download: Fail. status_code: %s, pdf_url: %s", r.status_code, pdf_url)
        logger.error("Download: Fail. pdf_file: %s", pdf_file)
    return found, r


def norm_url(url):
    if url.startswith("//"):
        url = "http:" + url
    return url


def get_driver(driver_path, download_dir='./'):
    # Disable Chrome's PDF Viewer
    profile = {"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
               "download.default_directory": download_dir, "download.extensions_to_open": "applications/pdf"}

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_experimental_option("prefs", profile)
    # Optional argument, if not specified will search path.
    driver = webdriver.Chrome(driver_path, chrome_options=options)

    return driver


def rename_latest_file(dir, title, extension="/*.pdf"):
    # * means all if need specific format then *.csv
    list_of_files = glob.glob(dir + extension)
    latest_file = max(list_of_files, key=os.path.getctime)
    logger.info("latest_file: %s" % latest_file)
    # os.rename(latest_file, os.path.join(dir, title + ".pdf"))
    shutil.move(latest_file, os.path.join(dir, title + ".pdf"))
    logger.info("rename finished with dir: %s, title: %s", dir,  title)
