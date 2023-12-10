import requests
from requests.exceptions import RequestException
import time

def make_request(url, request_method = "GET", headers=None, data=None, retries=3, delay=1):
    for i in range(retries):
        try:
            response = requests.request(request_method, url, headers=headers, data=data, timeout=10)
            response.raise_for_status()  # 检查响应状态码，如果不是 2xx，会抛出异常
            return response
        except RequestException as e:
            print(f"Error making request: {e}")
            if i < retries - 1:
                print(f"Retrying ({i+2}/{retries}) after {delay} second(s)...")
                time.sleep(delay)
    return None