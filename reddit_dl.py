import asyncpraw
import asyncio
import random

reddit = asyncpraw.Reddit(client_id='Your client ID here',
                     client_secret='Your client secret here',
                     user_agent='[project_name] by [reddit_username]',)

class Reddit_DL():

    def __init__(self):
        return

    @classmethod
    async def find_post_from_subreddit(cls, r_name):
        subreddit = await reddit.subreddit(r_name)
        x = random.randint(0, 99)
        i = 0
        submission_list = subreddit.hot(limit=100)
        async for submission in submission_list:
            if i == x:
                post = submission
                break
            i += 1
        #top_level_comments = await post.comments()
        #comment_count = len(top_level_comments)
        random_num = random.randint(0, 500)
        print([post.title, post.id, post.url, post.ups, random_num])
        return [post.title, post.id, post.url, post.ups, random_num]
