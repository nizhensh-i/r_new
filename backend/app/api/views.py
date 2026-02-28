from flask import jsonify, request, current_app, g, make_response
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
from datetime import datetime
import re
from functools import wraps
import jwt
import secrets
import threading
import time
from . import api
from .errors import unauthorized, bad_request, forbidden
from ..models import User

USTC_BASE_URL = 'https://xspt.ustc.edu.cn'
USTC_INDEX_URL = f'{USTC_BASE_URL}/sscjcx/index'
USTC_CAPTCHA_PATH = '/captcha/imageCode'
USTC_USER_AGENT = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/143.0.0.0 Safari/537.36'
)
CAPTCHA_SESSION_TTL_SECONDS = 300
_CAPTCHA_SESSION_CACHE = {}
_CAPTCHA_SESSION_LOCK = threading.Lock()


def _cleanup_captcha_sessions(now=None):
    if now is None:
        now = time.time()
    expired = []
    for token, entry in _CAPTCHA_SESSION_CACHE.items():
        if now - entry['created_at'] > CAPTCHA_SESSION_TTL_SECONDS:
            expired.append(token)
    for token in expired:
        _CAPTCHA_SESSION_CACHE.pop(token, None)


def _store_captcha_session(session, action_url, nd):
    token = secrets.token_urlsafe(16)
    now = time.time()
    with _CAPTCHA_SESSION_LOCK:
        _cleanup_captcha_sessions(now)
        _CAPTCHA_SESSION_CACHE[token] = {
            'session': session,
            'action_url': action_url,
            'nd': nd,
            'created_at': now
        }
    return token


def _get_captcha_session(token):
    if not token:
        return None
    now = time.time()
    with _CAPTCHA_SESSION_LOCK:
        _cleanup_captcha_sessions(now)
        entry = _CAPTCHA_SESSION_CACHE.get(token)
        if not entry:
            return None
        if now - entry['created_at'] > CAPTCHA_SESSION_TTL_SECONDS:
            _CAPTCHA_SESSION_CACHE.pop(token, None)
            return None
        return entry


def _parse_action_and_year(html):
    bs = BeautifulSoup(html, 'html.parser')
    form = bs.select_one('form#formId') or bs.find('form')
    action = form.get('action') if form else None
    if not action:
        return None, None
    if action.startswith('http://') or action.startswith('https://'):
        action_url = action
    elif action.startswith('/'):
        action_url = f'{USTC_BASE_URL}{action}'
    else:
        action_url = f'{USTC_BASE_URL}/{action}'
    nd_value = None
    nd_input = bs.select_one('input[name="nd"]')
    if nd_input and nd_input.get('value'):
        nd_value = nd_input.get('value').strip()
    return action_url, nd_value


def _init_ustc_session():
    session = requests.Session()
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "User-Agent": USTC_USER_AGENT
    }
    try:
        r = session.get(USTC_INDEX_URL, headers=headers, timeout=10)
    except requests.RequestException:
        return None, None, None, '成绩查询入口不可用，请稍后再试'
    if r.status_code != 200 or not r.text:
        return None, None, None, '成绩查询入口不可用，请稍后再试'
    action_url, nd_value = _parse_action_and_year(r.text)
    if not action_url:
        return None, None, None, '无法获取查询入口，请刷新验证码重试'
    return session, action_url, nd_value, None

def _get_college_options():
    allowlist = current_app.config.get('RANKING_COLLEGE_ALLOWLIST') or []
    blocklist = current_app.config.get('RANKING_COLLEGE_BLOCKLIST') or []
    options = [c for c in allowlist if c] if allowlist else []
    if not options:
        try:
            rows = User.query.with_entities(User.college).distinct().order_by(User.college).all()
            options = [row[0] for row in rows if row and row[0]]
        except Exception:
            options = []
    if blocklist and not allowlist:
        options = [c for c in options if c not in blocklist]
    return options

def _is_college_allowed(college):
    allowlist = current_app.config.get('RANKING_COLLEGE_ALLOWLIST') or []
    blocklist = current_app.config.get('RANKING_COLLEGE_BLOCKLIST') or []
    if not allowlist:
        if not blocklist:
            return True
        if not college:
            return False
        return college.strip() not in blocklist
    if not college:
        return False
    return college.strip() in allowlist

def _display_college_name(college):
    if not college:
        return '该学院'
    return re.sub(r'^\s*\d+\s*', '', college).strip() or '该学院'

def _build_super_admin_user():
    return {
        'kaohao': current_app.config.get('SUPER_ADMIN_KAOHAO'),
        'college': current_app.config.get('SUPER_ADMIN_DEFAULT_COLLEGE') or '',
        'major': current_app.config.get('SUPER_ADMIN_DEFAULT_MAJOR') or '',
        'subject1_code': '',
        'subject1_score': 0,
        'subject2_code': '',
        'subject2_score': 0,
        'subject3_code': '',
        'subject3_score': 0,
        'subject4_code': '',
        'subject4_score': 0,
        'net_score': 0,
        'total_score': 0,
        'is_super_admin': True
    }

def _is_super_admin_login(kaohao, password):
    if not current_app.config.get('SUPER_ADMIN_ENABLED'):
        return False
    return (
        kaohao == current_app.config.get('SUPER_ADMIN_KAOHAO') and
        password == current_app.config.get('SUPER_ADMIN_PASSWORD')
    )

def _generate_token(kaohao, role=None):
    payload = {
        'kaohao': kaohao,
        'exp': int(datetime.utcnow().timestamp() + 24 * 3600)
    }
    if role:
        payload['role'] = role
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

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
            if data.get('role') == 'super_admin':
                g.current_user = _build_super_admin_user()
                g.is_super_admin = True
            else:
                current_user = User.query.get(data['kaohao'])
                if not current_user:
                    return unauthorized('无效的认证令牌')
                # 将当前用户存储在g对象中，以便在视图函数中使用
                g.current_user = current_user
                g.is_super_admin = False
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
    
    if _is_super_admin_login(kaohao, password):
        token = _generate_token(kaohao, role='super_admin')
        return jsonify({
            'token': token,
            'user': _build_super_admin_user()
        })

    user = User.query.get(kaohao)
    if not user or not user.validate_password(password):
        return unauthorized('准考证号或密码错误')

    token = _generate_token(user.kaohao)

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
            'total_score': user.total_score,
            'is_super_admin': False
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
    id_number = data.get('id')
    password = data.get('password')
    code = data.get('code')
    college_input = (data.get('college') or '').strip()
    
    if not all([kaohao, id_number, password, code, college_input]):
        return bad_request('请提供所有必要的信息')
    
    # 检查用户是否已存在
    user = User.query.get(kaohao)
    if user:
        return bad_request('此准考证号已查过成绩，请直接登录')

    college_options = _get_college_options()
    if college_options and college_input not in college_options:
        return bad_request('学院不在列表中，请重新选择')

    captcha_token = request.cookies.get('captcha_session')
    captcha_ctx = _get_captcha_session(captcha_token)
    if not captcha_ctx:
        return bad_request('验证码已过期，请刷新验证码后再试')

    # 构造查询表单数据
    form_data = {
        'nd': captcha_ctx.get('nd') or 2026,
        'username': kaohao,
        'password': id_number,
        'validateCode': code,
        
    }
    # 查询成绩
    r = scrawl_score(form_data, captcha_ctx['session'], captcha_ctx['action_url'])
    
    if not isinstance(r, requests.Response):
        return bad_request(r)
    
    # 解析HTML数据并插入新用户
    try:
        user_data = parse_html_data(r.text)
    except Exception:
        return bad_request('成绩解析失败，请刷新验证码后重试')
    if not user_data:
        return bad_request('成绩解析失败，请刷新验证码后重试')
    user_data = list(user_data)
    user_data[1] = college_input
    user_data = tuple(user_data)
    college = college_input
    if not _is_college_allowed(college):
        college_label = _display_college_name(college)
        return forbidden(f'未开放{college_label}分数排名')

    user = User.insert_new(user_data, password=password)
    
    if not user:
        return bad_request('数据插入失败，请联系管理员')
    
    # 生成JWT令牌
    token = _generate_token(user.kaohao)
    
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
            'total_score': user.total_score,
            'is_super_admin': False
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
    id_number = data.get('id')
    code = data.get('code')
    
    if not all([kaohao, id_number, code]):
        return bad_request('请提供所有必要的信息')

    captcha_token = request.cookies.get('captcha_session')
    captcha_ctx = _get_captcha_session(captcha_token)
    if not captcha_ctx:
        return bad_request('验证码已过期，请刷新验证码后再试')
    
    # 构造查询表单数据
    form_data = {
        'username': kaohao,
        'password': id_number,
        'validateCode': code,
        'nd': captcha_ctx.get('nd') or '2026'
    }
    
    # 查询成绩
    r = scrawl_score(form_data, captcha_ctx['session'], captcha_ctx['action_url'])
    
    if not isinstance(r, requests.Response):
        return bad_request(r)
    
    user = User.query.get(kaohao)
    if not user:
        return bad_request('未找到该用户，请先查询成绩')
    
    if user.change_password(password) is None:
        return bad_request('修改密码失败，请联系管理员')
    
    return jsonify({'message': '修改密码成功'})

# 获取验证码（需与查询同一会话）
@api.route('/captcha')
def get_validate_image():
    session, action_url, nd_value, err = _init_ustc_session()
    if err:
        return bad_request(err)
    captcha_url = f'{USTC_BASE_URL}{USTC_CAPTCHA_PATH}?curDate={int(time.time() * 1000)}'
    headers = {
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "User-Agent": USTC_USER_AGENT,
        "Referer": USTC_INDEX_URL
    }
    try:
        r = session.get(captcha_url, headers=headers, timeout=10)
    except requests.RequestException:
        return bad_request('验证码获取失败，请刷新重试')
    if r.status_code != 200 or not r.content:
        return bad_request('验证码获取失败，请刷新重试')

    token = _store_captcha_session(session, action_url, nd_value)
    response = make_response(r.content)
    response.headers['Content-Type'] = r.headers.get('Content-Type', 'image/jpeg')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.set_cookie(
        'captcha_session',
        token,
        httponly=True,
        samesite='Lax',
        max_age=CAPTCHA_SESSION_TTL_SECONDS
    )
    return response

# 获取个人成绩
@api.route('/score')
@token_required
def score():
    user = g.current_user
    if isinstance(user, dict) and user.get('is_super_admin'):
        return jsonify({'user': user})

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
            'total_score': user.total_score,
            'is_super_admin': False
        }
    })

@api.route('/public_config')
def public_config():
    return jsonify({
        'ranking_college_allowlist': current_app.config.get('RANKING_COLLEGE_ALLOWLIST') or [],
        'ranking_college_blocklist': current_app.config.get('RANKING_COLLEGE_BLOCKLIST') or [],
        'ranking_college_block_message': current_app.config.get('RANKING_COLLEGE_BLOCK_MESSAGE') or '该学院排名已关闭'
    })

@api.route('/colleges')
def colleges():
    return jsonify({'colleges': _get_college_options()})

# 按总分排名
@api.route('/ranking_total/<college>/<major>')
@token_required
def ranking_total(college, major):
    page = request.args.get('page', 1, type=int)
    if not _is_college_allowed(college):
        return forbidden(current_app.config.get('RANKING_COLLEGE_BLOCK_MESSAGE') or '该学院排名已关闭')

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
    if not _is_college_allowed(college):
        return forbidden(current_app.config.get('RANKING_COLLEGE_BLOCK_MESSAGE') or '该学院排名已关闭')

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
def scrawl_score(form_data, session, action_url):
    if not session or not action_url:
        return '查询会话无效，请刷新验证码重试'
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "User-Agent": USTC_USER_AGENT,
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": USTC_BASE_URL,
        "Referer": action_url,
    }
    try:
        r = session.post(action_url, data=form_data, headers=headers, timeout=10)
    except requests.RequestException:
        return "成绩查询失败，请稍后再试"

    text = r.text or ""
    print("zmc_11", text)
    if "未查询到相关记录" in text:
        return "未查询到相关记录，请仔细检查或稍后再试"
    if "验证码错误" in text or ("验证码" in text and "错误" in text):
        return "验证码错误，请重新输入或稍后再试"
    if all(key not in text for key in ("result", "info-phone", "成绩单", "初试成绩单", "总分", "abc")):
        return "成绩抓取失败，请重新输入或稍后再试"

    return r

# 从html爬取考生信息及分数
def parse_html_data(html):
    bs = BeautifulSoup(html, 'html.parser')

    def _clean_text(node):
        if not node:
            return ''
        return ' '.join(node.stripped_strings).strip()

    def _parse_score(text):
        nums = re.findall(r'\d+', text or '')
        return int(nums[-1]) if nums else 0

    # 新版结构：成绩单表格
    table = bs.select_one('table.abc')
    if table:
        rows = table.find_all('tr')
        kaohao = ''
        college = ''
        major = ''
        major_text = ''
        subjects = []
        total_score = 0

        for row in rows:
            cells = row.find_all('td')
            if not cells:
                continue
            header = _clean_text(cells[0])
            if '准考证号' in header:
                if len(cells) >= 2:
                    kaohao = _clean_text(cells[1])
                continue
            if '报考专业' in header:
                if len(cells) >= 2:
                    major_text = _clean_text(cells[-1])
                continue
            if '总分' in header:
                if len(cells) >= 2:
                    total_score = _parse_score(_clean_text(cells[-1]))
                continue
            if re.search(r'\d{3}', header) and len(cells) >= 2:
                subject_name = header
                score = _parse_score(_clean_text(cells[-1]))
                subjects.append((subject_name, score))

        if major_text:
            parts = major_text.split()
            if len(parts) >= 2:
                college = parts[0]
                major = ''.join(parts[1:])
            else:
                major = major_text

        while len(subjects) < 4:
            subjects.append(('', 0))
        subjects = subjects[:4]

        if not total_score:
            total_score = sum(score for _, score in subjects)

        return (
            kaohao,
            college,
            major,
            subjects[0][0], subjects[0][1],
            subjects[1][0], subjects[1][1],
            subjects[2][0], subjects[2][1],
            subjects[3][0], subjects[3][1],
            total_score
        )

    # 旧版结构（兼容）
    base_info = bs.select('.info-phone')[0].contents[1].contents[1].contents
    kaohao = base_info[7].contents[3].text
    temp_list = str.split(base_info[9].contents[3].text)
    college = temp_list[0]
    major = temp_list[1]
    subjects = bs.select('.result')[0].contents[1].contents[3].contents
    first_name = subjects[1].contents[1].text + subjects[1].contents[3].text
    first_score = int(subjects[1].contents[5].text)
    second_name = subjects[3].contents[1].text + subjects[3].contents[3].text
    second_score = int(subjects[3].contents[5].text)
    third_name = subjects[5].contents[1].text + subjects[5].contents[3].text
    third_score = int(subjects[5].contents[5].text)
    fourth_name = subjects[7].contents[1].text + subjects[7].contents[3].text
    fourth_score = int(subjects[7].contents[5].text)
    total_score = int(subjects[9].contents[3].text)
    return (kaohao, college, major, first_name, first_score, second_name, second_score, third_name, third_score,
            fourth_name, fourth_score, total_score)
