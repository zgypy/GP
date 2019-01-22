# -*- coding:UTF-8 -*-

import os
import app_log
from flask import Flask
from flask_cors import CORS
from static_handle import static_handle
from api_computepool import handle_computepool
from api_modle import handle_modle
import config


__module_path = os.path.abspath(os.path.dirname(__file__))
__static_folder = os.path.abspath(os.path.join(__module_path, '..' + os.sep + 'webroot'))

app = Flask(__name__, static_folder=__static_folder)
CORS(app, supports_credentials=True)

app.register_blueprint(static_handle, url_prefix='')
# app.register_blueprint(handle_user, url_prefix='/api/v1/users')
# app.register_blueprint(handle_overview, url_prefix='/api/v1/overview')
app.register_blueprint(handle_computepool, url_prefix='/api/v1/resourcepool')
# app.register_blueprint(handle_nodes, url_prefix='/api/v1/nodes')
# app.register_blueprint(handle_monitor, url_prefix='/api/v1/monitor')
app.register_blueprint(handle_modle, url_prefix='/api/v1/modle')


if __name__ == '__main__':
    app_log.init_log(app)
    config.load()
    app.run(host='0.0.0.0', port=8080)
