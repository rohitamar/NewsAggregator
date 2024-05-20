import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

from dotenv import load_dotenv, dotenv_values 
import os

load_dotenv()

URI = os.getenv('URI')

client = MongoClient(URI)
db = client['newsagg']
collection = db['articles']

rss = 'https://news.google.com/rss/search?q=when:24h+allinurl:apnews.com&hl=en-US&gl=US&ceid=US:en'
for doc in collection.find({"rss_link": rss, "content": {"$exists": False}}):
    url = doc['link']
    
    response = requests.get(url, allow_redirects = True)
    
    soup = BeautifulSoup(response.content, 'html.parser')

    if 'video' in response.url:
        div = soup.find('div', class_ = 'VideoPage-pageSubHeading')
        _ = collection.update_one({
            'id': doc['id']
        },
        {
            "$set": {
                'link': response.url,
                'publisher': 'Video',
                'is_video': True,
                'video_content': div.text if div else ''
            }
        })
    else:
        div = soup.find('div', class_ = 'Page-breadcrumbs')
        a_tag = div.find('a', class_='Link')
        divs = soup.find('div', class_ = 'RichTextStoryBody RichTextBody')
        paras = divs.find_all('p')
        content = " ".join([para.text for para in paras])
        
        _ = collection.update_one({
            'id': doc['id']
        },
        {
            "$set": {
                'link': response.url,
                'publisher': a_tag.text,
                'is_video': False,
                'content': content
            }
        })

rss = 'https://abcnews.go.com/abcnews/politicsheadlines'
for doc in collection.find({"rss_link": rss, "content": {"$exists": False}}):
    response = requests.get(doc['link'], allow_redirects = True)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    div = soup.find('div', class_ = 'xvlfx ZRifP TKoO eaKKC bOdfO')
    paras = div.find_all('p')
    content = " ".join([para.text for para in paras])
    
    _ = collection.update_one({
        'id': doc['id']
    },
    {
        "$set": {
            'link': response.url,
            'publisher': 'US Politics',
            'is_video': False,
            'content': content
        }
    })

rss = ['https://feeds.npr.org/1003/rss.xml', 'https://feeds.npr.org/1004/rss.xml']
for doc in collection.find({"rss_link": {"$in": rss}, "content": {"$exists": False}}):    
    response = requests.get(doc['link'], allow_redirects = True)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    div = soup.find('div', class_ = 'storytext storylocation linkLocation')
    paras = div.find_all('p')
    content = "\n\n".join([para.text for para in paras])
    
    h3 = soup.find('h3', class_ = 'slug')
    if not h3:
        continue
    _ = collection.update_one({
        'id': doc['id']
    },
    {
        "$set": {
            'link': response.url,
            'publisher': h3.text,
            'is_video': False,
            'content': content
        }
    })

rss = ['https://news.google.com/rss/search?q=allinurl:cnn.com&hl=en-US&gl=US&ceid=US:en']
for doc in collection.find({"rss_link": {"$in": rss}, "content": {"$exists": False}}):    
    response = requests.get(doc['link'], allow_redirects = True)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    div = soup.find_all('p', class_ = 'paragraph inline-placeholder vossi-paragraph-primary-core-light')
    content = "\n\n".join([para.text.strip() for para in div])
    
    _ = collection.update_one({
        'id': doc['id']
    },
    {
        "$set": {
            'link': response.url,
            'is_video': False,
            'content': content
        }
    })

rss = ['https://www.forbes.com/real-time/feed2/']
for doc in collection.find({"rss_link": {"$in": rss}, "content": {"$exists": False}}):    
    response = requests.get(doc['link'], allow_redirects = True)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    div = soup.find('div', class_ = 'body-container')
    if not div: 
        continue
    paras = div.find_all('p', class_ = "")
    content = "\n\n".join([para.text.strip() for para in paras])
    
    _ = collection.update_one({
        'id': doc['id']
    },
    {
        "$set": {
            'link': response.url,
            'is_video': False,
            'content': content
        }
    })

rss = ['https://www.theguardian.com/us-news/rss']
for doc in collection.find({"rss_link": {"$in": rss}, "content": {"$exists": False}}):    
    response = requests.get(doc['link'], allow_redirects = True)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    paras = soup.find_all('p', class_ = "dcr-iy9ec7")
    content = "\n\n".join([para.text.strip() for para in paras])
    
    _ = collection.update_one({
        'id': doc['id']
    },
    {
        "$set": {
            'link': response.url,
            'is_video': False,
            'content': content
        }
    })

rss = ['https://feeds.nbcnews.com/nbcnews/public/politics', 'https://feeds.nbcnews.com/nbcnews/public/science', 'https://feeds.nbcnews.com/nbcnews/public/world']
for doc in collection.find({"rss_link": {"$in": rss}, "content": {"$exists": False}}):    
    response = requests.get(doc['link'], allow_redirects = True)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    div = soup.find('div', class_ = "article-body__content")
    if not div:
        span = soup.find('span', class_ = 'video-details__dek-description')
        if not span:
            print(doc['link'])
            continue
        _ = collection.update_one({
            'id': doc['id']
        },
        {
            "$set": {
                'link': response.url,
                'content': span.text
            }
        })
    else:
        paras = div.find_all('p')
        content = "\n\n".join([para.text.strip() for para in paras])
        _ = collection.update_one({
            'id': doc['id']
        },
        {
            "$set": {
                'link': response.url,
                'is_video': False,
                'content': content
            }
        })

rss = ['https://www.economist.com/united-states/rss.xml',
      'https://www.economist.com/business/rss.xml',
      'https://www.economist.com/finance-and-economics/rss.xml',
      'https://www.economist.com/science-and-technology/rss.xml']

for doc in collection.find({"rss_link": {"$in": rss}, "content": {"$exists": False}}):    
    response = requests.get(doc['link'], allow_redirects = True)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    paras = soup.find_all('p', class_ = "css-1f0x4sl e1tt35bk0")

    content = "\n\n".join([para.text.strip() for para in paras])
    
    _ = collection.update_one({
        'id': doc['id']
    },
    {
        "$set": {
            'link': response.url,
            'is_video': False,
            'content': content,
            'paywall': True
        }
    })

rss = ['https://moxie.foxnews.com/google-publisher/politics.xml',
      'https://moxie.foxnews.com/google-publisher/world.xml',
      'https://moxie.foxnews.com/google-publisher/science.xml',
      'https://moxie.foxnews.com/google-publisher/tech.xml']

for doc in collection.find({"rss_link": {"$in": rss}, "content": {"$exists": False}}):    
    response = requests.get(doc['link'], allow_redirects = True)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    div = soup.find('div', class_ = "article-body")
    paras = div.find_all('p', class_ = 'speakable')
    content = "\n\n".join([para.text.strip() for para in paras])
    
    _ = collection.update_one({
        'id': doc['id']
    },
    {
        "$set": {
            'link': response.url,
            'is_video': False,
            'content': content
        }
    })

rss = ["https://news.yahoo.com/rss/world",
      "https://news.yahoo.com/rss/health"]

for doc in collection.find({"rss_link": {"$in": rss}, "content": {"$exists": False}}):    
    print(doc['link'])
    response = requests.get(doc['link'], allow_redirects = True)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    div = soup.find('div', class_ = "caas-body")
    if not div:
        print(doc['link'])
        continue
    paras = div.find_all('p')
    content = "\n\n".join([para.text.strip() for para in paras])
    
    _ = collection.update_one({
        'id': doc['id']
    },
    {
        "$set": {
            'link': response.url,
            'is_video': False,
            'content': content
        }
    })