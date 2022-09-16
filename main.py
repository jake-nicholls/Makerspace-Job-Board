from flask import Flask, render_template, request, session, redirect

from requests_oauthlib import OAuth1Session

import os

import json

import sqlite3

from datetime import datetime, timezone, timedelta

app = Flask(__name__)

app.secret_key = 'dee'

consumer_key = os.environ['consumer_key']
consumer_secret = os.environ['consumer_secret']
test = OAuth1Session(consumer_key, client_secret=consumer_secret)
url = 'https://api.schoology.com/v1/course/2432500395/enrollments?start=0&limit=200&picture_size=tiny'
r = test.get(url)

users = json.loads(r.content)['enrollment']

names = []

for i in users:
    names.append(i['name_display'])

names.append("admin")


@app.route("/")
def index():
    if 'username' in session:
        print('logged in')
        con = sqlite3.connect("database.sqlite")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(
            "select title, description, status, people_required, date_created, creator_id, bagged_by, date_required from jobs"
        )
        jobData = cur.fetchall()
        print(jobData)
        return render_template("index.html", rows=jobData, session=session)
    else:
        return redirect("/login")


@app.route("/additem", methods=['POST', 'GET'])
def additem():
    if session['username'] == "admin":
        if request.method == "POST":
            try:
                print("ee")
                title = request.form['title']
                description = request.form['description']
                status = request.form['status']
                people_required = request.form['people_required']
                date = datetime.now(timezone(timedelta(hours=10)))
                date_created = date.strftime("%H:%M %d/%m/%Y")
                creator_id = request.form['creator_id']
                date_required = request.form['date_required']

                con = sqlite3.connect("database.sqlite")
                con.execute(
                    f"""INSERT INTO jobs (title, description, status, people_required, date_created, creator_id, bagged_by, date_required) VALUES(?,?,?,?,?,?,?,?);""",
                    (title, description, status, people_required, date_created,
                     creator_id, "[]", date_required))

                con.commit()
                print("ee")
                con.close()
            except:
                con.rollback()
                con.close()
            finally:
                return redirect("/")
        else:
            return redirect("/")
    else:
        return redirect("/")


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        name = request.form['name']
        studentNo = request.form['studentNo']
        if name == "admin" and studentNo == "admin":
            session['username'] = "admin"
            return redirect("/")
        else:
            for i in users:
                if name == i['name_display'] and studentNo == i['school_uid']:
                    session['username'] = i['school_uid']
                    return redirect("/")
            error = 'Incorrect student number.'
            return render_template("login.html", error=error, names=names)
    else:
        return render_template("login.html", names=names)


@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect("/")


@app.route("/reset")
def reset():
    conn = sqlite3.connect('database.sqlite')

    conn.execute("DROP TABLE jobs;")

    conn.execute(
        'CREATE TABLE jobs(job_id INTEGER PRIMARY KEY AUTOINCREMENT, title, description, status, people_required, date_created, creator_id, bagged_by, date_required);'
    )

    conn.execute(
        'INSERT INTO jobs (title, description, status, people_required, date_created, creator_id, bagged_by, date_required) VALUES("test title one","test description","pending","3","12:22 PM 4/04/2022","190262","[]", "5/04/2022");'
    )
    conn.execute(
        'INSERT INTO jobs (title, description, status, people_required, date_created, creator_id, bagged_by, date_required) VALUES("test title 2","test description 2","complete","5","12:43 PM 4/01/2022","190262","[]", "5/04/2022");'
    )

    conn.commit()

    conn.close()
    return redirect("/")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8080', debug=True)
