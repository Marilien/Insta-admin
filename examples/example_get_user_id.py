from six.moves.urllib.request import urlopen
from instagram_private_api_lib.instagram_web_api import Client


def get_insta_id(username):
    link = 'http://www.instagram.com/' + username
    response = urlopen(link)
    content = str(response.read())
    start_pos = content.find('"owner":{"id":"') + len('"owner":{"id":"')
    end_pos = content[start_pos:].find('"')
    insta_id = content[start_pos:start_pos+end_pos]
    return insta_id



# def get_id(username):
#     url = "https://www.instagram.com/web/search/topsearch/?context=blended&query=" + username + "&rank_token=0.3953592318270893&count=1"
#     response = requests.get(url)
#     respJSON = response.json()
#     try:
#         user_id = str(respJSON['users'][0].get("user").get("pk"))
#         return user_id
#     except:
#         return "Unexpected error"

# def main():
#     if len(sys.argv) < 2:
#         print("Usage: \npython followers-service.py USERNAME")
#         return
#     user_id = get_id(sys.argv[1])
#     print("ID: " + user_id)




# if __name__ == "__main__":
#     print(get_id('trofimova_anastazia'))