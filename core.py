import json
import os
import threading
import time

from GatherTarget import GatherTarget
from NpsPocExp import NpsScan


def active_scan_target():
    """
    目前只做了hunter的动态扫描
    :return:
    """
    # 获取hunter的扫描结果
    target_set = GatherTarget.hunter_scan()

    # 可以扩展其它的测绘工具

    return target_set


def read_file(file):
    target_set = set()
    with open(file, 'r') as f:
        for line in f:
            target_set.add(line.strip())
    return target_set


def check_target(target_set):
    # 2 目标检测
    info_list = []
    lock = threading.Lock()
    th_list = []
    for url in target_set:
        th = threading.Thread(target=NpsScan.th_single_target_process, args=(url, info_list, lock))
        th_list.append(th)
        th.start()
    # 确保线程完成
    [th.join() for th in th_list]
    return info_list


def get_file_name(file_type=1):
    # 获取配置文件
    with open("config", "r") as f:
        config = json.loads(f.read())
    if file_type == 1:
        path = os.path.join(config["save_dir"], "info_list_" + str(int(time.time())) + "_.json")
    elif file_type == 2:
        path = os.path.join(config["save_dir"], "http_proxy_" + str(int(time.time())) + "_.txt")
    elif file_type == 3:
        path = os.path.join(config["save_dir"], "socks5_proxy_" + str(int(time.time())) + "_.txt")
    else:
        path = "none.txt"
    return path


def save_result(info_list):

    # 存储总状态文件
    path = get_file_name(1)
    with open(path, "w") as f:
        f.write(json.dumps(info_list))

    # 解析结果
    http_, socks_ = [], []
    for item in info_list:
        if "alive_proxies" in item:
            if item["alive_proxies"]["http"]:
                for ob in item["alive_proxies"]["http"]:
                    http_.append(ob["proxy"])
            if item["alive_proxies"]["socks5"]:
                for ob in item["alive_proxies"]["socks5"]:
                    socks_.append(ob["proxy"])
    print(http_)
    print(socks_)
    # 存储http代理结果文件
    if http_:
        path = get_file_name(2)
        with open(path, 'w') as f:
            for item in http_:
                f.write(item+'\n')

    # 存储socks5代理文件
    if socks_:
        path = get_file_name(3)
        with open(path, 'w') as f:
            for item in socks_:
                f.write(item+'\n')

