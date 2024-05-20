import feedparser
from pymongo import MongoClient
from collections import defaultdict
from sentence_transformers import util, SentenceTransformer
import torch
from dotenv import load_dotenv, dotenv_values 
import os

load_dotenv()
URI = os.getenv('URI')

client = MongoClient(URI)

db = client['newsagg']
rssurls = db['rssurls']
articles = db['articles']

urls = [udoc['link'] for udoc in rssurls.find({})]
results = articles.find({})

def get_all_articles():
    documents = defaultdict(lambda : defaultdict(str))
    for result in results:
        documents[result['title']] = result
    return documents

model = SentenceTransformer('sentence-transformers/multi-qa-mpnet-base-dot-v1')

existing = get_all_articles()
documents = defaultdict(lambda : defaultdict(str))
idx = len(existing)

for feed_url in urls:
    feed = feedparser.parse(feed_url)
    if 'entries' not in feed: 
        continue
    for entry in feed.entries:
        if entry.title in documents or entry.title in existing:
            continue
        embed = model.encode([entry.title])[0]
        embed = embed.tolist()
        documents[entry.title] = {
            "id": idx,
            "title": entry.title,
            "rss_link": feed_url,
            "link": entry.link,
            "date": entry.published,
            "embedding": embed
        }
        idx += 1

if len(documents) > 0:
    ret = articles.insert_many(documents.values())
print('Inserted {} articles'.format(len(documents)))