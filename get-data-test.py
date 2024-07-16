from dotenv import load_dotenv, find_dotenv
import os
import requests

class API:
    BASE_URL = f"https://afdian.net/api"
    
    @classmethod
    def post_detail(cls, post_id):
        return f"{cls.BASE_URL}/post/get-detail?post_id={post_id}"

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


url = API.post_detail(TEST_POST_ID)



response = requests.get(url=url, headers=headers, proxies=proxies)

print(response.status_code)
print()
print(response.json())

