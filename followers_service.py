import json
import logging
import os.path
from time import time, sleep

from constants_local import *
from instagram_private_api_lib.examples.savesettings_logincallback import from_json, onlogin_callback
from flask_socketio import SocketIO, send, emit

# from cache import set_account_info, get_account_info, set_followers, get_followers

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
            i += 1


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

                # event('followers_received', len(updates_followers))

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
    print(MY_USERNAME, MY_PASSWORD)

    try:
        api = login_get_api(username=MY_USERNAME, password=MY_PASSWORD, coockie_file=COOCKIE_FILE_PATH)
    except:
        return None
    return api


def cache_reset():
    #     print('reset cache')
    #     cache.clear()
    return True


def account_info(username):
    # stored_account_info = get_account_info(username)
    # if (stored_account_info is not None):
    #    return stored_account_info
    user_info = get_user_info(username)
    user_id = user_info.get('user', []).get('pk', [])
    followers_len = user_info.get('user', []).get('follower_count', [])

    if user_info.get('user', []).get('is_private', []):
        res = {'is_private': True,
               'num_of_foll': None,
               'user_id': user_id,
               'msg': 'Sorry, you are trying to access private account'}
    else:
        if followers_len == 0:
            res = {'is_private': False,
                   'num_of_foll': 0,
                   'user_id': user_id,
                   'msg': 'Account exist'}

        elif followers_len > 200000:
            res = {'is_private': False,
                   'num_of_foll': followers_len,
                   'user_id': user_id,
                   'msg': 'Too many followers'}

        else:
            res = {'is_private': False,
                   'num_of_foll': followers_len,
                   'user_id': user_id,
                   'msg': 'Account exist'}
    # set_account_info(username, res)
    return res


def followers(user_id):
    # TODO  ---------------------------------
    # print(cache.keys())
    # if username in cache:
    #     print('return followers from cache')
    #     return cache[username]

    # user_info = get_user_info(username)
    # print(user_info)
    # user_id = user_info.get('user', []).get('pk', [])
    # followers_len = user_info.get('user', []).get('follower_count', [])

    # res = None
    # if user_info.get('user', []).get('is_private', []):
    #     res = {'msg': 'Sorry, you are trying to access private account', 'num_of_foll': None, 'foll_list': None}
    #
    # if followers_len == 0:
    #     res = {'msg': 'Account exist', 'num_of_foll': 0, 'foll_list': None}
    #
    # if followers_len > 200000:
    #     res = {'msg': 'Too many followers', 'num_of_foll': followers_len, 'foll_list': None}

    # if res is None:
    # stored_followers = get_followers(user_id)
    # if (stored_followers is not None):
    #    return stored_followers
    followers_list = get_followers_list(user_id=user_id)
    res = {'foll_list': followers_list}
    # set_followers(user_id, res)
    emit('followers_response', res)

    # return res


def get_accounts_info(list_of_usernames):
    if not isinstance(list_of_usernames, list) and len(list_of_usernames < 2):
        response = {'msg': 'Please, put at least two user_names', 'number_of_all_foll': None}
    else:
        check_result = 'Success'
        sum_of_followers = 0
        for username in list_of_usernames:
            user_info = get_user_info(username)
            if user_info.get('user', []).get('is_private', []):
                check_result = 'Private'
                sum_of_followers += user_info.get('user', []).get('follower_count', [])
            elif user_info.get('user', []).get('follower_count', []) < 1:
                check_result = 'No_foll'
                sum_of_followers += user_info.get('user', []).get('follower_count', [])
            else:
                sum_of_followers += user_info.get('user', []).get('follower_count', [])
        response = {'msg': check_result, 'number_of_all_foll': sum_of_followers}
    emit('accounts_info', response)
    return response


def get_multiple_list_followers(list_of_usedids):
    if not isinstance(list_of_usedids, list) and len(list_of_usedids < 2):
        response = {'len_of_cross_list': None, 'cross_list': None, 'msg': 'Too little number of accounts'}
    else:
        cross_list = get_followers_list(user_id=list_of_usedids[0])
        for i in range(1, len(list_of_usedids)):
            list_single_user_followers = get_followers_list(user_id=list_of_usedids[i])
            cross_list = list(set(cross_list) & set(list_single_user_followers))

        if len(cross_list) < 1:
            response = {'len_of_cross_list': len(cross_list), 'cross_list': None, 'msg': 'There are no similar followers'}
        else:
            response = {'len_of_cross_list': len(cross_list), 'cross_list': cross_list, 'msg': 'Success'}
    emit('cross_list_response', response)
    # return response


def get_cross_list(list_of_lists):
    print(type(list_of_lists))
    if not isinstance(list_of_lists, list) and len(list_of_lists < 2):
        response = {'len_of_cross_list': None, 'cross_list': None, 'msg': 'Too little number of accounts'}
    else:
        cross_list_ = list_of_lists[0]
        for element in list_of_lists:
            if element != cross_list_:
                cross_list_ = list(set(cross_list_) & set(element))
        response = {'len_of_cross_list': len(cross_list_), 'cross_list': cross_list_, 'msg': 'Success'}

    emit('cross_list_response', response)
    # return response


if __name__ == '__main__':
    # list_one = ['anastasiiaonatii', 'dmitrenkovitalii', 'denshcherbak', 'ejayy.official', 'sava_z', 'obi_van_kenobi_van', 'expelz', 'anastasiia_bogdanov_', 'adedashka', 'oldhouse_bakery', 'ivosaca', 'alla.vlayko', 'nata.cvetaeva', 'kqllly', 'marilien_m', 'antony_drovalev']
    # list_second = ['ivosaca', 'alla.vlayko', 'nata.cvetaeva', 'kqllly', 'marilien_m', 'antony_drovalev', 'bladiclab', 'alenka.stets', 'lazar_ira', 'fowiflowi', 'smyarga', 'k_aarrtt', 'mandrikm', 'persik1698', 'beatkafasi', 'k_voropaieva', 'mashakondratenko_', 'v_butovskyi', 'svetik3678', 'igorrr._', 'sazonova__m', 'nastya_rybchenko', 'mrvadamas', 'murmur_mari_', 'kolyayurchenko']
    # third_list = ['kqllly', 'antony_drovalev', 'marilien_m', 'nata.cvetaeva', 'ivosaca']
    # list_of_lists = [list_one, list_second, third_list]
    #
    # cross_list = get_cross_list('jhvkckt')
    # print(cross_list)

    # start_program_time = time()
    # acc_info = account_info('mur_mur_mash')

    #
    user_names = ['serhii_stets', 'mongolo4ka']
    accounts_info = get_accounts_info(user_names)
    print(accounts_info)



    acc_info_first = account_info('serhii_stets')
    print(acc_info_first)
    if not acc_info_first['is_private']:
        user_id_first = acc_info_first['user_id']

    acc_info_second = account_info('mongolo4ka')
    print(acc_info_second)
    if not acc_info_first['is_private']:
        user_id_second = acc_info_second['user_id']
    #
    # acc_info_third = account_info('alenka.stets')
    # print(acc_info_third)
    # if not acc_info_third['is_private']:
    #     user_id_third = acc_info_third['user_id']
    #
    list_user_ids = [user_id_first, user_id_second]
    print(list_user_ids)
    #
    cross_list = get_multiple_list_followers(list_user_ids)
    print(cross_list)

#     # print(time() - start_program_time)
