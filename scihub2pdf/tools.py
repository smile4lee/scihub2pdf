from __future__ import unicode_literals, print_function, absolute_import
from selenium import webdriver

import glob
import os
import shutil


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
        print("\tDownload: ok")
    else:
        print("\tDownload: Fail")
        print("\tStatus_code: ", r.status_code)
    return found, r


def norm_url(url):
    if url.startswith("//"):
        url = "http:" + url

    return url


def getDriver(driver_path, download_dir='./'):
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
    print("latest_file: %s" % latest_file)
    # os.rename(latest_file, os.path.join(dir, title + ".pdf"))
    shutil.move(latest_file, os.path.join(dir, title + ".pdf"))
    print("rename finished with dir: %s" % dir)
    print("rename finished with title: %s" % title)
