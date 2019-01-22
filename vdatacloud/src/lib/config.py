# -*- coding: utf-8 -*-

"""
@Create_date: 2017-08-01
@Author: tangcheng
@Email: tangcheng@cstech.ltd
@description: 配置管理模块
Copyright (c) 2017-2018 HangZhou CSTech.Ltd. All rights reserved.
"""

import os
import sys
import traceback
import logging

__module_path = os.path.abspath(os.path.dirname(__file__))

__cfg_path = os.path.abspath(os.path.join(__module_path, '..' + os.sep + 'conf'))
# __config_file = os.path.join(__cfg_path, '.' + os.sep + 'sdsdwebsrv.conf')
__config_file = os.path.join(__cfg_path, 'sdsdwebsrv.conf')
__root_path = os.path.abspath(os.path.join(__module_path, '..' + os.sep))
__run_path = os.path.abspath(os.path.join(__module_path, '..' + os.sep + 'run'))
__data_path = os.path.abspath(os.path.join(__module_path, '..' + os.sep + 'data'))
__bin_path = os.path.abspath(os.path.join(__module_path, '..' + os.sep + 'bin'))
__log_path = os.path.abspath(os.path.join(__module_path, '..' + os.sep + 'logs'))
__tmp_path = os.path.abspath(os.path.join(__module_path, '..' + os.sep + 'tmp'))
__web_root = os.path.abspath(os.path.join(__module_path, '..' + os.sep + 'ui'))

__data = {}

print __config_file


def load():
    global __data

    try:
        with open(__config_file) as f:
            for line in f:
                line = line.strip()

                if len(line) < 1:
                    continue
                if line[0] == "#":
                    continue
                elif line[0] == ";":
                    continue
                try:
                    pos = line.index('=')
                except ValueError:
                    continue
                key = line[:pos].strip()
                value = line[pos + 1:].strip()
                __data[key] = value
    except Exception as e:
        logging.error("Load configuration failed: %s:\n%s" % (repr(e), traceback.format_exc()))
        sys.exit(1)


def get_run_path():
    """
    :return: 返回run目录
    """
    return __run_path


def get_cfg_path():
    """获得conf目录路径"""
    return __cfg_path


def get_module_path():
    return __module_path


def get_root_path():
    return __root_path


def get_data_path():
    return __data_path


def get_bin_path():
    return __bin_path


def get_log_path():
    return __log_path


def get_tmp_path():
    return __tmp_path


def get_web_root():
    return __web_root


def get_pid_file():
    global __run_path
    return "%s/cm_server.pid" % __run_path


def get(key):
    return __data[key]


def set(key, value):
    __data[key] = value


def getint(key):
    return int(__data[key])


def has_key(key):
    return key in __data


def get_all():
    return __data
