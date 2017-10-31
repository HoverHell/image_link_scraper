
import urllib.parse


class BaseScraper:
    """
    Base class of a site-specific scraper.
    """

    def is_relevant_url(self, url, **hints):
        """
        Returns whether this particular scraper supports the given URL.
        """
        raise NotImplementedError

    def get_infos(self, url, **hints):
        """
        For the given supported URL, return a list of `item_info` dicts.

        `item_info` is currently internal-only.
        """
        raise NotImplementedError

    def get_data(self, item_info, **hints):
        """
        For the given `item_info` from `get_infos`, return a dict with:
          * `data`: the downloaded image data.
          * `filename`: (optional) the suggested image filename.
        """
        raise NotImplementedError


class CommonScraper(BaseScraper):
    """
    Base of a site-specific scraper that contains commonly-useful additions.
    """

    _relevant_domains = (
        # e.g. 'imgur.com'
    )

    def is_relevant_url(self, url, **hints):
        """
        Process `url` based on `self._relevant_domains`
        """
        # Synopsis:
        # parse the url into the domain.
        # check whether the domain is equals or subdomain of any self._relevant_domains
        url_info = hints.get('url_info') or urllib.parse.urlparse(url)
        hostname = url_info.hostname
        for domain in self._relevant_domains:
            if domain.startswith("."):  # ".example.com"
                if hostname.endswith(domain):  # "something.example.com"
                    return True
            else:  # "www.example.com"
                if hostname == domain:
                    return True
        return False

    @classmethod
    def _request(cls, url, **kwargs):
        from ..common.requests import req
        resp = req(url, **kwargs)
        return resp

    @classmethod
    def _is_html_resp(cls, resp, default=False, check_by_content_type=True):
        if check_by_content_type:
            content_type = (resp.headers.get('content-type') or '').lower()
            if content_type.startswith("text/html"):
                return True

        return default

    @classmethod
    def _get_page(cls, url, markup_lib="html5lib", add_text=True, add_bs=True, **kwargs):
        """
        Return a processed HTML page from the URL.
        """
        result = {}
        from bs4 import BeautifulSoup
        resp = cls._request(url, **kwargs)
        result['resp'] = resp

        if not cls._is_html_resp(resp, default=False):
            result.update(error="not_html_data", content_type=resp.headers.get('content-type'))
            return result

        if add_text or add_bs:
            text = resp.text
            result['text'] = text

        if add_bs:
            bs = BeautifulSoup(text, markup_lib)
            result['bs'] = bs

        return result
