# -*- coding:UTF-8 -*-

import os
from flask import Blueprint, render_template, request, send_from_directory, Flask

app = Flask(__name__)

__module_path = os.path.abspath(os.path.dirname(__file__))
__webroot = os.path.abspath(os.path.join(__module_path, '..' + os.sep + 'webroot'))

static_handle = Blueprint('static_handle', __name__, static_folder=__webroot)
route = static_handle.route


@route('/', methods=['GET'])
@route('/index.html', methods=['GET'])
def web_index():
    return static_handle.send_static_file('index.html')


@route('/static/<path:relative_path>', methods=['GET'])
def static_file(relative_path):
    return send_from_directory(__webroot, 'static/' + relative_path)
