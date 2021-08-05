from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, HttpUrl
from facebook_scraper import get_posts
import sqlite3

import warnings
warnings.filterwarnings("ignore")

app = FastAPI()


class URL(BaseModel):
    url: HttpUrl


@app.get('/')
def index():
    return {'About': 'Facebook scrapping service using fastAPI'}


@app.post('/scrap_posts')
async def scrap_tags(url: URL):
    page = requests.get(str(url.url))
    soup = BeautifulSoup(page.text, 'html.parser')

    def get_title():
        return soup.head.find('title').text if soup.head.find('title').text else None

    def get_description():
        main_description = soup.head.find('meta', attrs={'name': 'description'}).get('content') if soup.head.find(
            'meta', attrs={'name': 'description'}) else None
        og_description = soup.find('meta', property="og:description").get('content') if soup.find('meta',
                                                                                                  property="og:description") else None
        return main_description or og_description or None

    def get_keywords():
        keywords = soup.head.find('meta', attrs={'name': 'keywords'}).get('content') if soup.head.find('meta', attrs={
            'name': 'keywords'}) else None
        return keywords

    def get_image():
        return soup.find('meta', property="og:image").get('content') if soup.find('meta', property="og:image") else None

    def get_posts_page_fcb():
        listposts = []
        page = str(url.url).split("facebook.com/", 1)[1]

        ## connect to database
        conn = sqlite3.connect('fcb_page.db')
        c = conn.cursor()
        # delete table if exist

        try:
            c.execute('''DROP TABLE Results''')
        except:
            print("Table Results don't exists")

        # create a table
        c.execute(
            '''CREATE TABLE Results( post_id  TEXT ,  text  TEXT ,  post_text  TEXT ,  shared_text  TEXT ,  time  TEXT ,  image  TEXT ,  image_lowquality  TEXT ,  images  TEXT ,  images_description  TEXT ,  images_lowquality  TEXT ,  images_lowquality_description  TEXT ,  video  TEXT ,  video_duration_seconds  TEXT ,  video_height  TEXT ,  video_id  TEXT ,  video_quality  TEXT ,  video_size_MB  TEXT ,  video_thumbnail  TEXT ,  video_watches  TEXT ,  video_width  TEXT ,  likes  TEXT ,  comments  TEXT ,  shares  TEXT ,  post_url  TEXT ,  link  TEXT ,  user_id  TEXT ,  username  TEXT ,  user_url  TEXT ,  is_live  TEXT ,  factcheck  TEXT ,  shared_post_id  TEXT ,  shared_time  TEXT ,  shared_user_id  TEXT ,  shared_username  TEXT ,  shared_post_url  TEXT ,  available  TEXT ,  comments_full  TEXT ,  reactors  TEXT ,  w3_fb_url  TEXT ,  reactions  TEXT ,  reaction_count  TEXT ,  image_id  TEXT ,  image_ids TEXT)''')

        for post in get_posts(page, pages=1):
            listposts.append(post)
            post_str = [str(i) for i in post.values()]
            c.execute(
                '''INSERT INTO Results VALUES( ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                post_str)
            conn.commit()
        return listposts


    return {
        "url": url.url,
        "title": get_title(),
        "description": get_description(),
        "keywords": get_keywords(),
        "image": get_image(),
        "post": get_posts_page_fcb()

    }





