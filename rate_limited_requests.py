import time
import threading
import random
import requests


class RateLimiter:
    """
    频率限制器：控制请求频率，确保最小请求间隔，并加入随机等待时间
    """

    def __init__(self, min_requests_per_second=1, max_requests_per_second=2):
        self.min_interval = 1 / max_requests_per_second
        self.max_interval = 1 / min_requests_per_second
        self.last_request_time = 0
        self.lock = threading.Lock()

    def wait(self):
        with self.lock:
            current_time = time.time()
            elapsed = current_time - self.last_request_time
            # 随机时间间隔
            sleep_time = random.uniform(self.min_interval, self.max_interval)
            if elapsed < sleep_time:
                time.sleep(sleep_time - elapsed)
            self.last_request_time = time.time()


# 初始化全局频率限制器
_rate_limiter = RateLimiter(min_requests_per_second=1, max_requests_per_second=2)

# 配置请求头，模拟真实浏览器
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

# 重试机制设置，包括对 429 的处理
from requests.adapters import HTTPAdapter


def get_retry_session():
    session = requests.Session()
    from urllib3 import Retry
    retry = Retry(
        total=5,  # 总共尝试次数
        backoff_factor=1,  # 重试间隔时间指数倍数
        status_forcelist=[500, 502, 503, 504, 429],  # 遇到这些错误重试
        allowed_methods=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"],  # 新版使用 allowed_methods
        raise_on_status=False  # 不抛出异常，便于捕获和重试
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


# 创建一个带有频率限制和重试的 request 方法
def _rate_limited_request(method, url, **kwargs):
    _rate_limiter.wait()  # 频率限制等待
    session = get_retry_session()  # 获取带有重试机制的 session
    kwargs["headers"] = kwargs.get("headers", headers)  # 默认使用自定义请求头
    response = session.request(method, url, **kwargs)

    # 如果是 429 状态码，可以添加处理逻辑，比如等待
    if response.status_code == 429:
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            wait_time = int(retry_after)  # 如果有 Retry-After 头部，使用其值
            print(f"Too many requests, waiting for {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            # 默认等待 1 秒后重试
            print("Too many requests, waiting for 1 second...")
            time.sleep(1)
    return response


# 替换 requests 的方法
requests.request = _rate_limited_request
requests.get = lambda url, **kwargs: _rate_limited_request("GET", url, **kwargs)
requests.post = lambda url, **kwargs: _rate_limited_request("POST", url, **kwargs)
requests.put = lambda url, **kwargs: _rate_limited_request("PUT", url, **kwargs)
requests.delete = lambda url, **kwargs: _rate_limited_request("DELETE", url, **kwargs)
requests.head = lambda url, **kwargs: _rate_limited_request("HEAD", url, **kwargs)
requests.options = lambda url, **kwargs: _rate_limited_request("OPTIONS", url, **kwargs)
requests.patch = lambda url, **kwargs: _rate_limited_request("PATCH", url, **kwargs)

# 将原始 requests 的其他属性暴露
globals().update({k: getattr(requests, k) for k in dir(requests) if not k.startswith("_")})
