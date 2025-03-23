import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from GatherTarget import GatherTarget
from NpsPocExp import NpsScan


class core:
    file1 = ""
    file2 = ""
    file3 = ""
    @staticmethod
    def active_scan_target():
        """
        目前只做了hunter的动态扫描
        :return:
        """
        # 获取hunter的扫描结果
        target_set = GatherTarget.hunter_scan()

        # 可以扩展其它的测绘工具

        return target_set

    @staticmethod
    def read_file(file):
        target_set = set()
        with open(file, 'r') as f:
            for line in f:
                target_set.add(line.strip())
        return list(target_set)

    @staticmethod
    def check_target(target_set):
        # 2 目标检测
        info_list = []
        lock = threading.Lock()

        with ThreadPoolExecutor(max_workers=25) as executor:
            results = [executor.submit(NpsScan.th_single_target_process, url, info_list, lock) for url in target_set]
            [res for res in results] # 阻塞

        return info_list

    @staticmethod
    def get_file_name(file_type=1):
        # 获取配置文件
        with open("config", "r") as f:
            config = json.loads(f.read())
        if file_type == 1:
            if not core.file1:
                core.file1 = os.path.join(config["save_dir"], "info_list_" + str(int(time.time())) + "_.txt")
            path = core.file1
        elif file_type == 2:
            if not core.file2:
                core.file2 = os.path.join(config["save_dir"], "http_proxy_" + str(int(time.time())) + "_.txt")
            path = core.file2
        elif file_type == 3:
            if not core.file3:
                core.file3 = os.path.join(config["save_dir"], "socks5_proxy_" + str(int(time.time())) + "_.txt")
            path = core.file3
        else:
            path = "none.txt"
        return path

    @staticmethod
    def save_result(info_list):

        # 存储总状态文件
        path = core.get_file_name(1)
        with open(path, "a") as f:
            for item in info_list:
                f.write(json.dumps(item)+'\n')

        # 解析结果
        http_, socks_ = [], []
        for item in info_list:
            if "alive_proxies" in item:
                if item["alive_proxies"]["http"]:
                    for ob in item["alive_proxies"]["http"]:
                        if "proxy" in ob:
                            http_.append(ob["proxy"])
                if item["alive_proxies"]["socks5"]:
                    for ob in item["alive_proxies"]["socks5"]:
                        if "proxy" in ob:
                            socks_.append(ob["proxy"])
        # print(http_)
        # print(socks_)
        # 存储http代理结果文件
        if http_:
            path = core.get_file_name(2)
            with open(path, 'a') as f:
                for item in http_:
                    f.write(item+'\n')

        # 存储socks5代理文件
        if socks_:
            path = core.get_file_name(3)
            with open(path, 'a') as f:
                for item in socks_:
                    f.write(item+'\n')

