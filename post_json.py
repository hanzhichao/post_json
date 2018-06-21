import json
import sys
import requests
import optparse
import os


def postJson(path, timeout=60):
    try:
        with open(path, encoding='utf-8') as f:
            apis = json.load(f)

        if isinstance(apis, dict):
            apis=[apis]

        session = requests.session()
        for api in apis:

            # 处理全局变量
            str_api = json.dumps(api)
            if '%' in str_api:
                api = json.loads(str_api % globals())

            # 获取接口相关项
            url = api.get('url')
            method = api.get('method')
            headers = api.get('headers')
            cookies = api.get('cookies')
            params = api.get('params')
            data = api.get('data')
            files = api.get('files')
            _store = api.get('store')
            _assert = api.get('assert') # 系统变量 Response  Store  Assert Request Py  Sh Cmd  exec db Java JS

            # 如果json请求，转换一下数据
            if headers and 'json' in json.dumps(headers):
                data = json.dumps(data)

            # 根据method发送不同请求
            print("="*80)
            print("请求:")
            print("Url: %s\nHeaders: %s\nData: %s" % (url, headers, data if isinstance(data, str) else json.dumps(data)))
            if method and method.lower() == 'get':
                response = session.get(url=url, headers=headers, cookies=cookies, params=params, data=data, files=files, timeout=timeout)
            else:
                response = session.post(url=url, headers=headers, cookies=cookies, params=params, data=data, files=files, timeout=timeout)

            # 存储中间结果
            if _store:
                for key in _store:
                    globals()[key]=eval(_store[key])
            
            # 打印结果
            print("-"*80)
            print("响应:")
            try:
                print(json.dumps(response.json(), ensure_ascii=False, indent=2))
            except json.decoder.JSONDecodeError:  # only python3
                try:
                    print(response.text)
                except UnicodeEncodeError:
                    # print(response.content.decode("utf-8","ignore").replace('\xa9', ''))
                    print(response.content)
            finally:
                pass

            # 处理断言
            if _assert:
                print("-"*80)
                print("断言:")
                for item in _assert:
                    try:
                        assert eval(item)
                        print("PASS: <%s>" % item)
                    except AssertionError:
                        print("FAIL: <%s>" % item)
    
    except IOError as e:
        print(e)

    except json.decoder.JSONDecodeError:
        print("json文件格式有误")

def main():
    if len(sys.argv) != 2:
        print("缺少参数：json文件")
    else:
        postJson(sys.argv[1])


def discover(path="."):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.startswith("test") and file.endswith(".json"):
                postJson(os.path.join(root, file))

def report():
    pass


def collect_only(path="."):
    count = 0
    for root,dirs,files in os.walk(path):
        for file in files:
            if file.endswith(".json"):
                print(os.path.join(root, file))
                count += 1
        print("-"*80)
        print("Total: %d" % count)

# main()                

cli_opt = optparse.OptionParser()
cli_opt.add_option("--collect-only", action="store_true", dest="collect_only", help="列出所有用例")
(options, args) = cli_opt.parse_args()

if options.collect_only:
    collect_only() if not args else collect_only(args[0])

