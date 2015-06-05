#! /usr/bin/env python
# -*-coding: utf-8 -*-

import os
import sys
import urllib2
import threading
import logging
import subprocess
import socket
socket.setdefaulttimeout(5)

import music
import window
import player
import config

logging.basicConfig(
    format="%(asctime)s - \
[%(process)d]%(filename)s:%(lineno)d - %(levelname)s: %(message)s",
    datefmt='%Y-%m-%d %H:%I:%S',
    filename=os.path.expanduser('~/.luoo.log'),
    level=logging.WARNING
)

logger = logging.getLogger('luoo')
logger.setLevel(logging.INFO)


class luoo(window.Window):
    def __init__(self):
        self.data = music.main_page()
        self.data_type = 0
        self.event = threading.Event()  # 单曲播放结束的事件
        self.volume = 50
        self.key_down = False  # 用于辨别自动循环和手动播放
        self.playing = True  # 标记是否在播放
        self.player = player.MPlayer(self.event, self.volume)
        self.musics_page = 1  # 管理期刊页面
        self.musician_page = 1  # 管理单曲页面
        self.essay_page = 1  # 管理专栏页面
        super(luoo, self).__init__(self.data, self.data_type)
        self.play()
        threading.Thread(target=self.watchdog).start()

    #@profile
    def run(self):
        window_key = True  # 如果不是控制界面的操作，就不用刷新界面
        while True:
            if window_key:
                self.display()
            self.key_down = False
            ch = window.getCh()
            self.key_down = True
            if ch not in config.window_keys:
                window_key = False
            else:
                window_key = True
            if ch not in config.keys:
                continue
            if ch == 'k':
                self.updown(-1)
            elif ch == 'j':
                self.updown(1)
            elif ch == ' ':  # 暂停
                if self.data_type == 0:
                    self.player.pause()
                elif self.data_type == 1:
                    pass
            elif ch == '\r':  # 回车代表执行
                if self.data_type == 0:
                    self.play()
                elif self.data_type == 1:
                    self.data_type = 0
                    self.player.quit()
                    self.data = music.getOneMusicList(self.data[self.markline]['href'])
                    self.markline = 0
                    self.topline = 0
                    self.play()
                elif self.data_type == 2:
                    self.play()
                elif self.data_type == 3:
                    pass
            elif ch == '-' or ch == '=':
                if self.data_type == 0:
                    self.player.volumeUpDown(ch)
            elif ch == 'n':
                if self.data_type == 0:
                    self.playNext()
                elif self.data_type == 1:
                    self.musics_page += 1
                    self.data = music.getMusics(self.musics_page)
                elif self.data_type == 2:
                    self.essay_page += 1
                    self.data = music.getEssays(self.essay_page)
            elif ch == 'b':
                if self.data_type == 0:
                    self.playPre()
                elif self.data_type == 1:
                    if self.musics_page > 1:
                        self.musics_page -= 1
                    self.data = music.getMusics(self.musics_page)
                elif self.data_type == 2:
                    if self.essay_page > 1:
                        self.essay_page -= 1
                    self.data = music.getEssays(self.essay_page)
            elif ch == 'a':
                self.setPage()
                self.data_type = 1
                self.data = music.getMusics()
            elif ch == 's':
                self.setPage()
                self.data_type = 3
                self.data = music.getMusician()
            elif ch == 'd':
                self.setPage()
                self.data_type = 2
                self.data = music.getEssays()
            elif ch == 'q':
                self.player.quit()
                self.playing = False
                subprocess.call('echo "\033[?25h"', shell=True)
                break

    def setPage(self):
        self.musics_page = 1
        self.musician_page = 1
        self.essay_page = 1
        self.markline = 0
        self.topline = 0

    def watchdog(self):
        '''
        检查单曲是否播放完毕
        '''
        while self.playing:
            self.event.wait()
            self.event.clear()
            if self.key_down:
                continue
            else:
                if self.data_type == 0 or self.data_type == 2:
                    if self.markline < len(self.data) - 1:
                        self.markline += 1
                        self.playNext()
                    else:
                        self.markline = 0
                        self.display()
                        self.play()

    def playNext(self):
        self.updown(1)
        self.play()

    def playPre(self):
        self.updown(-1)
        self.play()

    def play(self):
        self.player.start(self.data[self.markline]['href'])


def main():
    l = luoo()
    l.run()

if __name__ == "__main__":
    main()
