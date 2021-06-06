from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

from ..config import MONGODB_SETTINGS


client = MongoClient(host=MONGODB_SETTINGS.get('host'),
                     port=MONGODB_SETTINGS.get('port'),
                     username=MONGODB_SETTINGS.get('username'),
                     password=MONGODB_SETTINGS.get('password'),
                     authSource=MONGODB_SETTINGS.get('db'))


class MongoManage:
    client = client

    def __init__(self):
        connect =self.client[MONGODB_SETTINGS.get('db', 'dataquest')]
        self.topic_collection = connect.topic_collection
        self.posts_collection = connect.posts_collection

    async def get_data(self, collection, filter_query, filter_fields):
        current_filter_fields = {"_id": 0}
        current_filter_fields |= filter_fields
        cursor = collection.find(filter_query, current_filter_fields)
        return (doc async for doc in cursor)

    async def write_data(self, collection, data):
        if isinstance(data, list):
            collection.insert_many(data)
        else:
            collection.insert_one(data)

    async def get_topics(self, *args):
        return await self.get_data(self.topic_collection, *args)

    async def write_topics(self, *args):
        await self.write_data(self.topic_collection, *args)

    async def get_posts(self, *args):
        return await self.get_data(self.posts_collection, *args)

    async def write_posts(self, *args):
        await self.write_data(self.posts_collection, *args)

    async def close(self):
        self.client.close()