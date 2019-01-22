# -*- coding:UTF-8 -*-
import base64

from flask import Blueprint, request, make_response, Flask
from sshremote import remote_ssh
import post_data
import json
import config

from os import path,getcwd


app = Flask(__name__)

handle_modle = Blueprint('api_modle', __name__)
route = handle_modle.route


def make_result(code, data):
    result = json.dumps({"status": code, "data": data})
    res = make_response(result)
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res


@route('/upload', methods=['POST'])
def upload():
    f = request.files["file"]
    base_path = path.abspath(path.dirname(getcwd()))
    upload_path = path.join(base_path, 'uploads/')
    file_name = upload_path + f.filename
    try:
        f.save(file_name)
        res = make_result(0, "文件保存成功")
    except Exception as e:
        app.logger.error(e)
        res = make_result(-1, "上传文件失败")
    return res



@route('/compool/choice', methods=['POST'])
def compool_choice():
    params = json.loads(request.data)
    cpool_name = params.get("cpool_name", "")

    sql_str = "select m_ip,root_passwd from cpool_host where pool_name=%s limit 1;"
    sql_ret = post_data.sql_query(sql_str, (cpool_name,))
    
    if len(sql_ret) == 0:
        res = make_result(-1, "满足条件的数据不存在或获取失败")
        return res
    # print sql_ret[0][1]
    node_ip = sql_ret[0][0]
    root_passwd = sql_ret[0][1]
    cmd = "/opt/cstech/poolstat.sh"
    ret = remote_ssh(node_ip, "root", root_passwd, cmd)
    if ret == -1:
        res = make_result(-1, "远程获取资源失败")
        return res
    data = []
    for i in ret:
        raw = i.strip("\n").split("@")
        da = {
            "host_name": raw[0],
            "instance_cnt": raw[1],
            "big_page_free": raw[2],
            "cpu_idle": raw[3]
        }
        data.append(da)
    res = make_result(0, data)
    return res


@route('/save', methods=['POST'])
def modle_save():
    params = json.loads(request.data)
    cpool_name = params.get("cpool_name", "")
    sga = params.get("sga", "")
    pga = params.get("pga", "")
    cpu = params.get("cpu", "")
    ccsid = params.get("ccsid", "")
    cn_ccsid = params.get("cn_ccsid", "")
    data_disk_g = params.get("data_disk_g", "")
    log_disk_g = params.get("log_disk_g", "")
    redo_size = params.get("redo_size", "")
    archive = params.get("archive", "")
    dispose = params.get("dispose", "")
    rac_type = params.get("rac_type", "")
    hosts = params.get("hosts", "")
    db_v = params.get("db_v", "")
    monitor_u = params.get("monitor_u", "")

    sqlstr = """insert into modle(compool_name,sga,pga,cpu,ccsid ,
                            cn_ccsid,data_disk_g,log_disk_g,redo_size,
                            archive,dispose,rac_type,hosts,db_v,monitor_u)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
             """
    post_data.sql_exec(sqlstr, (cpool_name, sga, pga, cpu, ccsid,
                            cn_ccsid, data_disk_g, log_disk_g, redo_size,
                            archive, dispose, rac_type, hosts, db_v, monitor_u))
    res = make_result(0, "保存模板完成")
    return res