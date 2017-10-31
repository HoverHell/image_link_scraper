========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |coveralls|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/image_link_scraper/badge/?style=flat
    :target: https://readthedocs.org/projects/image_link_scraper
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/HoverHell/image_link_scraper.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/HoverHell/image_link_scraper

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/HoverHell/image_link_scraper?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/HoverHell/image_link_scraper

.. |requires| image:: https://requires.io/github/HoverHell/image_link_scraper/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/HoverHell/image_link_scraper/requirements/?branch=master

.. |coveralls| image:: https://coveralls.io/repos/HoverHell/image_link_scraper/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/HoverHell/image_link_scraper

.. |version| image:: https://img.shields.io/pypi/v/image_link_scraper.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/image_link_scraper

.. |commits-since| image:: https://img.shields.io/github/commits-since/HoverHell/image_link_scraper/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/HoverHell/image_link_scraper/compare/v0.1.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/image_link_scraper.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/image_link_scraper

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/image_link_scraper.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/image_link_scraper

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/image_link_scraper.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/image_link_scraper


.. end-badges

A library for scraping image(s) from links (expecially ones posted to reddit).

* Free software: MIT license

Installation
============

::

    pip install image_link_scraper

Documentation
=============

https://image_link_scraper.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
