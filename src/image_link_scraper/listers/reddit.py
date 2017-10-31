"""
Reddut links lister(s).
"""

# import re
import urllib.parse

from .. import __version__ as VERSION
# import praw  # possibly too much for this


class RedditBase:

    USER_AGENT = 'python:image_link_scraper:{} (library)'.format(VERSION)
    BASE_URL = "https://www.reddit.com"

    @classmethod
    def _request(cls, url, **kwargs):
        """
        Common method for requesting Reddit with `requests`.

        https://github.com/reddit/reddit/wiki/API#rules
        https://www.reddit.com/wiki/api

        TODO?:
        https://praw.readthedocs.io/en/latest/getting_started/authentication.html
        """
        from ..common.requests import req
        from ..common.utils import merge_with_kwargs_dict

        merge_with_kwargs_dict(kwargs, 'headers', pre={'User-Agent', cls.USER_AGENT})
        return req(url, **kwargs)


class RedditPostsLister(RedditBase):

    def __init__(self, *args, **kwargs):
        raise Exception("TODO")

    @classmethod
    def build_url(cls, subreddit, multireddit=None, reddit_sort=None, prev_id=None, base=None):
        """
        Make a reddit data url for the given parameters.

        :param subreddit: ..., examples: 'python', 'somebody/m/name'
        :param multireddit: ...; default: `None` (autodetect)
        :param previd: add the 'posts starting from ...' to the parameters.
        :param reddit_sort: ..., examples: 'top', 'top/hour', 'new'

        Reddit documentation:
        https://www.reddit.com/dev/api#GET_hot
        https://www.reddit.com/dev/api#GET_{sort}

        >>> RedditPostsLister.build_url("pics", reddit_sort="top/day", prev_id="test")
        'https://reddit.com/r/pics/top.json?after=test&sort=top&t=day'
        >>> RedditPostsLister.build_url("pics", reddit_sort="random", prev_id="test")
        'https://reddit.com/r/pics/random.json?after=test'
        """
        if base is None:
            base = cls.BASE_URL

        subreddit = subreddit.strip("/")

        m_check = '/m/' in subreddit
        if multireddit is not None:  # if specified, do the validation.
            if multireddit and not m_check:
                raise ValueError("Multireddit subreddit should be in the form `{username}/m/{multireddit_name}`", subreddit)
            elif not multireddit and m_check:
                raise ValueError("Specified subreddit seems to be a multireddit when a non-multireddit is requested", subreddit)
        else:
            multireddit = m_check

        url = subreddit

        if multireddit and not url.startswith("user/"):
            url = "user/{}".format(url)  # "somebody/m/name" -> "user/somebody/m/name"
        elif not multireddit and not url.startswith("r/"):
            url = "r/{}".format(url)

        params = []

        if prev_id is not None:
            params.append(("after", prev_id))

        sort_type = sort_param = None
        if reddit_sort is not None:
            if isinstance(reddit_sort, tuple):  # `("top", "day")`
                sort_type, sort_param = reddit_sort
            elif "/" in reddit_sort:  # `"top/day"`
                sort_type, sort_param = reddit_sort.split("/", 1)
            else:  # `"top"`
                sort_type = reddit_sort

        if sort_type is not None:
            url = "{}/{}".format(url, sort_type)  # "r/somesubreddit/top"

        if sort_param is not None:
            params.append(("sort", sort_type))
            params.append(("t", sort_param))

        url = "{}.json".format(url)
        url = "{}?{}".format(url, urllib.parse.urlencode(params))
        url = urllib.parse.urljoin(base, url)
        return url

    def get_raw_items(self, source):
        """
        ...

        :param source: full listing json url, or a dict for `build_url`.
        """
        if isinstance(source, dict):
            source = self.build_url(**source)

        resp = self._request(source)
        data = resp.json()
        assert data['kind'] == 'Listing'
        # Notable: `data['data']['after']`, `data['data']['whitelist_status']`
        result = data['data']['children']
        # assert all(item['kind'] == 't3' for item in result)  # uncertain
        result = [item['data'] for item in result]
        return result

    def raw_item_to_item(self, item, allow_self_posts=False):
        """ Listing item data to library-common item format """
        url = item['url']
        if not allow_self_posts and item.get('is_self'):
            return None
        result = dict(
            url=url,
            # Does not include the subreddit name, but for now this works: "https://www.reddit.com/r/all/comments/{id}/"
            id=item['id'],
            # id=item['permalink'],
        )
        return result

    def get_items(self, source, include_self_posts=False, **kwargs):
        items = self.get_raw_items(source)
        result = [self.raw_item_to_item(item, allow_self_posts=include_self_posts)
                  for item in items]
        result = [item for item in result if item]
        return result
