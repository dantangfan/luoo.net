#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import threading
import signal
import subprocess
import fcntl
import logging

logger = logging.getLogger('player')
logger.setLevel(logging.DEBUG)


class MPlayer(object):
    """
    默认音量50
    event事件判断是否完成播放
    """

    def __init__(self, event, default_volume=50):
        self._sub_proc = None
        self._args = ['mplayer',  # 播放器名字
                '-slave',  # 把mplayer后台执行，需要查看mplayer -input cmdlist获取可用的命令
                '-nolirc',  # 不显示warning信息
                '-softvol',  # 不使用硬件全局的音量
                ]
        self._event = event
        self._volume = default_volume

    def __repr__(self):
        if self.is_alive:
            status = 'PID {0}'.format(self._sub_proc.pid)
        else:
            status = 'not running'
        return '<{0} ({1})>'.format(self.__class__.__name__, status)

    def _run_player(self, extra_cmd):
        if self.is_alive:
            self.quit()
        args = self._args + extra_cmd
        self._sub_proc = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
                )
        # 用subprocess调用子进程，只能在子进程结束的时候返回stdout输出
        # 为了让数据实时更新，需要把子进程到输出改成非阻塞的方式
        logger.debug('Start running')
        flags = fcntl.fcntl(self._sub_proc.stdout, fcntl.F_GETFL)
        fcntl.fcntl(self._sub_proc.stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        threading.Thread(target=self._watchdog).start()
        #threading.Thread(target=self._output).start()

    def _watchdog(self):
        '''
        独立的线程
        用于监控播放结束，结束后，会设置event
        '''
        if not self.is_alive:
            self._event.set()
            return
        returncode = self._sub_proc.wait()  # 一直等到播放完毕
        self._event.set()

    def _output(self):
        while self.is_alive:
            try:
                msg = self._sub_proc.stdout.read()
                if msg == '':
                    continue
                print msg
            except IOError:
                pass

    @property
    def is_alive(self):
        if self._sub_proc is None:
            return False
        return self._sub_proc.poll() is None

    def quit(self):
        if not self.is_alive:
            return
        try:
            os.killpg(os.getpgid(self._sub_proc.pid), signal.SIGKILL)
        except:
            pass

    def start(self, url):
        self._run_player(['-volume', str(self._volume), url])

    def pause(self):
        self._send_command('pause')

    def volumeUpDown(self, volume):
        if volume == '=':
            if self._volume < 100:
                self._volume += 5
            self._send_command('volume %d' % self._volume)
        elif volume == '-':
            if self._volume > 0:
                self._volume -= 5
            self._send_command('volume %d' % self._volume)

    def _send_command(self, cmd, expect=None):
        if not self.is_alive:
            #raise NotPlayingError()
            return
        cmd += '\n'
        try:
            self._sub_proc.stdin.write(cmd)
            self._sub_proc.stdin.flush()
        except(TypeError, UnicodeEncodeError):
            self._sub_proc.stdin.write(cmd.encode('utf-8', 'ignore'))
        if not expect:
            return


class NotPlayingError(Exception):
    pass

def main():
    e = threading.Event()
    player = MPlayer(e, 50)
    #player.start('http://emo.luoo.net/low/luoo/radio723/02.mp3')
    player.start('http://ftp.flash1890.com/audio/shenghuo/naozhong/8.mp3')
    e.wait()
    player.quit()

if __name__=="__main__":
    main()

