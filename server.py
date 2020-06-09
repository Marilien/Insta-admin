from flask import (Flask,
    render_template
)
from flask_cors import cross_origin, CORS

from followers_service import account_info, followers, get_multiple_list_followers, get_accounts_info

app = Flask(__name__)
CORS(app)
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/api/account_info/<username>')
def get_account_info(username):
    return account_info(username)

@app.route('/api/followers/<user_id>')
def get_followers(user_id):
    return followers(user_id)

@app.route('/api/get_accounts_info/<list_of_usernames>')
def multiple_accounts_info(list_of_usernames):
    return get_accounts_info(list_of_usernames)



# @socketio.on('followers')
# def handle_followers(user_id):
#     # print('answer from backend')
#     # emit('followers_response', user_id)
#     followers(user_id)


# @socketio.on('get_multiple_list_followers')
# def handle_multiple_followers(list_of_usedids):
#     # print('answer from backend')
#     # emit('followers_response', user_id)
#     get_multiple_list_followers(list_of_usedids)


# # @socketio.on('get_accounts_info')
# # def handle_accounts_info(list_of_usernames):
# #     # print('answer from backend')
# #     # emit('followers_response', user_id)
# #     get_accounts_info(list_of_usernames)



# @socketio.on('connect')
# def test_connect():
#     emit('other_client_connected', broadcast=True)

# @socketio.on('disconnect')
# def test_disconnect():
#     print('Client disconnected')
# @app.route('/api/1/followers/<user_id>')
# @cross_origin()
# def get_followers(user_id):
#     from followers_service import followers
#     job = q.enqueue(followers, user_id)
#     return job.get_id()

# @app.route('/task/<url>')
# @cross_origin()
# def handle_task(url):
#     from utils import count_words_at_url
#     job = q.enqueue(count_words_at_url, url)
#     return job.get_id()


# @app.route("/results/<job_key>")
# @cross_origin()
# def get_results(job_key):
#     job = Job.fetch(job_key, connection=conn)
#     if job.is_finished:
#         return jsonify(job.result)
#     else:
#         return "Nay!", 202

if __name__ == '__main__':
    app.run(debug=True)
## marta.khoma 1424071908
## mongolo4ka_ 9264496810
