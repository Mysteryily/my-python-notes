import asyncio

async def func():
    print("run func complete")


async def main():
    # Task是eventloop中的执行单位
    task1 = asyncio.create_task(func())
    task2 = asyncio.create_task(func())

    #当执行一个task时，task就占据了loop的占有权，只有当await和执行完毕后才会让出占有权
    # await 一般跟着的时future,task(task继承自future)或coroutine,返回值为后面对象__await__方法的返回值
    # 这里如果不await是一个不好的行为，run执行完main后事件循环就会close，并且cancel所有正在执行的协程。并且也可能会因为gc释放？
    await task1
    await task2
    print("run main complete")

if __name__ == "__main__":
    asyncio.run(main())