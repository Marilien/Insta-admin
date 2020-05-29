from flask import (Flask,
    render_template
)

from flask_cors import  cross_origin
from rq import Queue
from rq.job import Job
from worker import conn


from followers_service import account_info, followers

q = Queue(connection=conn)
app = Flask(__name__)
@app.route('/')
@cross_origin()
def home():
    return render_template('home.html')

@app.route('/api/account_info/<username>')
@cross_origin()
def get_account_info(username):
    return account_info(username)

    
@app.route('/api/followers/<user_id>')
@cross_origin()
def get_followers(user_id):
    return followers(user_id)

@app.route('/task/<url>')
@cross_origin()
def handle_task(url):
    from utils import count_words_at_url
    job = q.enqueue(count_words_at_url, url)
    return job.get_id()


@app.route("/results/<job_key>")
@cross_origin()
def get_results(job_key):
    job = Job.fetch(job_key, connection=conn)
    if job.is_finished:
        print(job.result)
        return 200
    else:
        return "Nay!", 202

if __name__ == '__main__':
    app.run(port=80, debug=True)
