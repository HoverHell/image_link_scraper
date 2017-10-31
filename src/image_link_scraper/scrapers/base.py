
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
        raise Exception("TODO")
