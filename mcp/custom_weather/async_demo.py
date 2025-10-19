import asyncio

# 定义异步函数
async def hello_world():
    print("Hello")
    await asyncio.sleep(1)  # 等待1秒，但不阻塞
    print("World")
    method1()

# 运行异步函数
async def main():
    print("开始演示")
    await hello_world()  # 等待异步函数完成
    print("演示结束")

def method1():
    print("方法1")

# 启动事件循环
asyncio.run(main())