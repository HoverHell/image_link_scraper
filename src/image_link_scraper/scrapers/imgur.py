"""
Imgur image links scraper.
"""

import re
import json
import urllib.parse

from .base import CommonScraper


class ImgurScraper(CommonScraper):

    _relevant_domains = (
        'imgur.com',
        '.imgur.com',
    )

    album_item_template = 'http://i.imgur.com/{id}{ext}'
    default_ext = '.jpg'
    removed_image_url = 'http://i.imgur.com/removed.png'

    def get_infos(self, url, **kwargs):
        results, meta = self.get_infos_ex(url, **kwargs)
        return results

    def get_infos_ex(self, url, simple_only=False, allow_videos=True, **hints):
        """

        :param url: ...; examples:
            'https://imgur.com/b86IJJQ'
            'https://imgur.com/a/76ErC'
            'https://i.imgur.com/lntBeOo.gifv'

        :param allow_videos: whether to return videos (gifv); currently does nothing (all items are returned).
        """
        if not allow_videos:
            raise Exception('TODO')

        kwargs = dict(hints, simple_only=simple_only, allow_videos=allow_videos)

        url_info = hints.get('url_info') or urllib.parse.urlparse(url)
        kwargs['url_info'] = url_info
        path = url_info.path
        assert path.startswith('/')

        if path.startswith('/a/') or path.startswith('/gallery/'):
            if simple_only:  # For cases when additional requests are undesired.
                return [], dict(reason='simple_only_but_gallery_url')
            return self._get_infos_album(url, **kwargs)

        info, meta = self._get_info_image(url, **kwargs)
        results = [info] if info else []
        return results, meta

    def _get_info_image(self, url, url_info, simple_only=False, prefer_mp4=True, **kwargs):
        meta = {}
        if not simple_only:
            # TODO: use this for both images and videos.
            try:
                result, meta = self._get_info_image_adv(url, **kwargs)
            except Exception as exc:
                meta['ext_exc'] = exc
            else:
                if result:
                    return result, meta

        meta['mode'] = 'simple_single'

        replacements = {}

        if url_info.scheme == 'http':
            replacements.update(scheme='https')  # it will 301 from http anyway
            meta['tuned_scheme'] = True

        if url_info.hostname == 'imgur.com':
            # NOTE: there's also 'https://imgur.com/download/{id}', but it
            # also returns `gif` instead of `mp4`.
            replacements.update(netloc='i.imgur.com')
            meta['tuned_host'] = True

        if not re.search(r'\..{2,5}$', url_info.path):  # does not have an extension
            replacements.update(path='{}{}'.format(url_info.path, self.default_ext))
            meta['tuned_default_ext'] = True
        elif prefer_mp4 and (url_info.path.endswith('.gifv') or url_info.path.endswith('.gif')):
            replacements.update(path=re.sub(r'\.[^.]+$', r'.mp4', url_info.path))
            meta['tuned_mp4_ext'] = True

        if replacements:
            url_info = url_info._replace(**replacements)

        result = dict(url=url_info.geturl())
        return result, meta

    def _get_info_image_adv(self, url, vid_types=None, **kwargs):
        if vid_types is None:
            vid_types = ('video/mp4', 'video/webm')

        meta = dict(mode='single_advanced')
        page_info = self._get_page(url)
        meta['page_info'] = page_info
        bs = page_info.get('bs')
        if not bs:
            return None, dict(meta, reason=page_info.get('error'))

        vid = bs.find('div', {'class': 'video-container'})
        # TODO: support and test some of:
        #     <link rel="image_src"            href="https://i.imgur.com/98dRIYm.png"/>
        #     <a href="//i.imgur.com/98dRIYm.png" class="zoom">
        #     <img src="//i.imgur.com/98dRIYm.png" alt="" itemprop="contentURL" />
        #     self._get_infos_album_adv(text=page_info['text'], _support_single=True)
        if not vid:
            return None, dict(meta, reason='no div .video-container')

        vid_url = None
        for vid_type in vid_types:
            vid_elem = vid.find('source', {'type': vid_type})
            if not vid_elem:
                continue
            vid_url = vid_elem.get('src')
        if not vid_url:
            return None, dict(meta, reason='no video source element')

        vid_url = urllib.parse.urljoin(url, vid_url)
        return dict(url=vid_url), meta

    def _get_infos_album(self, url, **kwargs):
        meta = {}

        page_info = self._get_page(url, add_bs=False)
        meta['page_info'] = page_info

        text = page_info.get('text')
        if not text:
            return [], dict(meta, reason=page_info.get('error'))

        # text example:
        # """
        # …
        #        <script type="text/javascript">
        #             window.runSlots = {
        #                 config: {"ads_website":"http:\/\/www.imgurads.com\/","allow_nsfw":false,"...},
        #                 item: {"id":"I8YJX","account_id":null,"title":"…", … "num_images":"4","datetime":"2017-04-10 22:16:06",\
        #                        … "hash":"I8YJX", … "is_album":true,\
        #                        … ,"album_images":{"count":4,"images":[\
        #                             {"hash":"wxvN0bJ","title":"","description":null,"has_sound":false,"width":3264,"height":1836,\
        #                              "size":491441,"ext":".jpg","animated":false,"prefer_video":false,"looping":false,\
        #                              "datetime":"2017-04-10 22:16:32"},\
        #                             … ]},\
        #                        "adConfig":{…}}
        #             }
        # …
        # """

        ext_result, ext_meta = self._get_infos_album_adv(text, **kwargs)
        if ext_result:
            meta.update(ext_meta)
            return ext_result, meta

        meta['mode'] = 'album_rex'
        item_re = r'"hash":"([^"]+)","title"'
        item_re_c = re.compile(item_re)

        items = [
            item
            for line in text.splitlines()  # TODO?: efficient iter-splitlines.
            for subitems in item_re_c.findall(line)
            for item in subitems
        ]

        result = [dict(url=self.album_item_template.format(id=item, ext=self.default_ext))
                  for item in items]
        return result, dict(items=items, page_info=page_info)

    def _get_infos_album_adv(self, text, prefer_mp4=True, _support_single=False, **kwargs):
        """
        Attempt to `json.loads` the data meant for javascript.
        """
        meta = dict(mode='album_rex_json')
        load_errors = []
        supitem_datas = []
        supitems_metas = []
        results = []
        results_metas = []

        supitem_jsons = re.findall(r'item: *(\{.*\}) *\n', text)

        for supitem_json in supitem_jsons:
            supitem_meta = dict(supitem_json=supitem_json)
            try:
                supitem_data = json.loads(supitem_json)
            except Exception as exc:
                load_errors.append(dict(supitem_meta, reason='json_loads_failed', loads_exc=exc))
                continue

            supitem_datas.append(supitem_data)
            supitem_meta['supitem_data'] = supitem_data

            supitem_results = []
            supitem_results_metas = []
            try:
                if _support_single and 'hash' in supitem_data and 'album_images' not in supitem_data:
                    items = [supitem_data]
                else:
                    items = supitem_data['album_images']['images']

                if not isinstance(items, list):
                    raise TypeError('.item.album_images.images is not a list', items)

                # NOTE: will fail the entire `item_json` if one of the subitems fails.
                for item in items:
                    item_meta = dict(data=item)
                    item_id = item['hash']
                    item_ext = item.get('ext') or self.default_ext
                    if prefer_mp4 and (item_ext == '.gif' or item_ext == '.gifv'):
                        item_ext = '.mp4'
                        item_meta['tuned_ext_mp4'] = True
                    item_res = dict(url=self.album_item_template.format(id=item_id, ext=item_ext))
                    # item.get('animated')
                    # item.get('prefer_video')
                    supitem_results.append(item_res)
                    supitem_results_metas.append(item_meta)
            except (KeyError, TypeError) as exc:
                load_errors.append(dict(item_meta, reason='unexpected_structure', struct_exc=exc))
                continue

            results.extend(supitem_results)
            results_metas.extend(supitem_results_metas)

        meta.update(load_errors=load_errors, supitem_datas=supitem_datas, results_metas=results_metas)
        return results, meta

    def get_data(self, item_info, **hints):
        url = item_info['url']

        if url == self.removed_image_url:
            return dict(data=None, error='item is a removed image')

        resp = self._request(url)

        if resp.url == self.removed_image_url:  # 302'd
            return dict(data=None, error='item redirects to a removed image')

        if self._is_html_resp(resp):
            return dict(data=None, error='got an HTML page')

        content = resp.content
        return dict(data=content, _content_type=resp.headers.get('content-type'), _resp=resp)
