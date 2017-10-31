"""
Common point for the `requests` library for the scrapers/listers/etcetera of this library.
"""

import requests
from requests import *


def req(url, method='GET', _rfs=True, **kwargs):
    """
    A general 'requests.request' wrapepr with some conveniences.

    Does `raise_for_status` as default.
    """

    # TODO: default User-Agent
    # TODO: default retries

    resp = requests.request(method, url, **kwargs)
    if _rfs:
        resp.raise_for_status()

    return resp
