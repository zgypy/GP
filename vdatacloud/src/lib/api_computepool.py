# -*- coding:UTF-8 -*-

from flask import Blueprint, render_template, request, session, make_response, jsonify, Flask
from sshremote import remote_ssh
import post_data
import json
import base64
import os
from copy import deepcopy

app = Flask(__name__)

handle_computepool = Blueprint('api_computepool', __name__)
route = handle_computepool.route


def make_result(code, data):
    result = json.dumps({"status": code, "data": data})
    res = make_response(result)
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res

@route('/cpool/host/find', methods=['POST'])
def computepool_host_find():
    params = json.loads(request.data)
    # pool_name = params.get("cpool_name", "")
    gi_home_path = params.get("gi_home_path", "")
    ora_home_path = params.get("ora_home_path", "")
    gi_name = params.get("gi_name", "")
    ora_name = params.get("ora_name", "")
    node_ip_port = params.get("node_ip_port", "")
    # ssh_method = params.get("ssh_method", "")
    root_passwd = params.get("root_passwd", "")

    root_passwd = base64.b64decode(root_passwd)

    node_ip = node_ip_port.split(":")[0]
    # 检查对应路径是否存在
    cmd = "/opt/cstech/sureinfo.sh %s %s %s %s"
    ret = remote_ssh(node_ip, "root", root_passwd, cmd % (gi_home_path, ora_home_path, gi_name, ora_name))
    if ret == -1:
        res = make_result(-1, "GI_home路径查找失败")
        return res
    
    gz = {"0": "gi_homepath", "1": "ora_homepath", "2": "gi_name", "3": "ora_name"}
    data = {}
    for i in ret:
        state_list = i.strip("\n").split(":")
        for idx, val in enumerate(state_list):
            if int(val) == -1:
                data[gz[idx]] = "not exsit"
    if len(data) > 0:
        res = make_result(-1, data)
        return res

    cmd = "/"+gi_home_path+"/"+gi_name+"/bin/srvctl config nodeapps -a|grep -v 'Network exists:' | awk '{print $3 $6}'"
    ret = remote_ssh(node_ip, "root", root_passwd, cmd)
    if ret == -1:
        res = make_result(-1, "执行远程脚本获取主机节点资源失败")
        return res

    result = []
    scan_ip = ""
    for lines in ret:
        line = lines.split(",")
        name = line[-1].strip("\n")
        vip = line[0].strip("/").split("/")[2]
        cmd_public = "traceroute -m 1 %s | head -1 | cut -d'(' -f2 | cut -d')' -f1" % name
        ret = remote_ssh(node_ip, "root", root_passwd, cmd_public)
        if ret == -1:
            public_ip = ""
        else:
            public_ip = (",".join(ret)).replace("\n", "")

        m_name = name[:-2]+"adm"+name[len(name)-2:]
        cmd_mip = "cat /etc/hosts | grep %s|grep -v 'ilom'|awk '{print $1}'" % m_name
        ret = remote_ssh(node_ip, "root", root_passwd, cmd_mip)
        if ret == -1:
            m_ip = public_ip
        else:
            m_ip = ret[0].strip("\n")

        if scan_ip == "":
            cmd_scan = "/" + gi_home_path + "/" + gi_name + "/bin/srvctl config scan|grep -v 'SCAN name:'|awk '{print $6}'"
            ret = remote_ssh(node_ip, "root", root_passwd, cmd_scan)
            if ret == -1:
                pass
            else:
                for i in ret:
                    scan_ip = scan_ip + i.strip("\n").split("/")[-1] + ","

        data = {"name": name, "vip": vip, "public_ip": public_ip, "m_ip": m_ip}
        result.append(data)
    result.append({"scan_ip": scan_ip.strip(",")})

    res = make_result(0, result)
    return res


@route('/cpool/srvpool/find', methods=['POST'])
def computepool_srvpool_find():
    params = json.loads(request.data)
    node_ip = params.get("node_ip", "")
    gi_name = params.get("gi_name", "")
    root_passwd = params.get("root_passwd", "")

    root_passwd = base64.b64decode(root_passwd)

    cmd = "su - %s -c 'srvctl config srvpool'" % gi_name
    ret = remote_ssh(node_ip, "root", root_passwd, cmd)
    if ret == -1:
        res = make_result(-1, "查找srvpool资源池失败")
        return res
    if len(ret) < 6:
        res = make_result(-1, "数据库集群状态异常")
        return res

    result = []
    for i in range(len(ret)/3):
        lines = ret[i*3:i*3+3]
        data = {}
        for idx, j in enumerate(lines):
            if idx == 0:
                pool_name = j.split(":")[-1].strip()
                data["dbpool_name"] = pool_name
            elif idx == 1:
                importance, min_v, max_v = [x.split(":")[-1].strip() for x in j.split(",")]
                data["importance"] = importance
                data["min_v"] = min_v
                data["max_v"] = max_v
            else:
                live_host = j.split(":")[-1].strip()
                data["live_host"] = live_host
        result.append(data)
    res = make_result(0, result)
    return res


# aorcl orcl porcl rac vastdb
# AORCL|aorcl2|pga_aggregate_target|3261071360  [{"aorcl":{"aorcl1":{"cpu":0, "pga":23131, "sga":23234}}}]
# AORCL|aorcl2|sga_target|9784262656
# AORCL|aorcl2|cpu_count|0
# AORCL|aorcl1|pga_aggregate_target|3261071360
# AORCL|aorcl1|sga_target|9784262656
# AORCL|aorcl1|cpu_count|0
# ORCL|orcl1|pga_aggregate_target|4568645632
# ORCL|orcl1|sga_target|13706985472
# ORCL|orcl1|cpu_count|0
# ORCL|orcl2|pga_aggregate_target|4568645632
# ORCL|orcl2|sga_target|13706985472
# ORCL|orcl2|cpu_count|0
# porcl is not running
# rac is not running
# vastdb is not running
@route('/cpool/db/find', methods=['POST'])
def computepool_db_find():
    params = json.loads(request.data)
    node_ip = params.get("node_ip", "")
    root_passwd = params.get("root_passwd", "")
    ora_name = params.get("ora_name", "")
    root_passwd = base64.b64decode(root_passwd)

    cmd = "su - %s -c '/opt/cstech/db_sga_pga_cpu.sh'" % ora_name
    ret = remote_ssh(node_ip, "root", root_passwd, cmd)
    if ret == -1:
        res = make_result(-1, "查找db资源失败")
        return res

    ret = remote_ssh(node_ip, "root", root_passwd, "cat /tmp/db_result.tmp")
    if ret == -1:
        res = make_result(-1, "查找db资源失败")
        return res

    db_list = ret[0].strip().strip("\n").split()
    data = []

    # ORCL | orcl2 | pga_aggregate_target | 4568645632
    # ORCL | orcl2 | sga_target | 13706985472
    # ORCL | orcl2 | cpu_count | 0
    raw = {"instance_name":""}
    for i in ret[1:]:
        line = i.strip("\n").strip().split("|")
        if len(line) >3:
            if len(raw) >= 5:
                da = deepcopy(raw)
                data.append(da)
                raw.clear()
                raw["instance_name"] = ""

            elif raw["instance_name"] != line[1]:
                raw["instance_name"] = line[1]
                raw["db_name"] = line[0].lower()

            if line[2] == "pga_aggregate_target":
                raw["pga"] = line[3]
            elif line[2] == "sga_target":
                raw["sga"] = line[3]
            else:
                raw["cpu"] = line[3]
            if line[0].lower() in db_list:
                db_list.remove(line[0].lower())
        else:
            line = line[0].split()
            da = {"db_name":line[0], "instance_name":"N/A", "pga":"N/A", "sga":"N/A", "cpu":"N/A"}
            data.append(da)
            if line[0].lower() in db_list:
                db_list.remove(line[0].lower())

    res = make_result(0, [{"data": data, "err_db":db_list}])
    return res


@route('/cpool/create', methods=['POST'])
def computepool_create():
    params = json.loads(request.data)
    base_info = params.get("base_info", "")
    host_info = params.get("host_info", "")
    dbpool_info = params.get("dbpool_info", "")
    db_info = params.get("db_info", "")

    if not (isinstance(base_info, dict) or isinstance(host_info, dict), isinstance(dbpool_info, dict), isinstance(db_info, dict)):
        res = make_result(-1, "args is not avaliable")
        return res

    pool_name = base_info["cpool_name"]
    gi_home = base_info["gi_home_path"]
    ora_home = base_info["ora_home_path"]
    gi_name = base_info["gi_name"]
    ora_name = base_info["ora_name"]
    node_ip = base_info["nodeIp"]
    root_passwd = base_info["root_passwd"]
    sql_base = "insert into computepool(pool_name,gi_homepath,ora_homepath,gi_name,ora_name,node_ip,rootpasswd) values(%s,%s,%s,%s,%s,%s,%s)"
    ret = post_data.sql_exec(sql_base, (pool_name,gi_home,ora_home,gi_name,ora_name,node_ip,root_passwd))
    if ret == -1:
        res = make_result(-1, "保存计算资源池信息失败")
        return res

    for host in host_info:
        host_name = host["name"]
        vip = host["vip"]
        scan_ip = host["public_ip"]
        m_ip = host["m_ip"]
        password = host["rootPassWord"]
        root_passwd = base64.b64decode(password)

        sql_host = "insert into cpool_host(pool_name,host_name,vip,scan_ip,m_ip,root_passwd) values (%s,%s,%s,%s,%s,%s)"
        ret = post_data.sql_exec(sql_host, (pool_name,host_name,vip,scan_ip,m_ip,root_passwd))
        if ret == -1:
            res = make_result(-1, "保存计算资源池信息失败")
            return res

    for dbpool in dbpool_info:
        dblevel = dbpool["importance"]
        live_host = dbpool["live_host"]
        min_v = dbpool["min_v"]
        max_v = dbpool["max_v"]
        dbpool_name = dbpool["dbpool_name"]
        sql_dbpool = "insert into dbpool(pool_name,dbpool_name,dblevel,live_host,min_v,max_v) values (%s,%s,%s,%s,%s,%s)"
        ret = post_data.sql_exec(sql_dbpool, (pool_name, dbpool_name, dblevel, live_host, min_v, max_v))
        if ret == -1:
            res = make_result(-1, "保存计算资源池信息失败")
            return res


    for db in db_info:
        db_name = db["db_name"]
        instance_name = db["instance_name"]
        sga = db["sga"]
        cpu_cnt = db["cpu"]
        pga = db["pga"]
        sql_db = "insert into db(pool_name,db_name,instance_name,sga_size,cpu_core,pga_size) values (%s,%s,%s,%s,%s,%s)"
        ret = post_data.sql_exec(sql_db, (pool_name, db_name, instance_name, sga, cpu_cnt, pga))
        if ret == -1:
            res = make_result(-1, "保存计算资源池信息失败")
            return res

    res = make_result(0, "保存计算资源池信息完成")
    return res



@route('/cpool/name/list', methods=['GET'])
def computepool_name():
    sql_str = "select pool_name from computepool;"
    sql_ret = post_data.sql_query(sql_str)
    data = []
    for i in sql_ret:
        data.append(i[0])
    res = make_result(0, data)
    return res


# [u'vd01db01@10.10.3.1@CentOS Linux release 7.3.1611 (Core) @Y@528013780@44@0@5:36@200GB\n', u'172.16.11.32\n']
def get_host_detail(raw):
    data = []
    for i in raw:
        node = i.strip("\n").split("@")
        da = {
            "node_name": node[0],
            "node_ip": node[1],
            "os": node[2],
            "cluster_state": node[3],
            "host_state": "Y",
            "memery": node[4],
            "cpu_cnt": node[5],
            "file_system": node[6]
        }
        data.append(da)
    return data


@route('/cpool/detail/list', methods=['GET'])
def computepool_list():
    sql_str = """select count(pool_name) from computepool UNION ALL SELECT count(host_id) from cpool_host
                 UNION ALL select count(dbpool_id) from dbpool UNION ALL select count(db_id) from db
                 UNION ALL select count(instance_name) from db"""
    sql_ret = post_data.sql_query(sql_str)
    if len(sql_ret) <= 0:
        res = make_result(0, {"cp_cnt": 0, "dbp_cnt": 0, "db_cnt": 0, "ins_cnt": 0, "host_cnt": 0})
        return res

    cnt = {
            "cp_cnt": sql_ret[0][0],
            "host_cnt": sql_ret[1][0],
            "dbp_cnt": sql_ret[2][0],
            "db_cnt": sql_ret[3][0],
            "ins_cnt": sql_ret[4][0]
           }

    sqlstr = "select pool_name,node_ip,rootpasswd, create_time from computepool;"
    ret = post_data.sql_query(sqlstr)
    raw = []
    for i in ret:
        data = {}
        node_ip = i[1]
        root_passwd = base64.b64decode(i[2])
        ret = remote_ssh(node_ip, "root", root_passwd, "/opt/cstech/host_info.sh")
        if ret == -1:
            res = make_result(-1, "执行远程脚本获取主机节点资源失败")
            return res
        info = get_host_detail(ret)
        data[i[0]] = info
        raw.append(data)
    res = make_result(0, {"cnt": cnt, "dt":raw})
    return res


@route('/dbpoolist', methods=['POST'])
def dbpool_list():
    params = json.loads(request.data)
    cpool_name = params.get("cpool_name", "")

    sql_str = "select pool_name,dbpool_name,live_host,dblevel,min_v,max_v from dbpool where pool_name=%s"
    sql_ret = post_data.sql_query(sql_str, (cpool_name,))
    data = []
    for i in sql_ret:
        row = {
            "cpool_name": i[0],
            "dbpool_name": i[1],
            "live_host": i[2],
            "import_level": i[3],
            "min_v": i[4],
            "max_v": i[5],
        }
        if i[2] == "":
            row["instance_cnt"] = 0
        else:
            row["instance_cnt"] = len(i[2].split(","))
        data.append(row)
    res = make_result(0, data)
    return res


@route('/dbpool/add', methods=['POST'])
def dbpool_add():
    """可能会有高级选项，需要执行多条命令"""
    params = json.loads(request.data)
    pool_name = params.get("pool_name", "")
    level = params.get("level", "")
    min_cnt = params.get("min_cnt", "")
    max_cnt = params.get("max_cnt", "")

    sqlstr = "select node_ip,rootpasswd,gi_homepath,gi_name from computepool where pool_name=%s"
    sqlret = post_data.sql_query(sqlstr, (pool_name,))
    
    if len(sqlret) == 0:
        res = make_result(-1, "满足要求的数据不存在或获取失败")
        return res

    node_ip = sqlret[0][0].split(":")[0]
    root_passwd = sqlret[0][1]
    gi_home_path = sqlret[0][2] + "/" + sqlret[0][3]
    cmd = "%s/bin/srvctl add srvpool -g %s -l %s -u %s -i %s"
    ret = remote_ssh(node_ip, "root", root_passwd, cmd % (gi_home_path, pool_name,int(min_cnt),int(max_cnt),int(level)))
    if ret == -1:
        res = make_result(-1, "远程添加DB资源池失败")
        return res

    res = make_result(0, "远程添加DB资源池完成")
    return res
