#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import unicode_literals, print_function, absolute_import

import argparse
import io
import logging
import re
import sys
import textwrap

import bibtexparser

import config
import download
import yml_logging

yml_logging.setup_logging()
logger = logging.getLogger("scihub2pdf")

py_version = sys.version_info[0]


def main():
    parser = argparse.ArgumentParser(
        prog="scihub2pdf",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        SciHub to PDF
        ----------------------------------------------------
        Downloads pdfs via a DOI number, article title
        or a bibtex file, using the database of libgen(sci-hub).

        Given a bibtex file

        $ scihub2pdf -i input.bib

        Given a DOI number...

        $ scihub2pdf 10.1038/s41524-017-0032-0

        Given a title...

        $ scihub2pdf --title An useful paper

        Arxiv...

        $ scihub2pdf arxiv:0901.2686

        $ scihub2pdf --title arxiv:Periodic table for topological insulators

        ## Download from list of items

        Given a text file like

        ```
        10.1038/s41524-017-0032-0
        10.1063/1.3149495
        .....
        ```
        download all pdf's
        ```
        $ scihub2pdf -i dois.txt --txt
        ```
        Given a text file like

        ```
        Some Title 1
        Some Title 2
        .....
        ```
        download all pdf's
        ```
        $ scihub2pdf -i titles.conf --txt --title
        ```
        Given a text file like

        ```
        arXiv:1708.06891
        arXiv:1708.06071
        arXiv:1708.05948
        .....
        ```
        download all pdf's
        ```
        $ scihub2pdf -i arxiv_ids.txt --txt
        ```
       -----------------------------------------------------
            @author: Bruno Messias
            @email: messias.physics@gmail.com
            @telegram: @brunomessias
            @github: https://github.com/bibcure/sci2pdf
        ''')
    )
    parser.add_argument(
        "--input", "-i",
        dest="inputfile",
        help="bibtex input file"
    )
    parser.add_argument(
        "--title", "-t",
        dest="title",
        action="store_true",
        help="download from title"
    )
    parser.add_argument(
        "--uselibgen",
        dest="uselibgen",
        action="store_true",
        help="Use libgen.io instead sci-hub."
    )
    parser.add_argument(
        "--location", "-l",
        help="folder, ex: -l 'folder/'"
    )
    parser.add_argument(
        "--txt",
        action="store_true",
        help="Just create a file with DOI's or titles"
    )

    parser.set_defaults(title=False)
    parser.set_defaults(uselibgen=False)
    parser.set_defaults(txt=False)
    parser.set_defaults(location=config.location)

    args = parser.parse_known_args()
    title_search = args[0].title
    is_txt = args[0].txt
    use_libgen = args[0].uselibgen
    inline_search = len(args[1]) > 0
    location = args[0].location

    if use_libgen:
        download.start_libgen()
        logger.info("Using Libgen.")
    else:
        download.start_scihub()
        logger.info("Using Sci-Hub.")

    download.start_arxiv()

    if inline_search:
        # values = [c if pyversion == 3 else c.decode(sys.stdout.encoding) for c in args[1]]
        values = [c if py_version == 3 else c.decode(sys.stdout.encoding) for c in args[1]]
        value = " ".join(values)
        is_arxiv = bool(re.match("arxiv:", value, re.I))
        if is_arxiv:
            field = "ti" if title_search else "id"
            download.download_from_arxiv(value, location, field)
        elif title_search:
            download.download_from_title(value, location, use_libgen)
        else:
            download.download_from_doi(value, location, use_libgen)
    else:
        if is_txt:
            with io.open(args[0].inputfile, "r", encoding="utf-8") as inputfile:
                file_values = inputfile.read()

            file_arr_ini = file_values.split("\n")

            file_arr = list(filter(lambda x: x != "", file_arr_ini))
            size = len(file_arr)
            i = 0
            for value in file_arr:
                is_arxiv = bool(re.match("arxiv:", value, re.I))
                try:
                    if value != "":
                        i += 1
                        logger.info("{}/{}: {}".format(i, size, value))
                        if is_arxiv:
                            field = "ti" if title_search else "id"
                            download.download_from_arxiv(value, field, location)
                        elif title_search:
                            download.download_from_title(value, location, use_libgen)
                        else:
                            download.download_from_doi(value, location, use_libgen)
                except Exception as e:
                    logger.error("----- error -----: %s", value)
                    logger.error(e)
        else:
            dict_parser = {
                'keywords': 'keyword',
                'keyw': 'keyword',
                'subjects': 'subject',
                'urls': 'url',
                'link': 'url',
                'links': 'url',
                'editors': 'editor',
                'authors': 'author'}
            parser = bibtexparser.bparser.BibTexParser()
            parser.alt_dict = dict_parser
            with io.open(args[0].inputfile, "r", encoding="utf-8") as inputfile:
                refs_string = inputfile.read()

            bibtex = bibtexparser.loads(refs_string,
                                        parser=parser)
            bibs = bibtex.entries
            if len(bibs) == 0:
                logger.error("Input File is empty or corrupted.")
                raise Exception("Input File is empty or corrupted.")
            else:
                download.download_pdf_from_bibs(bibs, location, use_libgen)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("error")
        logger.exception(e)
    finally:
        download.exit()

    sys.exit(0)
