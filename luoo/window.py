#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import tty
import termios
import logging
import time

logger = logging.getLogger('window')
logger.setLevel(logging.DEBUG)


class GetInput(object):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        fd = sys.stdin.fileno()
        attr = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        except:
            logger.debug("Input error")
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, attr)
        return ch


getCh = GetInput()


class Window(object):
    """
    data就是这里要展示抓取到的信息，每个栏目有所不同，用data_type表示
    data_type:0播放页面，1期刊页面，2专栏的文章页面,3专栏播放
    """
    def __init__(self, data, data_type):
        self.data = data
        self.data_type = data_type
        self.topline = 0  # 由于data数量有可能大于终端大小，topline表示第一行是第几个data
        self.currentline = 0  # 当前光标指向的行
        self.markline = 0  # 当前播放的行
        self.window_height, self.window_width = self.get_window_size()
        subprocess.call('echo "\033[?25l"', shell=True)  # 隐藏光标
        # subprocess.call('echo "\033[?25h"', shell=True)  # 显示光标

    """
    每当有动作的时候的时候都要重新展示一遍界面
    每个界面的展示方式根据data_type而定
    """
    def display(self):
        subprocess.call('clear', shell=True)
        title = u"\033[35m♥♥ luoo.net ├┠┡┢┣┤┥┩┪┫┮┰┱┲┳┴┵┺┻┼┽╀╁╂╃╅ 落 ♥♥\033[0m"
        subtitle = ['a.期刊    ', 's.单曲    ', 'd.专栏']
        #print '\033[;40m'
        print
        print ' '*((self.window_width - len(title))/2),
        print title
        print '\033[33m'
        sub_len = sum(map(len,subtitle))
        print ' '*((self.window_width - sub_len-1)/2),
        for i in subtitle:
            print i,
        print '\033[0m'
        top = self.topline
        bottom = self.topline + self.window_height + 1
        for index, content in enumerate(self.data[top:bottom]):
            if index == self.markline:
                prefex = '\033[36m  > '
                afterfex = '\033[0m'
            else:
                prefex = '    '
                afterfex = ''
            print prefex,content['title'],afterfex

    """
    获取命令行窗口的大小
    """
    def get_window_size(self):
        size = subprocess.check_output("stty size", shell=True)
        height, width = size.split(' ')
        return [int(height)-1, int(width)]

    def run(self):
        while True:
            self.display()
            ch = getCh()
            if ch == 'k':
                self.updown(-1)
            elif ch == 'j':
                self.updown(1)
            elif ch == ' ':
                self.updown(1)
            elif ch == '\r':  # 回车
                self.updown(1)
            elif ch == 'q':
                subprocess.call('echo "\033[?25h"', shell=True)
                break

    def updown(self, ch):
        if ch == -1 and self.markline == 0 and self.topline != 0:
            self.topline -= 1
        elif ch == 1 and self.markline + self.topline != len(self.data) - 1 and self.markline == self.window_height:
            self.topline += 1
        if ch == -1 and self.markline != 0:
            self.markline -= 1
        elif ch == 1 and self.markline != self.window_height and self.markline < len(self.data) - 1:
            self.markline += 1

def test_input():
    while 1:
        func = GetInput()
        ch = func()
        print ch
        if ch == 'q':
            break

def test_window():
    test_data = [
            {'title':'我是中国人哈哈哈','href':'http://'}, {'title': '我是中国人x', 'href':'www'},
            {'title':'我是中国人哈哈哈','href':'http://'}, {'title': '我是中国人x', 'href':'www'},
            {'title':'我是中国人哈哈哈','href':'http://'}, {'title': '我是中国人x', 'href':'www'},
            {'title':'我是中国人哈哈哈','href':'http://'}, {'title': '我是中国人x', 'href':'www'},
            {'title':'我是中国人哈哈哈','href':'http://'}, {'title': '我是中国人x', 'href':'www'},
            ]
    win = Window(test_data, 0)
    win.run()
    subprocess.call('echo "\033[?25h"', shell=True)

if __name__ == "__main__":
    #test_input()
    test_window()
