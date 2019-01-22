# -*- coding:UTF-8 -*-

import psycopg2
import MySQLdb
from flask import Flask
import config
app = Flask(__name__)


def sql_exec(sql, param=()):
    try:
        conn = psycopg2.connect(database="postgres", user="postgres", password="postgres", host="127.0.0.1",
                            port="5432")
        cur = conn.cursor()
        cur.execute(sql, param)
        result = 0
    except Exception as e:
        app.logger.error(e)
        result = -1
    finally:    
        cur.close()
        conn.commit()
        conn.close()
    return result


def sql_query(sql, param=()):
    try:
        conn = psycopg2.connect(database="postgres", user="postgres", password="postgres", host="127.0.0.1",
                            port="5432")
        cur = conn.cursor()
        cur.execute(sql, param)
        result = cur.fetchall()
    except Exception as e:
        app.logger.error(e)
        result = []
    finally:    
        cur.close()
        conn.commit()
        conn.close()
    return result



def sql_zabbix_query(sql):
    try:
        db = MySQLdb.connect("127.0.0.1", "root", "zabbix", "zabbix", charset='utf8' )
        cursor = db.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
    except Exception as e:
        app.logger.error(e)
        result = []
    finally:
        cursor.close()
        # 关闭数据库连接
        db.close()
    return result

