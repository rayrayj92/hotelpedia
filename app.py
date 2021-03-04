import os

import uuid

from flask import Flask, render_template, jsonify, request, redirect, url_for

app = Flask(__name__)

from pymongo import MongoClient

client = MongoClient('mongodb://13.125.251.48', 27017, username="test", password="test")
db = client.dbHotelpedia

from bson.objectid import ObjectId

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
def main():
    hotels = objectIdDecoder(list(db.hotels.find({'state': '서울', 'city': '강남'})))

    token_receive = request.cookies.get('mytoken')

    if token_receive:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return render_template("index.html", hotels=hotels, token=payload)

    return render_template("index.html", hotels=hotels, token=token_receive)

@app.route('/login')
def login():
    token_receive = request.cookies.get('mytoken')

    if token_receive:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return render_template('login.html', token=payload)

    return render_template('login.html', token=token_receive)


@app.route('/register')
def register():
    token_receive = request.cookies.get('mytoken')

    if token_receive:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return render_template('register.html', token=payload)

    return render_template('register.html', token=token_receive)

@app.route('/signup/confirm', methods=['POST'])
def confirm():
    email_receive = request.form['email_give']
    exists = bool(db.members.find_one({"email": email_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# [회원가입 API]
# email, name, phone, image, paasword를  받아서, mongoDB에 저장
# 저장하기 전 password를 암호화해서 저장.
@app.route('/api/signup', methods=['POST'])
def sign_up():
    email_receive = request.form['email_give']

    exists = bool(db.members.find_one({"email": email_receive}))
    if exists:
        return jsonify({'result': 'fail', 'msg' : '이미 존재하는 이메일입니다!'})

    name_receive = request.form['name_give']
    phone_receive = request.form['phone_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    file = request.files["file_give"]

    extension = file.filename.split('.')[-1]

    myuuid = uuid.uuid4()
    myuuidStr = str(myuuid)
    # 익스텐션을 이미지파일만 아래코드 실행가능
    #save_to = os.path.join(app.root_path, f'static/member_image/{myuuidStr}.{extension}')
    save_to = f'./static/member_image/{myuuidStr}.{extension}'

    file.save(save_to)

    doc = {'email': email_receive, 'password': pw_hash,
           'name': name_receive, 'phone': phone_receive,
           'file': save_to}

    db.members.insert_one(doc)

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
    result = db.members.find_one({'email': email_receive, 'password': pw_hash})
    # 발견시 JWT 토큰을 만들고 발급
    if result is not None:
        payload = {
            'email': email_receive,
            'name' : result['name'],
            'img' : result['file'],
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
        userinfo = db.users.find_one({'phone': payload['phone']}, {'_id': 0})
        return jsonify({'result': 'success', 'phone': userinfo['phone']})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지나면 에러
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


# [호텔 정보 조회 API]
@app.route('/hotels', methods=['GET'])
def get_hotels():
    state_receive = request.args.get("state_give")
    city_receive = request.args.get("city_give")
    hotels = objectIdDecoder(db.hotels.find({'state': state_receive, 'city': city_receive}))  # '_id':false 원랜 들어감
    # return render_template("index.html", hotels=hotels, state_receive=state_receive)
    return jsonify({'result': 'success', 'hotels': hotels})


def objectIdDecoder(list):
    results = []
    for document in list:
        document['_id'] = str(document['_id'])
        results.append(document)
    return results


# [예약 관련 호텔 및 회원 정보 조회 API]
@app.route('/detail/<id>')  # 잠시 보류// !!!payload 체크 필요!!!
def book_hotel(id):
    try:
        token_receive = request.cookies.get('mytoken')
        if token_receive is None:
            return redirect(url_for("login"))
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 앞뒤 <> 잘라야함 < 603e09f7aac3e9552ef296c9 > -> 완료
        hotel_info = db.hotels.find_one({"_id": ObjectId(id)})  # hotels 디비에서 가져옴

        return render_template("detail.html", hotel_info=hotel_info, token=payload)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("/"))


# [예약 완료 db 삽입 API]
@app.route('/book_complete', methods=['POST'])  # 잠시 보류// !!!payload 체크 필요!!!
def book_complete():
    try:
        token_receive = request.cookies.get('mytoken')
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # member_info = db.users.find_one({"email": payload['email']}, {'_id': 0})  # members 디비에서 가져옴

        booker_name_receive = request.form['booker_name_give']
        booker_phone_receive = request.form['booker_phone_give']
        booker_email_receive = request.form['booker_email_give']
        hotel_name_receive = request.form['hotel_name_give']
        hotel_location_receive = request.form['hotel_location_give']
        hotel_price_receive = request.form['hotel_price_give']
        hotel_imageUrl_receive = request.form['hotel_imageUrl_give']
        checkin_date_receive = request.form['checkin_date_give']
        checkout_date_receive = request.form['checkout_date_give']
        people_receive = request.form['people_give']

        print(hotel_name_receive, checkin_date_receive)

        doc = {
            'member_email' : payload['email'],
            'booking_email': booker_email_receive,
            'booking_name': booker_name_receive,
            'member_phone': booker_phone_receive,
            'hotel_name': hotel_name_receive,
            'hotel_location': hotel_location_receive,
            'hotel_price': hotel_price_receive,
            'hotel_imageUrl': hotel_imageUrl_receive,
            'checkin_date': checkin_date_receive,
            'checkout_date': checkout_date_receive,
            'people': people_receive
        }
        db.bookings.insert_one(doc)
        return jsonify({'result': 'success', 'msg': '예약이 완료되었습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("/"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
