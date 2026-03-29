import asyncio

async def func():
    print("run func complete")

def sync_func():
    print("run sync func complete")

def main():
    # eventloop事件循环负责调度Task。下面是官方文档的介绍
    """
    事件循环会从其待处理事项中取出一个作业并唤起它（或称“给予其控制权”），类似于调用一个函数，然后该作业就会运行。 一旦它暂停或完成，它会将控制权返
    回给事件循环。然后事件循环会从作业池中选择另一个作业并唤起它。你可以粗略地将这组作业视为一个队列：作业被添加然后被逐个处理，通常（但不总是）按顺
    序进行。此过程将无限地重复，事件循环也不停地循环下去。 如果没有待执行的作业，事件循环会足够智能地转入休息状态以避免浪费CPU周期，并在有更多工作需
    完成时恢复运行。
    """
    # loop比较底层，python更推荐直接通过asynico里面封装的函数来执行
    loop = asyncio.new_event_loop()
    loop.create_task(func())
    loop.run_in_executor(None, sync_func)
    # run_in_executor实际已经在向线程去执行sync_func了，返回一个执行结果future对象
    loop.run_forever()
    loop.close()
    # loop run_forever会让eventloop一直执行(阻塞)直到内部task手动调用loop.stop
    # 不会执行到下面的print
    print("run complete")

    # result = loop.run_until_complete(fut)

if __name__ == '__main__':
    main()