from flask import Flask, render_template, jsonify, request, session, redirect, url_for

# 회원가입 시, 비밀번호를 암호화
import hashlib
import bcrypt
from bson.json_util import dumps
from operator import itemgetter
# JWT 패키지
import jwt
from bson import ObjectId
import datetime
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.card

# JWT 비밀문자열
SECRET_KEY = 'SPARTA'


#로그인 페이지로 이동
@app.route('/login')
def login():
    return render_template('login.html')


# 회원가입 경로
@app.route('/register')
def register():
    return render_template("newMemberForm.html")


# 로그인
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['password_give']
    # pw를 암호화
    #해시로만
    # pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    # sault 추가
    encoded = pw_receive.encode('utf-8')
    pw_hash = bcrypt.hashpw(encoded, bcrypt.gensalt())

    print('---------------------------------------------------------------')
    print(pw_hash.decode('utf-8'))
    result = db.users.find_one({'email': id_receive})
    print(result['password'].decode('utf-8'))
    print(result['password'] == pw_hash)
    print(bcrypt.checkpw(pw_receive.encode('utf-8'), result['password']))
    print('---------------------------------------------------------------')

    if bcrypt.checkpw(pw_receive.encode('utf-8'), result['password']):
        #로그인 성공시
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        # token 주기
        return jsonify({'result': 'success', 'token': token})
    # 로그인 실패 시
    else:
        return jsonify({'result': 'fail', 'msg': '아이디 또는 비밀번호가 일치하지 않습니다.'})


@app.route('/')
def home():
    default_card_list = list(db.cards.find({'email': 'bbb@naver.com', 'card_bookmark': 0}))
    bookmark_card_list = list(db.cards.find({'email': 'bbb@naver.com', 'card_bookmark': 1}))
    # print(bookmark_card_list)

    return render_template('mainPage.html', default_card_list=default_card_list, bookmark_card_list=bookmark_card_list)



def get_word(select_word, input_word, bookmark):
    return list(db.cards.find({'email': 'bbb@naver.com', select_word: {'$regex': input_word}, 'card_bookmark': bookmark}))

#일반 리스트 검색
@app.route('/api/search', methods=['POST'])
def api_search():
    select_receive = request.form['select_give']
    input_receive = request.form['input_give']

    if select_receive == 'company':
        search_list = get_word('card_company', input_receive, 0)
        return jsonify({'result': dumps(search_list)})
    elif select_receive == 'name':
        search_list = get_word('card_name', input_receive, 0)
        return jsonify({'result': dumps(search_list)})
    elif select_receive == 'position':
        search_list = get_word('card_position', input_receive, 0)
        return jsonify({'result': dumps(search_list)})
    elif select_receive == 'role':
        search_list = get_word('card_role', input_receive, 0)
        return jsonify({'result': dumps(search_list)})
    elif select_receive == 'tel':
        search_list = get_word('card_tel', input_receive, 0)
        return jsonify({'result': dumps(search_list)})
    elif select_receive == 'email':
        search_list = get_word('card_email', input_receive, 0)
        return jsonify({'result': dumps(search_list)})

# 북마크 검색
@app.route('/api/search/bookmark', methods=['POST'])
def api_search_bookmark():
    select_receive = request.form['select_give']
    input_receive = request.form['input_give']

    if select_receive == 'company':
        search_list = get_word('card_company', input_receive, 1)
        return jsonify({'result': dumps(search_list)})
    elif select_receive == 'name':
        search_list = get_word('card_name', input_receive, 1)
        return jsonify({'result': dumps(search_list)})
    elif select_receive == 'position':
        search_list = get_word('card_position', input_receive, 1)
        return jsonify({'result': dumps(search_list)})
    elif select_receive == 'role':
        search_list = get_word('card_role', input_receive, 1)
        return jsonify({'result': dumps(search_list)})
    elif select_receive == 'tel':
        search_list = get_word('card_tel', input_receive, 1)
        return jsonify({'result': dumps(search_list)})
    elif select_receive == 'email':
        search_list = get_word('card_email', input_receive, 1)
        return jsonify({'result': dumps(search_list)})

# 일반 리스트 정렬
@app.route('/api/sort', methods=['POST'])
def api_sort():
    default_list_action_receive = request.form['default_list_action_give']

    default_list = list(db.cards.find({'email': 'bbb@naver.com', 'card_bookmark': 0}))

    if default_list_action_receive == 'register':
        return jsonify({'result': dumps(default_list)})
    elif default_list_action_receive == 'company':
        default_list = sorted(default_list, key=itemgetter('card_company'))
        return jsonify({'result': dumps(default_list)})
    elif default_list_action_receive == 'name':
        default_list = sorted(default_list, key=itemgetter('card_name'))
        return jsonify({'result': dumps(default_list)})

# 북마크 정렬
@app.route('/api/sort/bookmark', methods=['POST'])
def api_sort_bookmark():
    bookmark_list_action_receive = request.form['bookmark_list_action_give']

    bookmark_list = list(db.cards.find({'email': 'bbb@naver.com', 'card_bookmark': 1}))

    if bookmark_list_action_receive == 'register':
        return jsonify({'result': dumps(bookmark_list)})
    elif bookmark_list_action_receive == 'company':
        bookmark_list = sorted(bookmark_list, key=itemgetter('card_company'))
        return jsonify({'result': dumps(bookmark_list)})
    elif bookmark_list_action_receive == 'name':
        bookmark_list = sorted(bookmark_list, key=itemgetter('card_name'))
        return jsonify({'result': dumps(bookmark_list)})



# 리스트 작성 창에서 리스트 양식 값들 받아오기
@app.route('/api/pluscard', methods=['POST'])
def api_pluscard():
    # db schedule에 들어갈 정보들 dictionary 작성
    useremail = request.form['useremail']
    card_emailid = request.form['card_emailid']
    card_nameid = request.form['card_nameid']
    card_companyid = request.form['card_companyid']
    card_roleid = request.form['card_roleid']
    card_positionid = request.form['card_positionid']
    card_telid = request.form['card_telid']
    card_addressid = request.form['card_addressid']
    card_descid = request.form['card_descid']
    card_bookmarkid = int(request.form['card_bookmarkid'])

    doc = {
        "email": useremail,
        "card_email": card_emailid,
        # 카드 이미지 추가
        "card_name": card_nameid,
        "card_company": card_companyid,
        "card_role": card_roleid,
        "card_position": card_positionid,
        "card_tel": card_telid,
        "card_address": card_addressid,
        "card_desc": card_descid,
        "card_bookmark": card_bookmarkid,

        "register_time": datetime.now().timestamp()
    }
    print(doc)
    # db에 저장하기
    db.cards.insert_one(doc)
    return jsonify({'result': 'success', 'msg': '등록 성공하였습니다.'})


# 명함 삭제
@app.route('/api/list/delete', methods=["POST"])
def delete_card():
    card_id_receive = request.form['card_id_give']
    db.cards.delete_one({'_id': ObjectId(card_id_receive)})
    return jsonify({'msg': 'delete!'})


# 명함 즐겨찾기 등록 및 취소
@app.route('/api/list/bookmark', methods=["POST"])
def bookmark_card():
    card_id_receive = request.form['card_id_give']
    card = db.cards.find_one({'_id': ObjectId(card_id_receive)})

    if card['card_bookmark'] is 0:
        db.cards.update_one({'_id': ObjectId(card_id_receive)}, {"$set": {'card_bookmark': 1}})
        return jsonify({'msg': '즐겨찾기 등록완료'})
    else:
        db.cards.update_one({'_id': ObjectId(card_id_receive)}, {"$set": {'card_bookmark': 0}})
        return jsonify({'msg': '즐겨찾기 취소'})
    # return jsonify({'result': user})


@app.route('/newMember', methods=['POST'])
def post_new_member():
    email1 = request.form['email1']
    email2 = request.form['email2']
    # direct = request.direct['direct']
    # if direct == "":
    email = email1+'@'+email2
    # else:
    #     email = email1+'@'+direct
    name = request.form['name']
    password1 = request.form['password1']
    password2 = request.form['password2']
    company = request.form['company']
    role = request.form['role']
    position = request.form['position']
    tel = request.form['tel']
    address = request.form['address']

    if email1 == "" or email2 == "" or name == "" or password1 == "" or password2 == "" or company == "" or role == "":
        return jsonify({'msg': '필수 입력 사항을 확인 하세요'})

    emails = list(db.users.find({'email': email}, {'_id': False}))
    is_validate_email = False

    if(len(emails) == 0):
        is_validate_email = True
    else:
        return jsonify({'msg': '유효하지 않은 이메일'})

    if is_validate_email and (password1 == password2):
        encoded = password1.encode('utf-8')
        #pw_hash = hashlib.sha256(password1.encode('utf-8')).hexdigest()
        hash_password = bcrypt.hashpw(encoded, bcrypt.gensalt())
        doc = {'email': email, 'name': name, 'password': hash_password,
               'company': company, 'role': role, 'position': position, 'tel': tel, 'address': address}
        db.users.insert_one(doc)

    if is_validate_email and (password1 != password2):
        return jsonify({'msg': '비밀번호를 학인해 주세요'})

    return jsonify({'msg': '회원가입 완료'})

@app.route('/validate_email', methods=['POST'])
def validate_email():
    email = request.form['email']
    emails = list(db.users.find({'email': email}, {'_id': False}))
    is_validate = False
    if(len(emails) == 0):
        is_validate = True
    return jsonify({'validate': is_validate})


@app.route('/new_member_form')
def new_member_form():
    return render_template('newMemberForm.html')



# if __name__ == '__main__':
#     app.run('0.0.0.0', port=5000, debug=True)
#

if __name__ == '__main__':
    app.run('0.0.0.0', port=8080, debug=True)
