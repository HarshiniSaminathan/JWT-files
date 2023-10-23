from datetime import datetime

import jwt
from flask import Flask, render_template, url_for, redirect, request, flash, jsonify
from flask_mysqldb import MySQL
from datetime import datetime, timedelta

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "Harshini@2003"
app.config["MYSQL_DB"] = "JWT"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)

SECRET_KEY = "Harshini@2003"
@app.route("/signup", methods=['POST'])
def signup():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        fullname = data['fullname']
        con = mysql.connection.cursor()
        sql1 = "SELECT count(*) as count FROM users WHERE username = %s"
        con.execute(sql1, (username,))
        usernamecount = con.fetchone()
        print(usernamecount['count'], "result")
        con.close()
        if usernamecount['count'] < 1:
            con = mysql.connection.cursor()
            sql = "INSERT INTO users (username, password, fullname) VALUES (%s, %s, %s)"
            con.execute(sql, (username, password, fullname))
            mysql.connection.commit()
            con.close()
            expiration_time = datetime.utcnow() + timedelta(hours=1)
            token = jwt.encode({'username': username, 'exp': expiration_time},
                               SECRET_KEY, algorithm='HS256')
            return jsonify(success=True, token=token)

        else:
            return jsonify(error='username already exists')
    except Exception as e:
        print(e)
        return jsonify(error='DB error')


@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    con = mysql.connection.cursor()
    sql = "SELECT count(*) as count FROM users WHERE username = %s AND password = %s"
    con.execute(sql, (username, password))
    result = con.fetchone()
    print(result['count'], "result")
    con.close()
    if result['count'] == 1:
        expiration_time = datetime.utcnow() + timedelta(hours=1)
        token = jwt.encode({'username': username, 'exp': expiration_time},
                           SECRET_KEY, algorithm='HS256')
        return jsonify(success=True, token=token)
    else:
        return jsonify(success=False, error='Invalid credentials')

@app.route("/display/<username>", methods=['GET'])
def display(username):
    try:
        con = mysql.connection.cursor()
        sql = "SELECT fullname FROM users WHERE username = %s"
        con.execute(sql, (username,))
        result = con.fetchone()
        con.close()
        if result:
            fullname = result['fullname']
            return jsonify(success=True, fullname=fullname)
        else:
            return jsonify(success=False, error='User not found')
    except Exception as e:
        print(e)
        return jsonify(success=False, error='DB error')


if (__name__ == '__main__'):
    app.secret_key = "abc123"
    app.run(debug=True)