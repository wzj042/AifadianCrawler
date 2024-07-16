from dotenv import load_dotenv, find_dotenv
import os, json
import requests
from datetime import datetime


class API:
    BASE_URL = f"https://afdian.net/api"
    
    @classmethod
    def post_detail(cls, post_id):
        return {
            "url": f"{cls.BASE_URL}/post/get-detail?post_id={post_id}",
            "name": "get-post-detail"
        }
    @classmethod
    def post_list(cls, user_id, publish_sn, per_page=10):
        return {
            "url": f"{cls.BASE_URL}/post/get-list?user_id={user_id}&publish_sn={publish_sn}&per_page={per_page}&all=1",
            "name": "get-post-list"
        }

TEST_POST_ID = '6d117aca40ba11efa9795254001e7c00'

proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}

load_dotenv(find_dotenv(), override=True)

cookies = "os.getenv('COOKIES')"

headers = {
    'Cookie': cookies
}



"""
    保存 API 测试结果
"""
def save_api_response(api_name, response_data, base_path="res-example"):
    full_path = os.path.join(base_path, api_name)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    
    time_str = datetime.now().strftime("%Y%m%d-%H-%M-%S")
    file_path = os.path.join(full_path, f"{time_str}.json")
    
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(response_data, file, ensure_ascii=False, indent=4)
    
    print(f"Data saved to {file_path}")


"""
    测试 API 请求
"""
def test_api(api, headers=headers, proxies=proxies):

    response = requests.get(url=api["url"], headers=headers, proxies=proxies)

    save_api_response(api["name"], response.json())

    print("链接成功" if response.status_code == 200 else "链接失败") 
    try:
        if response.json()["data"]["post"]["has_right"] == 0:
            print("当前内容未订阅或 Cookies 已过期")
    except KeyError:
        print("当前内容格式错误或代码已过期")


post_detail = API.post_detail(TEST_POST_ID)
test_api(post_detail)


