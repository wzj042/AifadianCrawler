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


post_detail = API.post_detail(TEST_POST_ID)

"""
    保存 API 测试结果
"""
def save_api_response(api_name, response_data, base_path="res-example"):
    # 确保基于API名称的路径存在
    full_path = os.path.join(base_path, api_name)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    
    time_str = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_path = os.path.join(full_path, f"{time_str}.json")
    
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(response_data, file, ensure_ascii=False, indent=4)
    
    print(f"Data saved to {file_path}")

response = requests.get(url=post_detail["url"], headers=headers, proxies=proxies)

save_api_response(post_detail["name"], response.json())

print(response.status_code)
print()
print(response.json())

