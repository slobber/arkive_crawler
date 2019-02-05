import errno
import os
import re

import scrapy
from scrapy import Selector
from scrapy.spiders import CrawlSpider, Spider
from urllib.parse import urlparse, parse_qs

from arkive import prepare
from arkive.color_console import prGreen, prYellow, prCyan, prRed
from arkive.items import ArkiveItem


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

class Arkive(CrawlSpider):
    name = 'arkive'
    start_urls = prepare.all_spices_url
    embedFrameUrl = 'https://cdnapisec.kaltura.com/html5/html5lib/v1.9.2/mwEmbedFrame.php?&cache_st=1379606697&wid=_662652&uiconf_id=19837871&entry_id={}&flashvars[externalInterfaceDisabled]=false&flashvars[streamerType]=hdnetwork&flashvars[akamaiHD]=%7B%22loadingPolicy%22%3A%22preInitialize%22%2C%22asyncInit%22%3A%22true%22%7D&flashvars[autoPlay]=true&flashvars[aboutPlayer]=Arkive%20player&flashvars[mediaProxy.preferedFlavorBR]=600&flashvars[autoRewind]=true&flashvars[disableBitrateCookie]=true&playerId=kaltura_player_1379606697&forceMobileHTML5=true&urid=1.9.2&callback=mwi_kalturaplayer13796066970'
    data = prepare.data
    progress = {}
    index = 0

    def parse(self, response):
        uri = urlparse(response.url)
        spice_id = '/'.join(uri.path.split('/')[1:3])
        item = ArkiveItem()
        item['id'] = spice_id
        item['videos_url'] = []
        item['videos_path'] = []
        item['photos_url'] = []
        item['photos_path'] = []
        item['index'] = '{:02d}'.format(Arkive.index)
        Arkive.index = Arkive.index + 1

        Arkive.progress[item['id']] = {
            'photo': 0,
            'video': 0
        }

        folder = os.path.join(prepare.OUTPUT_ROOT, item["id"])
        if folder[-1] == '-': 
            folder = folder[:-1]

        spice = Arkive.data[item['id']]
        mkdir_p(folder)
        readme = os.path.join(folder, 'readme.md')
        mkdir_p(os.path.join(folder, 'tmp'))
        mkdir_p(os.path.join(folder, 'photos'))
        mkdir_p(os.path.join(folder, 'videos'))
        with open(readme, 'w', encoding='utf-8') as rm:
            data = {}
            if 'title' in spice:
                data['title'] = spice['title']
            if 'nameCommon' in spice:
                data['nameCommon'] = spice['nameCommon']
            if 'nameScientific' in spice:
                data['nameScientific'] = spice['nameScientific']
            if 'shortDescription' in spice:
                data['shortDescription'] = spice['shortDescription']
            if 'geographicLocation' in spice:
                data['geographicLocation'] = '\n\t* ' + '\n\t* '.join(spice['geographicLocation'])
            if 'accessionsGroup' in spice:
                data['accessionsGroup'] = spice['accessionsGroup']
            if 'IUCNId' in spice:
                data['IUCNId'] = spice['IUCNId']
            if 'IUCNStatus' in spice:
                data['IUCNStatus'] = spice['IUCNStatus']
            if 'folksonomyGroups' in spice:
                data['folksonomyGroups'] = '\n\t* ' + '\n\t* '.join(spice['folksonomyGroups'])
            if 'imageCount' in spice:
                data['imageCount'] = spice['imageCount']
                item['photo_count'] = spice['imageCount']
            if 'videoCount' in spice:
                data['videoCount'] = spice['videoCount']
                item['video_count'] = spice['videoCount']
            rm.write('\n'.join(['* {}: {}'.format(item, value) for item, value in data.items()]))
        prYellow('Start spice [{: ^60}], photos: {:2}, videos: {:2}'.format(item['index'] + '.' + item['id'], item['photo_count'], item['video_count']))

        with open(os.path.join(folder, 'factsheet.html'), 'w', encoding='utf-8') as f:
            f.write(response.body.decode('utf-8'))
        if item['video_count'] > 0:
            yield scrapy.Request('https://www.arkive.org/{}/videos.html'.format(item["id"]), meta={'item': item},
                             callback=self.parse_videos_page)
        if item['photo_count'] > 0:
            yield scrapy.Request('https://www.arkive.org/{}/photos.html'.format(item["id"]), meta={'item': item},
                             callback=self.parse_photos_page)

    def parse_photos_page(self, response):
        item = response.meta['item']
        folder = os.path.join(prepare.OUTPUT_ROOT, item["id"])
        if folder[-1] == '-': 
            folder = folder[:-1]
        with open(folder + '/tmp/photos.html', 'w', encoding='utf-8') as f:
            f.write(response.body.decode('utf-8'))
        photos = Selector(text=response.body).xpath(
            '//div[@id="results"]//div[@class="thumb"]/div[@class="wrapper"]/div[@class="inner"]/a/img/@src').extract()
        photos = [photo.replace('.Small', '.Large') for photo in photos]
        i = 1
        for photo in photos:
            photo_name = '{}. {}'.format(i, photo.split('/')[-1])
            i = i + 1
            if not os.path.isfile(os.path.join(folder, 'photos', photo_name)):
                yield scrapy.Request(photo, meta={'item': item, 'photo_name': photo_name}, callback=self.download_photo)
            else:
                Arkive.progress[item['id']]['photo'] += 1
        if len(photos) - Arkive.progress[item['id']]['photo'] > 0:
            prCyan('Loading photos [{:2}/{:2}] of [{: ^60}]'.format(len(photos) - Arkive.progress[item['id']]['photo'], len(photos), item['index'] + '.' + item['id']))

    def parse_fact_sheet_page(self, response):
        item = response.meta['item']
        folder = os.path.join(prepare.OUTPUT_ROOT, item["id"])
        if folder[-1] == '-': 
            folder = folder[:-1]
        with open(os.path.join(folder, 'factsheet.html'), 'w', encoding='utf-8') as f:
            f.write(response.body.decode('utf-8'))

    def parse_videos_page(self, response):
        item = response.meta['item']
        folder = os.path.join(prepare.OUTPUT_ROOT, item["id"])
        if folder[-1] == '-': 
            folder = folder[:-1]
        with open(os.path.join(folder, 'tmp', 'videos.html'), 'w', encoding='utf-8') as f:
            f.write(response.body.decode('utf-8'))
        videos = Selector(text=response.body).xpath(
            '//div[@id="results"]//div[@class="thumb"]/div[@class="wrapper"]/div[@class="inner"]/a/@href').extract()
        for video in videos:
            video_name = video.split('.')[0] + '.mp4'
            if not os.path.isfile(os.path.join(folder, 'videos', video_name)):
                yield scrapy.Request('https://www.arkive.org/{}/{}'.format(item['id'], video),
                                     meta={'item': item, 'video_id': video.split('.')[0]},
                                     callback=self.parse_video_page)
            else:
                Arkive.progress[item['id']]['video'] += 1
        if len(videos) - Arkive.progress[item['id']]['video'] > 0:
            prCyan('Loading videos [{:2}/{:2}] of [{: ^60}]'.format(len(videos) - Arkive.progress[item['id']]['video'], len(videos), item['index'] + '.' + item['id']))

    def parse_video_page(self, response):
        item = response.meta['item']
        video_id = response.meta['video_id']
        regex = r'"entry_id": "([^"]+)",'
        entry_id = re.findall(regex, response.body.decode('utf-8'), re.MULTILINE)[0]
        folder = os.path.join(prepare.OUTPUT_ROOT, item["id"])        
        if folder[-1] == '-': 
            folder = folder[:-1]
        with open(folder+'/tmp/video_page@{}.html'.format(entry_id), 'w', encoding='utf-8') as f:
            f.write(response.body.decode('utf-8'))
        yield scrapy.Request(Arkive.embedFrameUrl.format(entry_id), meta={'item': item, 'entry_id': entry_id, 'video_id': video_id}, callback=self.parse_video_js)
        
    def parse_video_js(self, response):
        item = response.meta['item']
        entry_id = response.meta['entry_id']
        video_id = response.meta['video_id']
        folder = os.path.join(prepare.OUTPUT_ROOT, item["id"])
        if folder[-1] == '-': 
            folder = folder[:-1]
        with open(folder+'/tmp/video_js@{}.js'.format(entry_id), 'w', encoding='utf-8') as f:
            f.write(response.body.decode('utf-8'))
        regex = r'\\"downloadUrl\\"\:\\"([^"]+)\\"'
        download_url = re.findall(regex, response.body.decode('utf-8'), re.MULTILINE)[0]
        download_url = download_url.replace('\\', '')
        yield scrapy.Request(download_url, meta={'item': item, 'entry_id': entry_id, 'video_id': video_id}, callback=self.download_video, errback=self.errback_httpbin)
            
    def errback_httpbin(self, failure):
        request = failure.request
        if 'kaltura.com' in request.url:
            item = request.meta['item']
            entry_id = request.meta['entry_id']
            video_id = request.meta['video_id']
            prRed('Fail download video [{}/{}] of [{: ^60}]'.format(entry_id, video_id, item['index'] + '.' + item['id']))
            with open('timeout.log', 'a+', encoding='utf-8') as f:
                f.write('{}: {} {}\n{}\n\n'.format(item['id'], video_id, entry_id, request.url))

    def download_video(self, response):
        item = response.meta["item"]
        video_id = response.meta['video_id']
        prGreen('Downloaded video [{}.mp4] of [{: ^60}] from {}'.format(video_id, item['index'] + '.' + item['id'], response.url[:30] + '...' + response.url[-20:]))
        folder = os.path.join(prepare.OUTPUT_ROOT, item["id"])
        if folder[-1] == '-': 
            folder = folder[:-1]
        with open(folder + '/videos/{}.mp4'.format(video_id), 'wb') as f:
            f.write(response.body)
        Arkive.progress[item['id']]['video'] += 1

    def download_photo(self, response):
        item = response.meta["item"]
        photo_name = response.meta["photo_name"]

        prGreen('Downloaded photo [{}] of [{: ^60}] from {}'.format(photo_name, item['index'] + '.' + item['id'], response.url[:30] + '...' + response.url[-20:]))
        folder = os.path.join(prepare.OUTPUT_ROOT, item["id"])
        if folder[-1] == '-': 
            folder = folder[:-1]
        with open(folder + '/photos/{}'.format(photo_name), 'wb') as f:
            f.write(response.body)

        Arkive.progress[item['id']]['photo'] += 1


