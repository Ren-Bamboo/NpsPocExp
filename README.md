# NpsPocExp工具

## 工具说明

该工具利用NPS漏洞实现有效代理抓取。

## 环境配置

~~~
pip install -r requirements.txt
~~~

## 使用方法

~~~
usage: main.py [-h] [-f FILE] [-u URL] [-a]

    _   ______  _____    ____  ____  ______   _______  __ ____ 
   / | / / __ \/ ___/   / __ \/ __ \/ ____/  / ____/ |/ // __ 
  /  |/ / /_/ /\__ \   / /_/ / / / / /      / __/  |   // /_/ /
 / /|  / ____/___/ /  / ____/ /_/ / /___   / /___ /   |/ ____/ 
/_/ |_/_/    /____/  /_/    \____/\____/  /_____//_/|_/_/      

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  url文件
  -u URL, --url URL     单个url
  -a, --active          使用主动获取模式
~~~

**注意：三个参数独立，不能共同使用**

~~~
-f 参数指定一个文件，文件内是需要目标url
-u 参数指定单一url
-a 表示使用主动模式，自动从空间测绘平台获取目标url（目前只支持hunter，需要配置config文件）
~~~

**使用示例：**

~~~
python main.py -a

python main.py -u https://www.test.com

python main.py -f filePath
~~~

## 配置文件

**config**文件目前主要配置了**结果的存储位置**、**hunter的API**以及**利用hunter API的抓取数量**

~~~

{	

  "hunter_api_key":"",  	# hunter的api-key，注册后有每日的免费积分
   
  "save_dir": "./data",  	# 结果的存储位置

  "target_number": 50           # 利用api 抓取的数量，按需设置，一般1积分对应一条数据
}
~~~

## 结果说明

该脚本跑完后，最多生成4个文件

~~~
target_url_timestamp_.txt		存储了测试的目标url
info_list_timestamp_.json		存储了有效目标的状态
http_proxy_timestamp_.txt		存储了可用的http代理
socks5_proxy_timestamp_.txt		存储了可用的socks5代理
~~~

**info_list_timestamp_.json**

该文件存储了针对所有有效目标的测试结果，包括存在的漏洞类型、出网情况、可用代理等。记录该文件的原因是：目标或许没有直接可以利用的http、socks代理，但能通过tcp隧道等进行深入利用，目前该版本并没有实现该功能。

~~~
w_flag 	表示弱口令
u_flag 	表示未授权
url 	表示目标
out 	测试是否能访问 https://www.facebook.com
in 	测试是否能访问 https://www.baidu.com
~~~

示例结果(info_list_timestamp_.json)：

~~~json
{
    "w_flag": true,
    "u_flag": true,
    "url": "http://example:8080",
    "alive_proxies": {
        "http": [
            {
                "proxy": "http://example:7002",
                "status": {
                    "out": false,
                    "in": true
                }
            }
        ],
        "socks5": [
            {
                "proxy": "socks5://example:7001",
                "status": {
                    "out": false,
                    "in": true
                }
            },
            {
                "proxy": "socks5://example:7003",
                "status": {
                    "out": false,
                    "in": true
                }
            }
        ]
    }
}
~~~

