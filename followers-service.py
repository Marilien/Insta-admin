import json
import codecs
import datetime
import os.path
import logging
import argparse
import time
import requests

import instaloader
from six.moves.urllib.request import urlopen
from instagram_private_api_lib.examples.savesettings_logincallback import to_json, from_json, onlogin_callback
from instagram_private_api.errors import ClientThrottledError
from constants_local import *

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

    print('Client version: {0!s}'.format(client_version))

    device_id = None
    try:
        settings_file = coockie_file
        # settings_file = args.settings_file_path
        if not os.path.isfile(settings_file):
            # settings file does not exist
            print('Unable to find file: {0!s}'.format(settings_file))

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
            print('Reusing settings: {0!s}'.format(settings_file))

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

    except ClientLoginError as e:
        print('ClientLoginError {0!s}'.format(e))
        exit(9)
    except ClientError as e:
        print('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
        exit(9)
    except Exception as e:
        print('Unexpected Exception: {0!s}'.format(e))
        exit(99)

    return api


# def get_insta_id(username):
#     url = "https://www.instagram.com/web/search/topsearch/?context=blended&query=" + username + "&rank_token=0.3953592318270893&count=1"
#     response = requests.get(url)
#     respJSON = response.json()
#     try:
#         user_id = str(respJSON['users'][0].get("user").get("pk"))
#         return user_id
#     except:
#         return "Unexpected error"

def get_user_info(api, user_name):
    # uuid = api.generate_uuid()
    user_info = api.username_info(user_name)
    return user_info


def get_insta_id(api, user_name):
    user_info = get_user_info(api=api, user_name=user_name)

    if not user_info.get('user', []).get('is_private', []):
        link = 'http://www.instagram.com/' + user_name
        response = urlopen(link)
        content = str(response.read())
        start_pos = content.find('"owner":{"id":"') + len('"owner":{"id":"')
        end_pos = content[start_pos:].find('"')
        insta_id = content[start_pos:start_pos + end_pos]

    else:
        # print('Sorry, you are trying to access private account')
        return None

    return insta_id


def get_followers_list(api, user_id, save=True):
    # Show when login expires
    # cookie_expiry = api.cookie_jar.auth_expires
    # print('Cookie Expiry: {0!s}'.format(datetime.datetime.fromtimestamp(cookie_expiry).strftime('%Y-%m-%dT%H:%M:%SZ')))

    uuid = api.generate_uuid()
    followers = api.user_followers(user_id=user_id, rank_token=uuid)

    # followers = {}

    updates_followers = []
    updates_followers.extend(followers.get('users', []))

    next_max_id = followers.get('next_max_id')
    while next_max_id:
        print(next_max_id)

        followers = api.user_followers(user_id=user_id, rank_token=uuid, max_id=next_max_id)
        print(followers)
        print(len(followers['users']))
        updates_followers.extend(followers.get('users', []))
        # if len(updates) >= 30:       # get only first 30 or so
        #     break
        next_max_id = followers.get('next_max_id')

        if save:
            with open('data/followers_' + str(user_id) + '.txt', 'w', encoding="utf-8") as file:
                for item in updates_followers:
                    file.write('%s\n' % item['username'])

        time.sleep(3)

    # print('followers all', updates_followers)
    # print('updates len', len(updates_followers))
    followers_names = [x['username'] for x in updates_followers]
    # print('followers names: ', followers_names)
    print(len(followers_names))

    # with open('followers_' + str(user_id) + '.txt', 'w') as file:
    #     for item in followers_names:
    #         file.write('%s\n' % item)
    # print('All ok, list in file')

    return followers_names


def followers(username):
    api = login_get_api(username=MY_USERNAME, password=MY_PASSWORD, coockie_file=COOCKIE_FILE_PATH)
    user_id = get_insta_id(api, username)

    if user_id is not None:
        user_info = get_user_info(api, username)
        followers_len = user_info.get('user', []).get('follower_count', [])
    else:
        return {'message': 'Sorry, you are trying to access private account'}
    followers_list = get_followers_list(api=api, user_id=user_id)

    # return {'len_followers':followers_len, 'followers_list': followers_list}
    return {followers_len: followers_list}


if __name__ == '__main__':
    followers = followers('pythongirl_m')
    print(followers)
    # # user_id = get_insta_id("marilien_m")  # 5510404286
    # # print(user_id)
    #
    # api = login_get_api(username=MY_USERNAME, password=MY_PASSWORD, coockie_file=COOCKIE_FILE_PATH)
    # user_info = get_user_info(api=api, user_name='marilien_m')
    # print(user_info)
    # # print(user_info.get('user', []).get('is_private', []))
    #
    # # followers_list = get_followers_list(api=api, user_id=user_id)
