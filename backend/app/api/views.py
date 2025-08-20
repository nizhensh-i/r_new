from flask import jsonify, request, current_app, g, make_response
from flask_login import login_user, logout_user, login_required, current_user
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
from datetime import datetime
from functools import wraps
import jwt
from . import api
from .errors import unauthorized, bad_request
from ..models import User
from .. import db

# JWT认证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从请求头中获取token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return unauthorized('缺少认证令牌')
        
        try:
            # 解码token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['kaohao'])
            
            if not current_user:
                return unauthorized('无效的认证令牌')
            
            # 将当前用户存储在g对象中，以便在视图函数中使用
            g.current_user = current_user
        except:
            return unauthorized('无效的认证令牌')
        
        return f(*args, **kwargs)
    
    return decorated

# 登录
@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data:
        return bad_request('无效的请求数据')
    
    kaohao = data.get('kaohao')
    password = data.get('password')
    
    if not kaohao or not password:
        return bad_request('请提供准考证号和密码')
    
    user = User.query.get(kaohao)
    
    if not user or not user.validate_password(password):
        return unauthorized('准考证号或密码错误')
    
    # 生成JWT令牌
    token = jwt.encode(
        {'kaohao': user.kaohao, 'exp': int(datetime.utcnow().timestamp() + 24 * 3600)},
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    # 返回用户信息和令牌
    return jsonify({
        'token': token,
        'user': {
            'kaohao': user.kaohao,
            'college': user.college,
            'major': user.major,
            'subject1_code': user.subject1_code,
            'subject1_score': user.subject1_score,
            'subject2_code': user.subject2_code,
            'subject2_score': user.subject2_score,
            'subject3_code': user.subject3_code,
            'subject3_score': user.subject3_score,
            'subject4_code': user.subject4_code,
            'subject4_score': user.subject4_score,
            'net_score': user.net_score,
            'total_score': user.total_score
        }
    })

# 退出登录
@api.route('/logout')
def logout():
    return jsonify({'message': '已安全退出登录'})

# 查询成绩（注册）
@api.route('/cjcx', methods=['POST'])
def cjcx():
    data = request.get_json()
    
    if not data:
        return bad_request('无效的请求数据')
    
    kaohao = data.get('kaohao')
    name = data.get('name')
    id_number = data.get('id')
    password = data.get('password')
    code = data.get('code')
    
    if not all([kaohao, name, id_number, password, code]):
        return bad_request('请提供所有必要的信息')
    
    # 检查用户是否已存在
    user = User.query.get(kaohao)
    if user:
        return bad_request('此准考证号已查过成绩，请直接登录')
    
    # 构造查询表单数据
    form_data = {
        'kaohao': kaohao,
        'name': name,
        'id': id_number,
        'code': code
    }
    
    # 查询成绩
    # r = scrawl_score(form_data)
    
    # if not isinstance(r, requests.Response):
    #     return bad_request(r)
    
    # # 解析HTML数据并插入新用户
    # user_data = parse_html_data(r.text)
    # user = User.insert_new(user_data, password)

    # 使用模拟数据
    user = User.insert_new(parse_html_data(data), password=password)
    
    if not user:
        return bad_request('数据插入失败，请联系管理员')
    
    # 生成JWT令牌
    token = jwt.encode(
        {'kaohao': user.kaohao, 'exp': int(datetime.utcnow().timestamp() + 24 * 3600)},
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    # 返回用户信息和令牌
    return jsonify({
        'token': token,
        'user': {
            'kaohao': user.kaohao,
            'college': user.college,
            'major': user.major,
            'subject1_code': user.subject1_code,
            'subject1_score': user.subject1_score,
            'subject2_code': user.subject2_code,
            'subject2_score': user.subject2_score,
            'subject3_code': user.subject3_code,
            'subject3_score': user.subject3_score,
            'subject4_code': user.subject4_code,
            'subject4_score': user.subject4_score,
            'net_score': user.net_score,
            'total_score': user.total_score
        }
    })

# 修改密码
@api.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    
    if not data:
        return bad_request('无效的请求数据')
    
    password = data.get('password')
    
    if not password:
        return bad_request('请提供新密码')
    
    # 判断是否已登录
    token = None
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
    
    if token:
        try:
            # 已登录状态下修改密码
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user = User.query.get(data['kaohao'])
            
            if not user:
                return unauthorized('无效的认证令牌')
            
            if user.change_password(password) is None:
                return bad_request('修改密码失败，请联系管理员')
            
            return jsonify({'message': '修改密码成功'})
        except:
            pass
    
    # 未登录状态下修改密码
    kaohao = data.get('kaohao')
    name = data.get('name')
    id_number = data.get('id')
    code = data.get('code')
    
    if not all([kaohao, name, id_number, code]):
        return bad_request('请提供所有必要的信息')
    
    # 构造查询表单数据
    form_data = {
        'kaohao': kaohao,
        'name': name,
        'id': id_number,
        'code': code
    }
    
    # 查询成绩
    # r = scrawl_score(form_data)
    
    # if not isinstance(r, requests.Response):
    #     return bad_request(r)
    
    user = User.query.get(kaohao)
    if not user:
        return bad_request('未找到该用户，请先查询成绩')
    
    if user.change_password(password) is None:
        return bad_request('修改密码失败，请联系管理员')
    
    return jsonify({'message': '修改密码成功'})

# 获取验证码
@api.route('/captcha')
def get_validate_image():
    url = 'http://yzb2.ustc.edu.cn/api/captcha'
    r = requests.get(url)
    response = make_response(r.content)
    response.headers['Content-Type'] = 'image/jpg'
    return response

# 获取个人成绩
@api.route('/score')
@token_required
def score():
    user = g.current_user
    
    return jsonify({
        'user': {
            'kaohao': user.kaohao,
            'college': user.college,
            'major': user.major,
            'subject1_code': user.subject1_code,
            'subject1_score': user.subject1_score,
            'subject2_code': user.subject2_code,
            'subject2_score': user.subject2_score,
            'subject3_code': user.subject3_code,
            'subject3_score': user.subject3_score,
            'subject4_code': user.subject4_code,
            'subject4_score': user.subject4_score,
            'net_score': user.net_score,
            'total_score': user.total_score
        }
    })

# 按总分排名
@api.route('/ranking_total/<college>/<major>')
@token_required
def ranking_total(college, major):
    page = request.args.get('page', 1, type=int)
    
    pagination = User.query.filter_by(college=college, major=major).order_by(User.total_score.desc()).paginate(
        page=page, per_page=current_app.config["USERS_PER_PAGE"], error_out=False
    )
    
    users = pagination.items
    users_data = []
    
    for user in users:
        users_data.append({
            'kaohao': user.kaohao,
            'subject1_score': user.subject1_score,
            'subject2_score': user.subject2_score,
            'subject3_score': user.subject3_score,
            'subject4_score': user.subject4_score,
            'net_score': user.net_score,
            'total_score': user.total_score
        })
    
    return jsonify({
        'users': users_data,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    })

# 按除政治后总分排名
@api.route('/ranking_net/<college>/<major>')
@token_required
def ranking_net(college, major):
    page = request.args.get('page', 1, type=int)
    
    pagination = User.query.filter_by(college=college, major=major).order_by(User.net_score.desc()).paginate(
        page=page, per_page=current_app.config["USERS_PER_PAGE"], error_out=False
    )
    
    users = pagination.items
    users_data = []
    
    for user in users:
        users_data.append({
            'kaohao': user.kaohao,
            'subject1_score': user.subject1_score,
            'subject2_score': user.subject2_score,
            'subject3_score': user.subject3_score,
            'subject4_score': user.subject4_score,
            'net_score': user.net_score,
            'total_score': user.total_score
        })
    
    return jsonify({
        'users': users_data,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    })

# 从 USTC网站上查询成绩
def scrawl_score(form_data):
    post_url = 'http://yzb2.ustc.edu.cn/cjcx'
    r = requests.post(post_url, data=form_data)
    
    if "未查询到相关记录" in r.text:
        return "未查询到相关记录，请仔细检查或稍后再试"
    
    if "错误" in r.text:
        return "验证码错误，请重新输入或稍后再试"
    
    if "result" not in r.text:
        return "成绩抓取失败，请重新输入或稍后再试"
    
    return r

# 从html爬取考生信息及分数
# def parse_html_data(html):
#     bs = BeautifulSoup(html, 'html.parser')
#     base_info = bs.select('.info-phone')[0].contents[1].contents[1].contents
#     kaohao = base_info[7].contents[3].text
#     temp_list = str.split(base_info[9].contents[3].text)
#     college = temp_list[0]
#     major = temp_list[1]
#     subjects = bs.select('.result')[0].contents[1].contents[3].contents
#     first_name = subjects[1].contents[1].text + subjects[1].contents[3].text
#     first_score = int(subjects[1].contents[5].text)
#     second_name = subjects[3].contents[1].text + subjects[3].contents[3].text
#     second_score = int(subjects[3].contents[5].text)
#     third_name = subjects[5].contents[1].text + subjects[5].contents[3].text
#     third_score = int(subjects[5].contents[5].text)
#     fourth_name = subjects[7].contents[1].text + subjects[7].contents[3].text
#     fourth_score = int(subjects[7].contents[5].text)
#     total_score = int(subjects[9].contents[3].text)
#     return (kaohao, college, major, first_name, first_score, second_name, second_score, third_name, third_score,
#             fourth_name, fourth_score, total_score)


# 从html爬取考生信息及分数（模拟数据）
def parse_html_data(data):
    import random
    kaohao = data.get('kaohao')
    college = '225软件学院'
    major = '085400电子信息'
    first_name = '思想政治理论'
    first_score = random.randint(60, 80)
    second_name = '英语二'
    second_score = random.randint(70, 90)
    third_name = '数学二'
    third_score = random.randint(80, 100)
    fourth_name = '计算机专业基础'
    fourth_score = random.randint(90, 120)
    total_score = first_score + second_score + third_score + fourth_score
    return (kaohao, college, major, first_name, first_score, second_name, second_score, third_name, third_score,
            fourth_name, fourth_score, total_score)