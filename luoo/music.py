#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
import logging
import urllib2
import sys

logger = logging.getLogger('music')
logger.setLevel(logging.DEBUG)

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml; " \
        "q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "text/html",
    "Accept-Language": "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "http://www.xiami.com/",
    "User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 "\
        "(KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36"
}

url = "http://luoo.net/"  # 主页
music = "http://luoo.net/music/"  # 期刊
musician = "http://luoo.net/musician/"  # 单曲
essays = "http://luoo.net/essays/"  # 专栏
url_type = {'url': url,
        'music': music,
        'musician': musician,
        'essays': essays}

head_tabs = {'luoo': u'落',
             'music': u'期刊',
             'musician': u'单曲',
             'essay': u'专栏'}

class TimeOutError(Exception):
    def __repr__(self):
        return """
        wow.... It seems Something wriong with your Network
        Please try later.
        """

    def __str__(self):
        return self.__repr__()


# 首页，进入应用之后，默认获取第一个推荐期刊
def main_page():
    try:
        page = urllib2.urlopen(url)
        html = BeautifulSoup(page.read())
    except:
        logger.debug('get_main_page timeout')
        raise TimeOutError()
    # music_section
    music_section = html.find('div', {'class': 'section-vol'})
    #music_tags = music_section.findAll('a', {'class': 'tag'})
    #music_tags = map(lambda x: {'href': dict(x.attrs)['href'], 'title': x.string}, music_tags)
    #print u'音乐期刊\t',
    #for tags in music_tags:
    #    print tags['title'],
    #print ''
    musics = music_section.findAll('a', {'class': 'title'})
    musics = map(lambda x: {'href': dict(x.attrs)['href'], 'title': x.string}, musics)
    music_list = getOneMusicList(musics[0]['href'])
    return music_list  # [{title:,href:}]

# 获取某个专栏的全部music，传入专栏的链接
def getOneMusicList(url):
    try:
        page = urllib2.urlopen(url)
        html = BeautifulSoup(page)
        songs = html.findAll('a', {'class': 'trackname btn-play'})
        songs = map(lambda x: x.string, songs)
    except:
        logger.debug('get music list timeout')
        raise TimeOutError()
    num = url.split('/')[-1]
    song_urls = []
    pre = 'http://emo.luoo.net/low/luoo/radio%s/%s.mp3'
    for s in songs:
        song_urls.append(pre % (num, s.split('.')[0]))
    returndata = []
    for i in range(len(songs)):
        returndata.append({'title': songs[i], 'href': song_urls[i]})
    return returndata

# 获取期刊
def getMusics(page = 1):
    if page == 1:
        try:
            page = urllib2.urlopen('http://www.luoo.net/music/')
            html = BeautifulSoup(page.read())
            musics = html.findAll('a', {'class': 'name'})
            musics = map(lambda x: {'href': dict(x.attrs)['href'], 'title': x.string}, musics)
            return musics
        except:
            logger.debug('timeout')
            raise TimeOutError()
    elif page >= 2:
        try:
            page = urllib2.urlopen('http://www.luoo.net/tag/?p=%s' % page)
            html = BeautifulSoup(page.read())
            musics = html.findAll('a', {'class': 'name'})
            musics = map(lambda x: {'href': dict(x.attrs)['href'], 'title': x.string}, musics)
            return musics
        except:
            logger.debug('timeout')
            raise TimeOutError()


def getMusician(page=1):
    try:
        page = urllib2.urlopen('http://www.luoo.net/musician/?p=%s' % page)
        html = BeautifulSoup(page.read())
        musics = html.findAll('a', {'class': 'title', 'href': 'javascript:;'})
        musics = map(lambda x: dict(x.attrs), musics)
        titles = html.findAll('img', {'class': 'cover rounded'})
        titles = map(lambda x: dict(x.attrs), titles)
        musician = []
        for index in range(len(titles)):
            tmp = dict()
            tmp['href'], tmp['title'], tmp['id'] = 'javascript:;',titles[index]['alt'], musics[index]['id']
            musician.append(tmp)
        return musician
    except Exception,e:
        print e
        logger.debug('timeout')
        raise TimeOutError()


def getEssays(page=1):
    try:
        page = urllib2.urlopen("http://www.luoo.net/essay/index/p/%s" % page)
        html = BeautifulSoup(page.read())
        musics = html.find('div', {'class': 'essay-list'})
        essays = musics.findAll('a', {'class': 'title'})
        essays = map(lambda x: {'essay_href': dict(x.attrs)['href'], 'title': dict(x.attrs)['title']}, essays)
        songs = musics.findAll('span', {'class': 'time'})
        songs = map(lambda x: x.string, songs)
        pre_url = "http://emo.luoo.net/low/"
        for index, s in enumerate(songs):
            s = s.split('-')
            href = pre_url + s[0] + '/' + s[1] + s[2] + '.mp3'
            essays[index]['href'] = href
        return essays
    except Exception, e:
        print e
        raise TimeOutError()


def test_main_page():
    main_page()

def test_get_musics():
    print getMusics(2)

def test_get_musician():
    print getMusician()

def test_get_essays():
    print getEssays(2)

if __name__ == "__main__":
    #test_main_page()
    #test_get_musics()
    #test_get_musician()
    test_get_essays()
