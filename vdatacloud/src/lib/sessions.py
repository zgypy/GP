# coding=utf-8

import os
import time
import hashlib
import base64
import config
import threading

# 字典的格式为{"xxxxxxxxxx":{""}}
__session_dict = {}
__lock = threading.RLock()


def get_session(user_name):
    """
    :param user_name:
    :return: string, 返回一个session_id
    """

    session_id = ""
    __lock.acquire()
    try:
        now = time.time()
        if len(__session_dict) >= 10000:
            for i in __session_dict:
                if now >= __session_dict[i][0]:
                    __session_dict.pop(i)
        while True:
            session_id = base64.b64encode(os.urandom(32)).decode()
            if session_id in __session_dict.keys():
                continue
            break
        __session_dict[session_id] = {"user_name": user_name, "expired_time": now + 600, "status": 0}
    except:
        pass
    finally:
        __lock.release()
    return session_id


def login(user_name, session_id, client_hash_value):
    """
    :param user_name:
    :param session_id:
    :param client_hash_value:
    :return:
    """

    conf_user_name = config.get('http_user')
    if conf_user_name != user_name:
        return False, "用户名或密码错误!"

    password = config.get('http_pass')

    hash256 = hashlib.sha256()
    hash_key = user_name + password + session_id
    hash256.update(hash_key.encode())
    server_hash_value = hash256.hexdigest()

    __lock.acquire()
    try:
        now = time.time()
        if session_id not in __session_dict:
            return False, "session expired!"
        else:
            if time.time() > __session_dict[session_id]['expired_time']:
                __session_dict.pop(session_id)
                return False, "session expired!"

        if client_hash_value != server_hash_value:
            return False, "用户名或密码错误!"

        __session_dict[session_id]['expired_time'] = now + 600
        __session_dict[session_id]['status'] = 1
        return True, "OK"
    finally:
        __lock.release()


def check_session(session_id):
    __lock.acquire()
    try:
        now = time.time()
        if session_id not in __session_dict:
            return False, "session expired!"
        else:
            if time.time() > __session_dict[session_id]['expired_time']:
                __session_dict.pop(session_id)
                return False, "session expired!"
        if not __session_dict[session_id]['status']:
            return False, "session not login!"
        __session_dict[session_id]['expired_time'] = now + 600
        return True, "OK"
    finally:
        __lock.release()


def logout(session_id):
    __lock.acquire()
    try:
        if session_id not in __session_dict:
            return False, "session not exists!"
        __session_dict.pop(session_id)
        return True, "OK"
    finally:
        __lock.release()
