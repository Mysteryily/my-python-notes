import asyncio

async def func():
    print("run func complete")

def sync_func():
    print("run sync func complete")

async def main():
    # 对loop.py里面做法的现代化写法
    task1 = asyncio.create_task(func())
    task2 = asyncio.to_thread(sync_func)
    await task1
    await task2
    print("run complete")


if __name__ == '__main__':
    asyncio.run(main())
    # 结果
    """
    run func complete
    run sync func complete
    run complete
    
    而loop里面一般是先run sync func complete。原因在与run_in_executor会直接提交任务至线程池执行。
    但是to_thread是需要await来手动去执行的
    源码摘抄
    async def to_thread(func, /, *args, **kwargs):
        loop = events.get_running_loop()
        ctx = contextvars.copy_context()
        func_call = functools.partial(ctx.run, func, *args, **kwargs)
        return await loop.run_in_executor(None, func_call)
    """
