import requests,json

authcode = ""

def post_zabbix(data):
    headers = {"Content-Type":"application/json"}
    raw = {}
    try:
        ret = requests.post("http://172.16.11.35:81/zabbix/api_jsonrpc.php", headers=headers, data=json.dumps(data))
        raw = json.loads(ret.content)
    except Exception as e:
        print e.message
        return -1
    if raw.has_key("error"):
        print(raw["error"])
        return -1
    res = raw["result"]
    return res


def get_auth_session():
    data = {
            "jsonrpc":"2.0",
            "method":"user.login",
            "params":
                    {
                        "user": "Admin",
                        "password": "zabbix"
                    },
            "id":0
        }
    result = post_zabbix(data)
    return result

def sql_zabbix_query(sql):
    try:
        db = MySQLdb.connect("127.0.0.1", "root", "zabbix", "zabbix", charset='utf8')
        cursor = db.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
    except Exception as e:
        result = []
    finally:
        cursor.close()
        db.close()
    return result


def get_wroming(authcode):
    if authcode == "":
        authcode = get_auth_session()

    data = {
        "jsonrpc": "2.0",
        "method": "trigger.get",
        "params": {
            "output": [
                "triggerid",
                "description",
                "status",
                "value",
                "priority",
                "lastchange",
                "recovery_mode",
                "hosts",
                "state"
            ],
            "selectHosts": "name",
            "filter": {
                "value": 1,
                "status": 0
                },
        },
        'auth': authcode,
        'id': '0'
    }
    result = post_zabbix(data)
    return result

def get_host(hostid):
    data = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": [
                "name"
            ],
            "hostids": "%s" % (hostid)
        },
        "auth": "58617b0ab6a311acd60af17c61c4ab2c",
        "id": 0
    }
    result = post_zabbix(data)
    return result


def getHosts(authcode):
    if authcode == "":
        authcode = get_auth_session()

    data = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": [
                "hostid",
                "host"
            ]
        },
        "id": 0,
        "auth": authcode,

    }

    result = post_zabbix(data)
    return result

import paramiko
try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print "start to connect"
    client.connect("172.16.11.31", 22, username="root", password="root123", timeout=5)
    print "connect ok"
except:
    print "err"