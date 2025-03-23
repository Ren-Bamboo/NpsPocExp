import argparse

from core import *


def init():
    # 创建解析器对象
    des = """
    _   ______  _____    ____  ____  ______   _______  __ ____ 
   / | / / __ \/ ___/   / __ \/ __ \/ ____/  / ____/ |/ // __ 
  /  |/ / /_/ /\__ \   / /_/ / / / / /      / __/  |   // /_/ /
 / /|  / ____/___/ /  / ____/ /_/ / /___   / /___ /   |/ ____/ 
/_/ |_/_/    /____/  /_/    \____/\____/  /_____//_/|_/_/      
"""
    parser = argparse.ArgumentParser(description=des,formatter_class=argparse.RawDescriptionHelpFormatter)

    # 添加参数
    parser.add_argument("-f", "--file", help="url文件")
    parser.add_argument("-u", "--url", help="单个url")
    parser.add_argument("-a",  "--active", action="store_true", help="使用主动获取模式")

    # 解析参数
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = init()
    if args.active:
        target_set = core.active_scan_target()
    else:
        if args.file:
            target_set = core.read_file(args.file)
        elif args.url:
            target_set = [args.url]
        else:
            print("参数错误")
            exit(-1)

    chunk = 25  # 可通过配置文件改
    for i in range(0, len(target_set), chunk):
        print("第", i//25+1, "块开始处理")
        info_list = core.check_target(list(target_set)[i:i+chunk])
        core.save_result(info_list)
