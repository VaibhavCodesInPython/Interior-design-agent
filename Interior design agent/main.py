import asyncio
from lib.agent import run_agent
from dotenv import load_dotenv
load_dotenv()
async def main():
    result = await run_agent()
    pass

if __name__=="__main__":
    asyncio.run(main())