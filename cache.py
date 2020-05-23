import time


TTL = 120

cache = {}

def set_account_info(username, account_info):
  if (not username in cache):
    cache[username] = {}
  cache[username]['account_info'] = account_info
  cache[username]['updated_at'] = int(time.time())

def get_account_info(username):
  current_time = int(time.time())
  if (
    username in cache 
    and (current_time - cache[username]['updated_at'] <= TTL) 
    and 'account_info' in cache[username]
  ):
    print('return account_info from cache')
    return cache[username]['account_info']

def set_followers(username, followers):
  if (not username in cache):
    cache[username] = {}
  cache[username]['followers'] = followers
  cache[username]['updated_at'] = int(time.time())

def get_followers(username):
  current_time = int(time.time())
  if (
    username in cache 
    and (current_time - cache[username]['updated_at'] <= TTL) 
    and 'followers' in cache[username]
  ):
    print('return followers from cache')
    return cache[username]['followers']

set_account_info('test', {'private': True})
