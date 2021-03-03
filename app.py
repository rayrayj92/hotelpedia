from flask import Flask, render_template, jsonify, request, session, redirect, url_for

app = Flask(__name__)

from pymongo import MongoClient

# client = MongoClient('mongodb://13.125.251.48', 27017, username="test", password="test")
client = MongoClient('localhost', 27017)
db = client.plus_week1

# JWT 토큰을 만들 때 필요한 비밀문자열
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있음
SECRET_KEY = 'HOTELPEDIA'

# JWT 패키지
import jwt

# 토큰 만료시간
import datetime

# 비밀번호 암호화.
import hashlib

## HTML 화면 보여주기
@app.route('/')
def homework():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"email": payload['email']})
        return render_template('index.html', email=user_info["email"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# [회원가입 API]
# email, name, phone, image, paasword를  받아서, mongoDB에 저장
# 저장하기 전 password를 암호화해서 저장.
@app.route('/api/signup', methods=['POST'])
def sign_up():
    email_receive = request.form['email_give']
    name_receive = request.form['name_give']
    phone_receive = request.form['phone_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    doc = {'email': email_receive, 'password': pw_hash,
           'name': name_receive, 'phone':phone_receive}

    db.users.insert_one(doc)

    return jsonify({'result': 'success'})

# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/api/signin', methods=['POST'])
def signin():
    # 입력한 email / password를 받는다
    email_receive = request.form['email_give']
    password_receive = request.form['password_give']

    # password 암호화
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    # email, password(암호화)를 가지고 해당 유저를 찾는다
    result = db.users.find_one({'email': email_receive, 'password': pw_hash})

    # 발견시 JWT 토큰을 만들고 발급
    if result is not None:
        payload = {
            'email': email_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

# [유저 정보 확인 API]
# 로그인된 유저 확인해주는 API
@app.route('/api/', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)
        userinfo = db.user.find_one({'phone': payload['phone']}, {'_id': 0})
        return jsonify({'result': 'success', 'phone': userinfo['phone']})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지나면 에러
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)