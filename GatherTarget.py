import os

import requests
import json
from datetime import datetime, timedelta
import time


class GatherTarget:
    @staticmethod
    def hunter_scan():
        url = "https://hunter.qianxin.com/openApi/search?api-key={}" \
              "&search=d2ViLmJvZHk9Ii9sb2dpbi92ZXJpZnkiJiZ3ZWIuYm9keT0ic2VyaWFsaXplQXJyYXkoKSI=" \
              "&page={}&page_size=10" \
              "&is_web=1&port_filter=false" \
              "&start_time={}" \
              "&end_time={}"

        # 获取API-key
        with open("config", "r") as f:
            config = json.loads(f.read())
        api_key = config["hunter_api_key"]

        # 限制日志，提取前1-15天的信息
        start_data = (datetime.now()-timedelta(days=15)).strftime("%Y-%m-%d")
        end_date = (datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d")

        count = 0
        test_count = config["target_number"]/10
        target_url = set()
        while count < test_count:
            # 拼接最后的请求url
            url = url.format(api_key, count+1, start_data, end_date)
            try:
                res = requests.get(url)
                if res.json()["code"] == 401 or res.json()["code"] == 400:
                    continue
                elif res.json()["code"] == 429:
                    print("请求太多进行暂停")
                    time.sleep(2)
                    continue
            except Exception:
                continue
            count += 1
            target_url.update([item["url"] for item in res.json()["data"]["arr"]])

            if int(res.json()["data"]['rest_quota'].split("：")[-1]) < 10:
                break

        # 本地保存一份
        path = os.path.join(config["save_dir"], "target_url_"+str(int(time.time()))+"_.txt")

        with open(path, 'w') as f:
            for t in target_url:
                f.write(t+"\n")

        return target_url
