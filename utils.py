import requests

def count_words_at_url(url):
    resp = requests.get('https://'+url)
    return len(resp.text.split())
