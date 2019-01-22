# -*- coding:UTF-8 -*-

import paramiko
from flask import Flask
import config
import xmlrpclib
import socket
import os
import threading 

app = Flask(__name__)

counter_lock = threading.Lock()


def remote_ssh(sys_ip, username, password, cmd):
    """需要在调用前获取到用户名密码或者秘钥"""
    global client, result
    print "ip:", sys_ip, "name:", username, "password:", password, "cmd:", cmd
    counter_lock.acquire()
    try:
        # 创建ssh客户端
        client = paramiko.SSHClient()
        # 第一次ssh远程时会提示输入yes或者no
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 密码方式远程连接
        client.connect(sys_ip, 22, username=username, password=password, timeout=15)
        # 互信方式远程连接
        # key_file = paramiko.RSAKey.from_private_key_file("/root/.ssh/id_rsa")
        # ssh.connect(sys_ip, 22, username=username, pkey=key_file, timeout=20)
        # 执行命令
        stdin, stdout, stderr = client.exec_command(cmd, timeout=25)
        err = stderr.read()
        if err and err != "stty: standard input: Inappropriate ioctl for device\n":
            app.logger.error(err)
            result = -1
        else:
            # 获取命令执行结果,返回的数据是一个list
            result = stdout.readlines()
    except Exception as e:
        app.logger.error(e)
        result = -1
    finally:
        client.close()
        counter_lock.release()
        return result


def remote_xmlrpc(tp, node_ip, cmd):
    """根据前端选择的集群和节点，来确定对应节点的IP"""
    auth_code = "a7PJ4knSuZWmZXUfEZKdpc7u1OUP72qP"
    ret = None
    xmlrpc_port = config.get('xmlrpc_port')
    try:
        server = xmlrpclib.ServerProxy("http://"+node_ip+":"+xmlrpc_port, allow_none=True)
        socket.setdefaulttimeout(25)
        # 传入认证参数
        if tp == "adldisk":
            # attach detach load
            ret = server.adlDisk(cmd, auth_code)
        elif tp == "unloaddisk":
            ret = server.UnLoadDisk(cmd, auth_code)
        elif tp == "get_process_state":
            ret = server.ShowProcessState(auth_code)
        elif tp == "get_store_node_list":
            ret = server.ShowStoreNodeList(auth_code)
        elif tp == "get_compute_node_list":
            ret = server.ShowComputeNodeList(auth_code)
    except Exception as e:
        app.logger.error(e)
    finally:
        socket.setdefaulttimeout(None)
        return ret


def remote_download(sys_ip, username, password, remote_path):
    global cli, ret1, ret2
    try:
        cli = paramiko.Transport(sys_ip, 22)
        cli.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(cli)
        remotepath = remote_path
        localpath = '/opt/cstech/logs/'+sys_ip+"_"+remote_path.split("/")[-1]

        if not os.path.isdir("/opt/cstech/logs"):
            os.mkdir("/opt/cstech/logs")

        if os.path.exists(localpath):
            os.remove(localpath)

        sftp.get(remotepath, localpath)  # 上传文件和下载差别只有get/put和本地与远程文件的路径不同
        ret1, ret2 = 0, localpath
    except Exception as e:
        app.logger.error(e)
        ret1, ret2 = -1, ""
    finally:
        cli.close()
        return ret1, ret2