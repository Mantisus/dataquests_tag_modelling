import asyncio
import json

from lxml import html

from ..config import CATEGORY_URL, POSTS_URL
from ..utils.downloader import Downloader
from ..utils.logger import logger
from ..utils.iterutils import chunks


class Crowler():

    def __init__(self, db_manager, Downloader=Downloader):
        self.db_manager = db_manager
        self.Downloader = Downloader

    async def start(self, start_page=0):
        self.downloader = self.Downloader()
        await self.downloader.start()
        await self.category_loading(start_page)

    async def stop(self):
        while len(asyncio.all_tasks()) > 1:
            logger.warning(f"Current tasks pool {len(asyncio.all_tasks())}")
            await asyncio.sleep(10)
        logger.warning(f"Current tasks pool {len(asyncio.all_tasks())}")
        await self.downloader.stop()

    def posts_praser(self, json_data):
        json_data = json_data["post_stream"]
        posts = [
            {
                "topic_id": post["topic_id"],
                "post_id": post["id"],
                "post_number": post["post_number"],
                "score": post["score"],
                "author_username": post["username"],
                "author_name": post["name"],
                "text": html.fromstring(post["cooked"]).text_content() if post["cooked"] else '',
                "reads": post["reads"],
                "readers_count": post["readers_count"],
                "created": post["created_at"],
            } for post in json_data["posts"]
              if post["post_number"] != 1
        ]
        return posts

    async def posts_loader(self, topic_id, posts_ids):
        posts_ids = f"post_ids%5B%5D={'&post_ids%5B%5D='.join(posts_ids)}"
        url = POSTS_URL.format(post_id=topic_id, posts_ids=posts_ids)
        response_content = await self.downloader.get(url)
        json_data = json.loads(response_content)
        posts = self.posts_praser(json_data)
        asyncio.create_task(self.db_manager.write_posts(posts))

    def topic_parser(self, html_content, topic):
        data = html.fromstring(html_content)
        json_data = data.xpath("//*[@id='data-preloaded']/@data-preloaded")[0]
        json_data = json.loads(json_data)
        json_data = json.loads(json_data[f"topic_{topic['topic_id']}"])
        topic_data = json_data['post_stream']['posts'][0]
        text = html.fromstring(topic_data["cooked"]).text_content()
        topic.update({
            "author_username": topic_data["username"],
            "author_name": topic_data["name"],
            "created": topic_data["created_at"],
            "text": text,
            "reads": topic_data["reads"],
            "readers_count": topic_data["readers_count"],
            "score": topic_data["score"],
            "word_count": json_data["word_count"],
        })
        posts_ids = json_data["post_stream"]["stream"]
        return topic, posts_ids

    async def topic_loader(self, topic):
        topic_id = topic["topic_id"]
        url = f'{topic["url"]}/{topic_id}'
        logger.info(f"Loading topic by id {topic_id}")
        response_content = await self.downloader.get(url)
        topic, posts_ids = self.topic_parser(response_content, topic)
        chunks_posts_ids = chunks((str(posts_id) for posts_id in posts_ids), 100)
        asyncio.create_task(self.db_manager.write_topics(topic))
        for cheunk_posts_ids in chunks_posts_ids:
            asyncio.create_task(self.posts_loader(topic_id, cheunk_posts_ids))

    def category_parser(self, json_data):
        json_data = json_data["topic_list"]
        more_topic = True if json_data.get("more_topics_url", False) else False
        raw_topics = json_data["topics"]
        topics = ({"url": f"https://community.dataquest.io/t/{topic['slug']}",
                "topic_id": topic['id'],
                "title": topic['title'],
                "posts_count": topic["posts_count"],
                "views": topic["views"],
                "like_count": topic["like_count"]
                } for topic in raw_topics)
        return topics, more_topic

    async def category_loading(self, page):
        logger.info(f"Loading category page {page}")
        url = CATEGORY_URL.format(page=page)
        response_content = await self.downloader.get(url)
        json_data = json.loads(response_content)
        topics, more_topic = self.category_parser(json_data)
        if more_topic:
            next_page = int(page) + 1
            asyncio.create_task(self.category_loading(next_page))
        for topic in topics:
            asyncio.create_task(self.topic_loader(topic))
