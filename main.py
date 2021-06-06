import asyncio

from .parser.data_parser import Crowler
from .db.db_manager import MongoManage
from .utils.logger import logger

async def start_scan():
    try:
        mongo = MongoManage()
        crowler = Crowler(db_manager=mongo)
        await crowler.start(start_page=0)
        await crowler.stop()
    except Exception as e:
        logger.exception(e)
    finally:
        await mongo.close()

if __name__ == '__main__':
    asyncio.run(start_scan())