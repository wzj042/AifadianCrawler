from dotenv import load_dotenv, find_dotenv
import os
import json
import requests
from time import sleep
import random
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import ProxyError, ConnectionError

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

    @classmethod
    def comment_list(cls, post_id, publish_sn='', type='old', hot=1):
        return {
            "url": f"{cls.BASE_URL}/comment/get-list?post_id={post_id}&publish_sn={publish_sn}&type={type}&hot={hot}",
            "name": "get-comment-list"
        }

TEST_POST_ID = '6d117aca40ba11efa9795254001e7c00'

proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}

load_dotenv(find_dotenv(), override=True)

cookies = os.getenv('COOKIES')

headers = {
    'Cookie': cookies
}


"""
    保存 API 测试结果
"""


def save_api_response(target_id, response_data, base_path="comment"):
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    file_path = os.path.join(base_path, f"{target_id}.json")


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
    retry_count = 5
    last_post_list_res = None

    while has_more and retry_count > 0:
        api = API.post_list(user_id, publish_sn)
        response = requests.get(
            url=api['url'], headers=headers, proxies=proxies)
        if response.status_code == 200:
            data = response.json()

            # 检查数据是否和上次相同
            if last_post_list_res is not None:
                if data['data']['list'] == last_post_list_res['data']['list']:
                    retry_count -= 1
                    continue
                elif data['data']['list'] != last_post_list_res['data']['list']:
                    retry_count = 5

            last_post_list_res = data

            posts = data['data']['list']
            publish_sn = posts[-1]['publish_sn']
            for post in posts:
                # 检查是否已保存
                post_detail = API.post_detail(post['post_id'])

                if os.path.exists(f"post/{post['post_id']}.json"):
                    print(f"Post {post['title']} already saved")
                    continue

                detail_response = requests.get(
                    url=post_detail['url'], headers=headers, proxies=proxies)
                if detail_response.json()['data']['post']['has_right'] == 0:
                    print("当前内容未订阅或 Cookies 已过期")
                    continue

                # post_detail['name'] 临时移除，确保得到一堆零散的一级品：（
                save_api_response(post['post_id'], detail_response.json())
                print(f"Post {post['title']} saved")
                # Simulate human-like pauses
                sleep(random.randint(1, 5))

            has_more = data['data']['has_more']
        else:
            has_more = False
            retry_count -= 1

    print("All posts saved")

# 爬取动态做备份
# user_id = '3f49234e3e8f11eb8f6152540025c377'
# get_posts(user_id, headers, proxies)

# 爬取完动态备份后，顺便爬取一下评论

def get_comments_for_post(post_id, headers, proxies):
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.mount('http://', HTTPAdapter(max_retries=retries))

    has_more = True
    publish_sn = ''  # 初始为空，用于获取第一页评论
    comment_index = 0
    while has_more:
        api = API.comment_list(post_id, publish_sn=publish_sn)
        
        try:
            response = session.get(url=api['url'], headers=headers, proxies=proxies, timeout=(10, 30))
            # 处理响应
        except requests.exceptions.ChunkedEncodingError as e:
            print("Chunked Encoding Error occurred:", e)
            # 重试
            continue
        except requests.exceptions.RequestException as e:
            print("HTTP Request failed:", e)

            
        if response.status_code == 200:
            data = response.json()
            comments = data['data']['list']
            if comments:
                publish_sn = comments[-1]['publish_sn']  # 更新为最后一条评论的publish_sn以获取下一页评论

            # 保存评论数据
            save_api_response(comment_index, data, base_path=f"comments/{post_id}/")

            # 检查是否还有更多评论
            if comment_index > 0 and data['data']['list'] == []:
                has_more = False
                break

            has_more = data['data']['has_more']
            if has_more:
                comment_index += 1
        else:
            print("Failed to fetch comments for post", post_id)
            break

        # 随机暂停以模拟人类行为
        sleep(random.randint(1, 3))

    print(f"All comments saved for post {post_id}")


def fetch_and_save_all_comments(headers, proxies):
    base_path = "post"
    for filename in os.listdir(base_path):
        if filename.endswith(".json"):
            post_id = filename.split('.')[0]
            get_comments_for_post(post_id, headers, proxies)

# 在适当的地方调用 fetch_and_save_all_comments
fetch_and_save_all_comments(headers, proxies)


# 输出requirements.txt
# pip freeze > requirements.txt