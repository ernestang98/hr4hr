from flask import Flask
from flask import render_template
import sqlite3

app = Flask(__name__)
app.debug = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/hello_world')
def hello_world():
    return "Hello World!"


@app.route('/', methods=['POST', 'GET'])
def home():
    return render_template('index.html')


@app.route('/claim')
def claim():
    conn = sqlite3.connect('../bot/db.sqlite')
    cur = conn.cursor()
    conn.text_factory = str
    data = []
    for row in cur.execute("SELECT * FROM claims"):
        data.append(row)

    print(data)

    return render_template('claim.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
