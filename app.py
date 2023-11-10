from datetime import datetime
from functools import wraps
import random
import smtplib

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
            # expiration_time = datetime.utcnow() + timedelta(hours=1)
            # token = jwt.encode({'username': username, 'exp': expiration_time},
            #                    SECRET_KEY, algorithm='HS256')
            return jsonify(success=True)

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
        token = jwt.encode({'username': username},
                           SECRET_KEY, algorithm='HS256')
        return jsonify(success=True, token=token)
    else:
        return jsonify(success=False, error='Invalid credentials')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(success=False, error='Token is missing'), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            username = data['username']

        except jwt.InvalidTokenError:
            return jsonify(success=False, error='Invalid token'), 401
        return f(username, *args, **kwargs)

    return decorated

@app.route("/display/<username>", methods=['GET'])
@token_required
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
@app.route("/usersignup", methods=['POST'])
def usersignup():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        email=data['email']
        phonenumber=data['phonenumber']
        con = mysql.connection.cursor()
        sql1 = "SELECT count(*) as count FROM userinfo WHERE username = %s"
        con.execute(sql1, (username,))
        usernamecount = con.fetchone()
        print(usernamecount['count'], "result")
        con.close()
        if usernamecount['count'] < 1:
            con = mysql.connection.cursor()
            sql = "INSERT INTO userinfo (username, password, email,phonenumber) VALUES (%s, %s, %s,%s)"
            con.execute(sql, (username, password, email,phonenumber))
            mysql.connection.commit()
            con.close()
            return jsonify(success=True)
        else:
            return jsonify(error='username already exists')
    except Exception as e:
        print(e)
        return jsonify(error='DB error')


global_otp= None
def generate_otp():
    return str(random.randint(10000, 99999))

@app.route("/forgotpasswordotp", methods=['GET'])
def forgotpasswordotp():
    try:
        global global_otp
        data = request.get_json()
        email = data['email']
        otp = generate_otp()
        global_otp=otp
        print(global_otp)
        send_otp_email(email, otp)
        return jsonify(success=True, message='OTP sent successfully')
    except Exception as e:
        print(e)
        return jsonify(error='Failed to send OTP')

@app.route("/otpverify",methods=['GET'])
def otpverify():
    try:
        data=request.get_json()
        email=data['email']
        otp=data['otp']
        print(global_otp,otp)
        if otp==global_otp:
            return jsonify(message='OTP VALID',success=True)
        else:
            return jsonify(message='OTP INVALID',success=False)
    except Exception as e:
        return jsonify(error='Failed to verify')

def send_otp_email(email, otp):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'sharshini2003@gmail.com'
    smtp_password = 'znwm mgfw jaxc bdyp'
    from_email = 'sharshini2003@gmail.com'
    to_email = email

    subject = 'OTP Verification'
    body = f'Your OTP is: {otp}. \n This is to verify your account for FORGOT-PASSWORD-VERIFICATION. \n\n Note: This is an auto-generated mail. Don\'t reply to this email.'

    message = f'Subject: {subject}\n\n{body}'

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(from_email, to_email, message)



if (__name__ == '__main__'):
    app.secret_key = "abc123"
    app.run(debug=True)