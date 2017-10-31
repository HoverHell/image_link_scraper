"""
A combining wrapper of the scrapers.
"""

from .base import BaseScraper
from .imgur import ImgurScraper


all_scrapers = (
    ImgurScraper,
)

class CombiningScraperBase(BaseScraper):

    children_classes = ()

    def __init__(self, child_kwargs=None):
        child_kwargs = child_kwargs or {}
        self.children = [cls(**child_kwargs) for cls in self.children_classes]

    def _select_child(self, url, **hints):
        for child in self.children:
            if child.is_relevant_url(url, **hints):
                return child

    def is_relevant_url(url, **hints):
        return self._select_child(url, **hints) is not None

    def get_infos(self, url, _annotate_manager=True, _annotate_original=True, **hints):
        child = self._select_child(url, **hints)
        if child is None:
            return []
        result = child.get_infos(url, **hints)
        if _annotate_manager:
            for item in result:
                item['_manager'] = child
        if _annotate_original:
            for item in result:
                item['_original_url'] = url
        return result

    def get_data(self, item_info, allow_auto_child=False, **hints):
        child = item_info.get('_manager')
        if child is None and allow_auto_child:
            original_url = item_info.get('_original_url')
            if original_url:
                child = self._select_child(original_url, **hints)
        if child is None and allow_auto_child:
            item_url = item_info['url']
            child = self._select_child(item_url, **hints)
        if child is None:
            raise Exception("Unable to select a child manager for `get_data`")

        return child.get_data(item_info, **hints)


class CombiningScraper(CombiningScraperBase):

    children_classes = all_scrapers
