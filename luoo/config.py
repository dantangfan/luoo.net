# -*- coding: utf-8 -*-
import os


keys = ['j', 'k', '-', '=', 'a', 's', 'd', 'n', 'b', 'q', '\r', ' ']
window_keys = ['j', 'k', 'a', 's', 'd', 'n', 'b', 'q', '\r']

def suicide():
    os.system('kill `pgrep luoo.py`')
