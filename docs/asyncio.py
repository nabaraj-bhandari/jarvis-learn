# asyncio basics

import asyncio


async def test():
    await asyncio.sleep(1)
    print("Hello World!")


async def main():
    await asyncio.gather(test(), test())
    await test()
    await test()
    await test()


if __name__ == "__main__":
    asyncio.run(main())
