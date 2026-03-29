import asyncio
import time
import requests
import aiohttp

urls = [
    "https://www.baidu.com",
    "https://www.taobao.com",
    "https://www.jd.com",
    "https://www.sina.com",
    "https://www.bing.com",
    "https://www.pinduoduo.com",
    "https://www.weibo.com",
    "https://www.sogou.com",
]

def sync_single_request(url):
    response = requests.get(url)
    response.raise_for_status()

async def async_single_request(url):
    response = requests.get(url)
    response.raise_for_status()

async def aiohttp_async_single_request(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            await response.read()

def sync_request_test():
    for url in urls:
        sync_single_request(url)

async def async_request_test():
    tasks = [async_single_request(url) for url in urls]
    await asyncio.gather(*tasks)

async def aiohttp_async_request_test():
    tasks = [aiohttp_async_single_request(url) for url in urls]
    await asyncio.gather(*tasks)

def main():
    sync_start_time = time.time()
    sync_request_test()
    sync_end_time = time.time()
    print(f"同步请求耗时{sync_end_time - sync_start_time} seconds")

    async_start_time = time.time()
    asyncio.run(async_request_test())
    async_end_time = time.time()
    print(f"request异步请求耗时{async_end_time - async_start_time} seconds")

    aiohttp_start_time = time.time()
    asyncio.run(aiohttp_async_request_test())
    aiohttp_end_time = time.time()
    print(f"aiohttp异步请求耗时{aiohttp_end_time - aiohttp_start_time} seconds")

if __name__ == "__main__":
    main()
    """
    同步请求耗时5.57884407043457 seconds
    request异步请求耗时5.52463436126709 seconds
    aiohttp异步请求耗时0.451275110244751 seconds
    
    request是同步的，实际会阻塞事件循环
    aiohttp能实现真正的异步
    """



