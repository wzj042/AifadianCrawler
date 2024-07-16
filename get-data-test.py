from dotenv import load_dotenv, find_dotenv
import os, json
import requests
from time import sleep
import random
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
def save_api_response(api_name, response_data, base_path="post"):
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



def get_posts(user_id, headers, proxies):
    publish_sn = '0'  # Initial value for pagination
    has_more = True

    while has_more:
        api = API.post_list(user_id, publish_sn)
        response = requests.get(url=api['url'], headers=headers, proxies=proxies)
        if response.status_code == 200:
            data = response.json()
            posts = data['data']['list']
            for post in posts:
                publish_sn = post['publish_sn']  # Update publish_sn for next loop iteration
                post_detail = API.post_detail(post['post_id'])
                detail_response = requests.get(url=post_detail['url'], headers=headers, proxies=proxies)
                save_api_response(post_detail['name'], detail_response.json())
                
                # Simulate human-like pauses
                sleep(random.randint(1, 5))
            
            has_more = data['data']['has_more']
        else:
            has_more = False


user_id = '3f49234e3e8f11eb8f6152540025c377'
get_posts(user_id, headers, proxies)