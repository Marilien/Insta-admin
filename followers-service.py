import json
import codecs
import datetime
import os.path
import logging
import argparse
from time import time, sleep
import requests

import instaloader
from six.moves.urllib.request import urlopen
from instagram_private_api_lib.examples.savesettings_logincallback import to_json, from_json, onlogin_callback
from instagram_private_api.errors import ClientThrottledError
from constants_local import *
from cache import cache

try:
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)
except ImportError:
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)


def login_get_api(username, password, coockie_file):
    logging.basicConfig()
    logger = logging.getLogger('instagram_private_api')
    logger.setLevel(logging.WARNING)

    # # Example command:
    # # python examples/followers-service.py -u "yyy" -p "zzz" -settings "test_credentials.json"
    # parser = argparse.ArgumentParser(description='login callback and save settings demo')
    # parser.add_argument('-settings', '--settings', dest='settings_file_path', type=str, required=True)
    # parser.add_argument('-u', '--username', dest='username', type=str, required=True)
    # parser.add_argument('-p', '--password', dest='password', type=str, required=True)
    # parser.add_argument('-debug', '--debug', action='store_true')
    #
    # args = parser.parse_args()
    # if args.debug:
    #     logger.setLevel(logging.DEBUG)

    # print('Client version: {0!s}'.format(client_version))

    device_id = None
    try:
        settings_file = coockie_file
        # settings_file = args.settings_file_path
        if not os.path.isfile(settings_file):
            # settings file does not exist
            # print('Unable to find file: {0!s}'.format(settings_file))

            # login new
            api = Client(
                username, password,
                on_login=lambda x: onlogin_callback(x, coockie_file))

            # api = Client(
            #     args.username, args.password,
            #     on_login=lambda x: onlogin_callback(x, args.settings_file_path))

        else:
            with open(settings_file) as file_data:
                cached_settings = json.load(file_data, object_hook=from_json)
            # print('Reusing settings: {0!s}'.format(settings_file))

            device_id = cached_settings.get('device_id')
            # reuse auth settings
            api = Client(
                username, password,
                settings=cached_settings)

            # api = Client(
            #     args.username, args.password,
            #     settings=cached_settings)

    except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
        print('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))

        # Login expired
        # Do relogin but use default ua, keys and such

        api = Client(
            username, password,
            device_id=device_id,
            on_login=lambda x: onlogin_callback(x, coockie_file))

        # api = Client(
        #     args.username, args.password,
        #     device_id=device_id,
        #     on_login=lambda x: onlogin_callback(x, args.settings_file_path))

    # except ClientLoginError as e:
    #     print('ClientLoginError {0!s}'.format(e))
    #     exit(9)
    # except ClientError as e:
    #     print('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
    #     exit(9)
    # except Exception as e:
    #     print('Unexpected Exception: {0!s}'.format(e))
    #     exit(99)

    return api


def get_user_info(user_name):
    # uuid = api.generate_uuid()
    i = 0
    while True:
        api = get_api(i)
        if api is None:
            return None
        try:
            user_info = api.username_info(user_name)
            return user_info
        except:
            i +=1

def get_followers_list(user_id, save=True):

    # Show when login expires
    # cookie_expiry = api.cookie_jar.auth_expires
    # print('Cookie Expiry: {0!s}'.format(datetime.datetime.fromtimestamp(cookie_expiry).strftime('%Y-%m-%dT%H:%M:%SZ')))
    i = 0
    while True:
        api = get_api(i)
        if api is None:
            print("No possible login accounts")
            return None
        try:
            start_time = time()
            list_foll_len = 0

            uuid = api.generate_uuid()
            print("@@@@@@@@@@@@", user_id, uuid)
            followers = api.user_followers(user_id=user_id, rank_token=uuid)

            updates_followers = []
            updates_followers.extend(followers.get('users', []))

            next_max_id = followers.get('next_max_id')
            while next_max_id:
                # print(next_max_id)

                followers = api.user_followers(user_id=user_id, rank_token=uuid, max_id=next_max_id)
                # print(followers)
                # print(len(followers['users']))
                updates_followers.extend(followers.get('users', []))
                # if len(updates) >= 30:       # get only first 30 or so
                #     break
                next_max_id = followers.get('next_max_id')

                if save:
                    with open('data/followers_' + str(user_id) + '.txt', 'w', encoding="utf-8") as file:
                        for item in updates_followers:
                            file.write('%s\n' % item['username'])

                print(len(updates_followers))
                # list_foll_len += len(updates_followers)
                # print(list_foll_len)
                print(time() - start_time)
                sleep(0.01)

            # print('followers all', updates_followers)
            followers_names = [x['username'] for x in updates_followers]
            # print('followers names: ', followers_names)

            # with open('followers_' + str(user_id) + '.txt', 'w') as file:
            #     for item in followers_names:
            #         file.write('%s\n' % item)
            # print('All ok, list in file')

            # print('Names = ', followers_names)
            return followers_names
        except:
            i += 1
            print("Get next account", i)


def get_api(index):
    # print(MY_USERNAME)
    # print(MY_PASSWORD)
    # api = login_get_api(username=MY_USERNAME, password=MY_PASSWORD, coockie_file=COOCKIE_FILE_PATH)
    if index != 0:
        os.remove(COOCKIE_FILE_PATH)
    if index >= len(LOGIN_DATA):
        return None
    MY_USERNAME = LOGIN_DATA[index].get('MY_USERNAME', [])
    MY_PASSWORD = LOGIN_DATA[index].get('MY_PASSWORD', [])
    api = login_get_api(username=MY_USERNAME, password=MY_PASSWORD, coockie_file=COOCKIE_FILE_PATH)
    return api

def cache_reset():
    print('reset cache')
    cache.clear()
    return True

def followers(username):
    print(cache.keys())
    if username in cache:
        print('return followers from cache')
        return cache[username]
    
    user_info = get_user_info(username)
    print(user_info)
    user_id = user_info.get('user', []).get('pk', [])
    followers_len = user_info.get('user', []).get('follower_count', [])
    res = None
    if user_info.get('user', []).get('is_private', []):
        res = {'msg': 'Sorry, you are trying to access private account', 'num_of_foll': None, 'foll_list': None}

    if followers_len == 0:
        res = {'msg': 'Account exist', 'num_of_foll': 0, 'foll_list': None}

    if followers_len > 200000:
        res =  {'msg': 'Too many followers', 'num_of_foll': followers_len, 'foll_list': None}

    if res is None:
        followers_list = get_followers_list(user_id=user_id)
        res = {'msg': "Account exist", 'num_of_foll': followers_len, 'foll_list': followers_list}
    cache[username] = res
    return res

if __name__ == '__main__':
    # start_program_time = time()
    followers = followers('marilien_m')
    print(followers)
#     # print(time() - start_program_time)
