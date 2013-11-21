import json
import re
import os
import urlparse
from tornado.httpclient import AsyncHTTPClient
import tornado.ioloop
import tornado.web
from tornado import gen
from pyquery import PyQuery as pq
from lxml import etree


PROJECT_PATH = os.path.dirname(__file__)
STATIC_PATH = os.path.join(PROJECT_PATH, 'static')
TEMPLATE_PATH = os.path.join(PROJECT_PATH, 'templates')


class NonCachedStaticFileHandler(tornado.web.StaticFileHandler):
    """
    Non cached static files for development purpose. Use nginx to serve static
    files in production.
    """

    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control',
                        'no-store, no-cache, must-revalidate, max-age=0')


class MainHandler(tornado.web.RequestHandler):
    _template = os.path.join(TEMPLATE_PATH, 'index.html')

    def get(self):
        self.render(self._template)


class ZingMp3Handler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        album_url = self.get_argument('album', '')
        if album_url == '':
            reason = 'Album url is invalid'
            self.set_status(400, reason=reason)
            self.write({'ok': False, 'reason': reason})
            return

        http_client = AsyncHTTPClient()

        # Retrieve the link of the album XML list
        res = yield http_client.fetch(album_url)
        search = re.search(r'name="flashvars".*?xmlURL=(.*?)&amp;', res.body)
        if not search:
            reason = 'Cannot find flashvars'
            self.write({'ok': False, 'reason': reason})
            return
        album_xml_url = search.group(1)

        # Retrieve mp3 links
        res = yield http_client.fetch(album_xml_url)
        xml = pq(etree.fromstring(res.body))
        mp3_links = []
        for item in xml('item[type=mp3]'):
            title = item.find('title')
            artist = item.find('performer')
            source = item.find('source')
            mp3_links.append({
                'title': title.text.strip() if title is not None else '',
                'artist': artist.text.strip() if artist is not None else '',
                'url': source.text if source is not None else [],
            })

        self.set_status(200)
        self.write({'ok': True, 'mp3': mp3_links, 'xml': album_xml_url})


class ZingTvHandler(tornado.web.RequestHandler):
    _SERIES_URL = 'http://tv.zing.vn/tv/media/get-media-of-series?seriesId=%s'
    _ZING_TV_URL = 'http://tv.zing.vn/'

    @gen.coroutine
    def get(self):
        series_url = self.get_argument('series', '')
        if series_url == '':
            reason = 'Series url is invalid'
            self.set_status(400, reason=reason)
            self.write({'ok': False, 'reason': reason})
            return

        http_client = AsyncHTTPClient()

        # Find all series id from the url
        res = yield http_client.fetch(series_url)
        matches = re.findall(r'id="curpage_series_(\w+?)"', res.body)
        if not matches:
            reason = 'Cannot find series id'
            self.write({'ok': False, 'reason': reason})
            return
        search = re.search(r'class="page-title".*?>(.*?)</h1', res.body)
        if search:
            series_name = search.group(1).strip().decode('utf-8')
        else:
            series_name = None

        movie_links = []
        for series_id in matches:
            res = yield http_client.fetch(self._SERIES_URL % series_id)
            info = json.loads(res.body[1:len(res.body)-1])
            for page in info['page']:
                name = page['media']['name'].replace('\\', '').replace('/', '')\
                    .strip()
                if series_name is not None:
                    name = series_name + ' - ' + name
                link = urlparse.urljoin(self._ZING_TV_URL,
                                        page['media']['linkDetail'])
                res = yield http_client.fetch(link)
                search = re.search(r'\'<source src="(.*?)"', res.body)
                if search:
                    movie_links.append({'name': name, 'url': search.group(1)})

        movie_links.reverse()

        self.set_status(200)
        self.write({'ok': True, 'movies': movie_links})


application = tornado.web.Application([
    (r'/static/(.*)', NonCachedStaticFileHandler, {'path': STATIC_PATH}),
    (r'/zingmp3', ZingMp3Handler),
    (r'/zingtv', ZingTvHandler),
    (r'/', MainHandler),
], debug=True)


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
