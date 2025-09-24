from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
from datetime import datetime
import socket
import re
from collections import defaultdict
import pandas as pd
from werkzeug.utils import secure_filename
import requests

app = Flask(__name__)
app.secret_key = 'point_manager_secret_key_2024'

# 데이터 파일
DATA_FILE = 'point_data.json'
EMPLOYEE_FILE = 'employee_data.json'

# 잔디 웹훅 URL
JANDI_WEBHOOK_URL = 'https://wh.jandi.com/connect-api/webhook/14611962/0c004aecab37f46a168402c71d4cbaa7'

 # 업로드 설정
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 관리자 계정
ADMINS = {
    'admin1': 'admin123',
    'admin2': 'admin123'
}

def load_data():
    """데이터 로드"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return get_sample_data()
    else:
        data = get_sample_data()
        save_data(data)
        return data

def save_data(data):
    """데이터 저장"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_sample_data():
    """샘플 데이터"""
    return []

def load_employees():
    """직원 데이터 로드"""
    if os.path.exists(EMPLOYEE_FILE):
        try:
            with open(EMPLOYEE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    else:
        # 초기 직원 데이터
        employees = {
            'Paul': {'name': 'Paul(윤희선)', 'department': '평촌', 'total_points': 5000},
            'L': {'name': 'L(류주완)', 'department': '평촌', 'total_points': 5000},
            'Sammy': {'name': 'Sammy(육성일)', 'department': '평촌', 'total_points': 5000},
            'Kai': {'name': 'Kai(윤상훈)', 'department': '평촌', 'total_points': 5000},
            'Jack': {'name': 'Jack(정재락)', 'department': '판교', 'total_points': 5000},
            'Anna': {'name': 'Anna(이한영)', 'department': '판교', 'total_points': 10000},
            'Jake': {'name': 'Jake(조준현)', 'department': '광주', 'total_points': 15000},
            'James': {'name': 'James(정우석)', 'department': '광주', 'total_points': 20000},
            'Jinie': {'name': 'Jinie(이효진)', 'department': '판교', 'total_points': 5000},
            'Yup': {'name': 'Yup(김현엽)', 'department': '평촌', 'total_points': 5000},
            'Brown': {'name': 'Brown(권은성)', 'department': '평촌', 'total_points': 5000},
            'Jayone': {'name': 'Jayone(서재원)', 'department': '판교', 'total_points': 5000}
        }
        save_employees(employees)
        return employees

def save_employees(employees):
    """직원 데이터 저장"""
    with open(EMPLOYEE_FILE, 'w', encoding='utf-8') as f:
        json.dump(employees, f, ensure_ascii=False, indent=2)

def allowed_file(filename):
    """허용된 파일 확장자 확인"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_jandi_notification(title, message, color="#00d4ff"):
    """잔디로 알림 메시지 전송"""
    try:
        data = {
            "body": message,
            "connectColor": color,
            "connectInfo": [{
                "title": title,
                "description": message
            }]
        }

        response = requests.post(JANDI_WEBHOOK_URL, json=data, timeout=5)
        return response.status_code == 200

    except Exception as e:
        print(f"잔디 알림 전송 중 오류: {str(e)}")
        return False

def calculate_points(from_location, to_location):
    """경로에 따른 포인트 계산"""
    # 판교<->평촌: 5000원
    # 광주<->판교, 광주<->평촌: 10000원
    route = f"{from_location}-{to_location}"

    short_routes = ["판교-평촌", "평촌-판교"]
    long_routes = ["광주-평촌", "평촌-광주", "광주-판교", "판교-광주"]

    if route in short_routes:
        return 5000, 5000  # 요청자, 전달자
    elif route in long_routes:
        return 5000, 10000  # 요청자, 전달자
    else:
        return 5000, 5000  # 기본값

def parse_chat_message(message):
    """채팅 메시지에서 운송 정보 추출"""
    print(f"[DEBUG] parse_chat_message 시작: '{message}'")

    # 위치 패턴 (정확한 사무실 명칭)
    locations = {
        '평촌': ['평촌', '제조혁신센터'],
        '판교': ['판교', '판교R&D', '판교rnd', '1센터', '2센터'],
        '광주본사': ['광주본사', '광주', '본사'],
        '광주R&D': ['광주R&D', '광주rnd', 'R&D', 'rnd']
    }

    from_loc = None
    to_loc = None
    from_text = None
    to_text = None

    # 새로운 간단한 형식 처리: /싣고받고 [출발지] [도착지] [물품명] 또는 [출발지] [도착지] [물품명]
    if message.strip().startswith('/싣고받고'):
        parts = message.strip().split()
        if len(parts) >= 3:  # /싣고받고 출발지 도착지 (물품명은 선택사항)
            from_text = parts[1]
            to_text = parts[2]
    else:
        # 잔디 웹훅에서 data 필드로 오는 경우: "평촌 판교 센서"
        parts = message.strip().split()
        if len(parts) >= 2:  # 출발지 도착지 (물품명은 선택사항)
            from_text = parts[0]
            to_text = parts[1]

    # 위치 정규화
    if from_text and to_text:
        print(f"[DEBUG] from_text: '{from_text}', to_text: '{to_text}'")
        for key, values in locations.items():
            if any(v in from_text for v in values):
                from_loc = key
                print(f"[DEBUG] from_loc 찾음: {key}")
            if any(v in to_text for v in values):
                to_loc = key
                print(f"[DEBUG] to_loc 찾음: {key}")
    else:
        print(f"[DEBUG] from_text 또는 to_text가 없음: from_text='{from_text}', to_text='{to_text}'")

    # 위에서 찾지 못했다면 기존 복잡한 패턴들 시도 (하위 호환성)
    if not from_loc or not to_loc:
        patterns = [
            r'(평촌|판교|광주)[\s]*[→>-]+[\s]*(평촌|판교|광주)',
            r'(평촌|판교|광주)[\s]*--+>[\s]*(평촌|판교|광주)',
            r'(평촌|판교|광주)[\s]*에서[\s]*(평촌|판교|광주)[\s]*로',
            r'(평촌|판교|광주).*to.*(평촌|판교|광주)'
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                from_text = match.group(1)
                to_text = match.group(2)

                # 정규화
                for key, values in locations.items():
                    if any(v in from_text for v in values):
                        from_loc = key
                    if any(v in to_text for v in values):
                        to_loc = key

                if from_loc and to_loc:
                    break

    # 메시지 타입 분류
    message_type = 'unknown'
    requester = None
    transporter = None

    # 1. 운송 요청 메시지
    if message.strip().startswith('/싣고받고') and from_loc and to_loc:
        message_type = 'request'
        # 요청자는 메시지 작성자 (웹훅에서 sender로 전달됨)
    elif from_loc and to_loc:
        # 잔디 웹훅에서 data 필드로 "평촌 판교 센서" 형태로 오는 경우
        message_type = 'request'
        print(f"[DEBUG] 잔디 웹훅 요청으로 인식: from_loc={from_loc}, to_loc={to_loc}")
        # 요청자는 메시지 작성자 (웹훅에서 sender로 전달됨)
    elif any(keyword in message for keyword in ['이송 부탁', '전달 부탁', '전달 요청', '이동하시는 분', '운송 요청']):
        message_type = 'request'
        # 요청자는 메시지 작성자 (웹훅에서 sender로 전달됨)

    # 2. 전달 수락 메시지
    elif any(keyword in message for keyword in ['접수', '신청']):
        message_type = 'accept'
        # 전달자는 메시지 작성자

    # 3. 완료 메시지
    elif any(keyword in message for keyword in ['받았습니다', '수령했습니다', '잘 받았습니다', '완료']):
        message_type = 'complete'

    # 이름 패턴 추출 (태그된 사람들)
    name_pattern = r'@?([A-Za-z]+)\([가-힣]+\)'
    names = re.findall(name_pattern, message)

    return {
        'from_location': from_loc,
        'to_location': to_loc,
        'message_type': message_type,
        'names': names,
        'requester': requester,
        'transporter': transporter
    }

def get_next_id(data):
    """다음 ID 생성"""
    if not data:
        return 1
    return max(item['id'] for item in data) + 1

@app.route('/')
def index():
    """메인 페이지 - 바로 현황 조회로"""
    data = load_data()

    # 통계 계산
    requester_stats = defaultdict(lambda: {'count': 0, 'points': 0})
    transporter_stats = defaultdict(lambda: {'count': 0, 'points': 0})

    for record in data:
        if record.get('status') == '완료':
            requester = record.get('applicant', '')
            transporter = record.get('transporter', '')

            if requester:
                requester_stats[requester]['count'] += 1
                requester_stats[requester]['points'] += record.get('applicant_amount', 0)

            if transporter:
                transporter_stats[transporter]['count'] += 1
                transporter_stats[transporter]['points'] += record.get('transporter_amount', 0)

    # 상위 10명 추출 (동순위 고려)
    top_requesters = sorted(requester_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:10]
    top_transporters = sorted(transporter_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:10]

    # 동순위 처리를 위한 순위 계산
    def calculate_rank(sorted_list):
        result = []
        current_rank = 1
        prev_count = None

        for i, (name, stats) in enumerate(sorted_list):
            if prev_count is not None and stats['count'] != prev_count:
                current_rank = i + 1

            result.append({
                'name': name,
                'stats': stats,
                'rank': current_rank,
                'display_rank': current_rank if stats['count'] != prev_count or i == 0 else None
            })
            prev_count = stats['count']

        return result

    top_requesters_ranked = calculate_rank(top_requesters)
    top_transporters_ranked = calculate_rank(top_transporters)

    return render_template('dashboard.html',
                         records=data,
                         top_requesters=top_requesters_ranked,
                         top_transporters=top_transporters_ranked)

@app.route('/admin')
def admin():
    """관리자 페이지로 이동"""
    if session.get('user_type') != 'admin':
        return redirect(url_for('admin_login'))

    employees = load_employees()
    data = load_data()

    # 직원별 통계 계산
    for emp_id in employees:
        employees[emp_id]['request_count'] = 0
        employees[emp_id]['transport_count'] = 0
        employees[emp_id]['earned_points'] = 0

    for record in data:
        if record.get('status') == '완료':
            requester = record.get('applicant')
            transporter = record.get('transporter')

            if requester in employees:
                employees[requester]['request_count'] += 1
                employees[requester]['earned_points'] += record.get('applicant_amount', 0)

            if transporter and transporter in employees:
                employees[transporter]['transport_count'] += 1
                employees[transporter]['earned_points'] += record.get('transporter_amount', 0)

    return render_template('admin.html',
                         username=session.get('username'),
                         employees=employees)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    """관리자 로그인"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in ADMINS and ADMINS[username] == password:
            session['user_type'] = 'admin'
            session['username'] = f'관리자 ({username})'
            return redirect(url_for('admin'))
        else:
            return render_template('admin_login.html', error='ID 또는 비밀번호가 잘못되었습니다.')

    return render_template('admin_login.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    """웹훅 엔드포인트 - 채팅 메시지 자동 처리"""
    try:
        print(f"[DEBUG] 웹훅 요청 수신: {request.method} {request.url}")
        print(f"[DEBUG] Content-Type: {request.content_type}")
        print(f"[DEBUG] Raw data: {request.get_data()}")

        webhook_data = request.json
        if not webhook_data:
            print("[ERROR] JSON 데이터가 없습니다")
            return jsonify({'success': False, 'error': 'JSON 데이터가 필요합니다'})

        print(f"[DEBUG] 파싱된 JSON: {webhook_data}")

        # 잔디 웹훅 데이터 구조에 맞게 수정
        message = webhook_data.get('data', webhook_data.get('text', webhook_data.get('message', '')))
        sender = webhook_data.get('writerName', webhook_data.get('writer_name', webhook_data.get('sender', '익명')))
        timestamp = webhook_data.get('timestamp', datetime.now().isoformat())

        print(f"[DEBUG] 메시지: {message}")
        print(f"[DEBUG] 보낸이: {sender}")

        # 스레드/메시지 ID (잔디에서 제공되는 경우)
        thread_id = webhook_data.get('thread_id', webhook_data.get('message_id', None))
        reply_to = webhook_data.get('reply_to', None)  # 댓글인 경우 원본 메시지 ID

        # 메시지 파싱
        parsed = parse_chat_message(message)
        data = load_data()

        # 1. 운송 요청 메시지
        if parsed['message_type'] == 'request':
            if not parsed['from_location'] or not parsed['to_location']:
                # 위치 정보가 없는 경우
                send_jandi_notification(
                    "🏢 사무실 명칭을 정확히 입력해주세요",
                    f"**정확한 사무실 명칭을 사용해주세요!**\n\n📍 **사용 가능한 사무실:**\n• **평촌** (제조혁신센터)\n• **판교** (R&D센터)\n• **광주본사**\n• **광주R&D**\n\n📝 **예시:**\n`/싣고받고 평촌 판교 센서`\n`/싣고받고 광주본사 광주R&D 노트북`",
                    "#e74c3c"
                )
                return jsonify({'success': False, 'error': '위치 정보가 누락되었습니다.'})

            # 정상적인 요청 처리
            # 포인트 계산
            applicant_points, transporter_points = calculate_points(
                parsed['from_location'],
                parsed['to_location']
            )

            # 물품명 추출
            item = '물품'

            # /싣고받고 형식의 경우 세 번째 파라미터가 물품명
            if message.strip().startswith('/싣고받고'):
                parts = message.strip().split()
                if len(parts) >= 4:  # /싣고받고 출발지 도착지 물품명
                    item = parts[3]
                elif len(parts) == 3:  # 물품명이 없는 경우
                    item = '물품'
            else:
                # 기존 방식: 패턴 매칭
                item_patterns = ['센서', '박스', '노트북', 'ML-U', 'SL-U', '보드', '서버', '하드웨어']
                for pattern in item_patterns:
                    if pattern.lower() in message.lower():
                        item = pattern
                        break

            # 새 운송 요청 레코드 생성
            new_record = {
                'id': get_next_id(data),
                'request_date': timestamp[:10] if len(timestamp) >= 10 else datetime.now().strftime('%Y-%m-%d'),
                'applicant': sender,
                'transporter': '',  # 아직 정해지지 않음
                'from_location': parsed['from_location'],
                'to_location': parsed['to_location'],
                'item': item,
                'applicant_amount': applicant_points,
                'transporter_amount': transporter_points,
                'accumulate_date': '',
                'deadline_date': '',
                'status': '대기중',
                'created_at': datetime.now().isoformat(),
                'source': 'webhook',
                'thread_id': thread_id,  # 스레드 추적용
                'message_id': thread_id
            }

            data.append(new_record)
            save_data(data)

            # 잔디 알림 전송 (간단한 확인 메시지)
            send_jandi_notification(
                "✅ 접수완료",
                f"📋 **#{new_record['id']}번** {parsed['from_location']}→{parsed['to_location']} {item} | {applicant_points:,}P",
                "#27ae60"
            )

            return jsonify({'success': True, 'action': 'request_created', 'record': new_record})

        # 2. 전달 수락 메시지
        elif parsed['message_type'] == 'accept':
            # 댓글인 경우 특정 요청에 대한 수락, 아니면 가장 최근 요청
            target_requests = []

            if reply_to:
                # 특정 메시지에 대한 댓글인 경우
                target_requests = [r for r in data if r.get('message_id') == reply_to and r.get('status') == '대기중']
            else:
                # 일반 메시지인 경우 가장 최근 대기중인 요청
                target_requests = [r for r in data if r.get('status') == '대기중' and not r.get('transporter')]

            if target_requests:
                # 가장 최근 요청에 전달자 배정
                latest_request = max(target_requests, key=lambda x: x['created_at'])

                for i, record in enumerate(data):
                    if record['id'] == latest_request['id']:
                        data[i]['transporter'] = sender
                        data[i]['status'] = '진행중'
                        data[i]['updated_at'] = datetime.now().isoformat()
                        break

                save_data(data)

                # 잔디 알림 전송
                send_jandi_notification(
                    "✅ 접수완료!",
                    f"🚛 전달자: {sender}\n📦 요청: {latest_request['from_location']} → {latest_request['to_location']}\n물품: {latest_request['item']}\n\n배송을 시작해주세요!",
                    "#27ae60"
                )

                return jsonify({'success': True, 'action': 'transporter_assigned', 'record': data[i]})
            else:
                return jsonify({'success': False, 'error': '대기중인 운송 요청이 없습니다.'})

        # 3. 완료 메시지
        elif parsed['message_type'] == 'complete':
            # 가장 최근의 진행중인 요청 찾기
            in_progress = [r for r in data if r.get('status') == '진행중']

            if in_progress:
                # 가장 최근 요청을 완료로 변경
                latest_request = max(in_progress, key=lambda x: x.get('updated_at', x['created_at']))

                for i, record in enumerate(data):
                    if record['id'] == latest_request['id']:
                        data[i]['status'] = '완료'
                        data[i]['accumulate_date'] = datetime.now().strftime('%Y-%m-%d')
                        data[i]['completed_at'] = datetime.now().isoformat()
                        break

                save_data(data)

                # 잔디 알림 전송
                completed_record = data[i]
                send_jandi_notification(
                    "🎉 배송완료!",
                    f"✅ 운송이 완료되었습니다!\n\n요청자: {completed_record['applicant']} (+{completed_record['applicant_amount']:,}P)\n전달자: {completed_record['transporter']} (+{completed_record['transporter_amount']:,}P)\n경로: {completed_record['from_location']} → {completed_record['to_location']}\n물품: {completed_record['item']}\n\n포인트 적립 예정! 감사합니다! 🙏",
                    "#27ae60"
                )

                return jsonify({'success': True, 'action': 'completed', 'record': data[i]})
            else:
                return jsonify({'success': False, 'error': '진행중인 운송 요청이 없습니다.'})

        else:
            # 양식 안내 메시지 전송
            if any(keyword in message for keyword in ['운송', '이송', '전달', '배송']):
                send_jandi_notification(
                    "❓ 사용법",
                    "**간단한 키워드로 사용하세요!**\n\n🚚 **운송 요청**: `/싣고받고 평촌 판교 센서`\n✅ **전달 수락**: `접수` (댓글로)\n✅ **완료 확인**: `완료`",
                    "#f39c12"
                )
                return jsonify({'success': False, 'error': '양식 안내를 전송했습니다.'})
            else:
                return jsonify({'success': False, 'error': '인식할 수 없는 메시지 형식입니다.'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/parse_chat', methods=['POST'])
def parse_chat():
    """채팅 내용 일괄 파싱 API"""
    if session.get('user_type') != 'admin':
        return jsonify({'error': '권한이 없습니다.'}), 403

    chat_text = request.json.get('chat_text', '')
    lines = chat_text.split('\n')

    data = load_data()
    added_records = []
    current_date = None
    pending_requests = {}  # 대기중인 요청들

    for line in lines:
        # 날짜 패턴 확인
        date_match = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', line)
        if date_match:
            year = date_match.group(1)
            month = date_match.group(2).zfill(2)
            day = date_match.group(3).zfill(2)
            current_date = f"{year}-{month}-{day}"
            continue

        # 운송 요청 패턴
        if any(keyword in line for keyword in ['이동하시는 분', '이송 부탁', '전달 부탁', '전달 요청']):
            parsed = parse_chat_message(line)
            if parsed['from_location'] and parsed['to_location']:
                applicant_points, transporter_points = calculate_points(
                    parsed['from_location'],
                    parsed['to_location']
                )

                # 물품 추출
                item = '물품'
                item_patterns = ['센서', '박스', '노트북', 'ML-U', 'SL-U', '보드']
                for pattern in item_patterns:
                    if pattern.lower() in line.lower():
                        item = pattern
                        break

                new_record = {
                    'id': get_next_id(data),
                    'request_date': current_date or datetime.now().strftime('%Y-%m-%d'),
                    'applicant': parsed['requester'] or '미지정',
                    'transporter': '',
                    'from_location': parsed['from_location'],
                    'to_location': parsed['to_location'],
                    'item': item,
                    'applicant_amount': applicant_points,
                    'transporter_amount': transporter_points,
                    'accumulate_date': '',
                    'deadline_date': '',
                    'status': '진행중',
                    'created_at': datetime.now().isoformat(),
                    'source': 'chat_import'
                }

                # 요청자를 키로 저장
                if parsed['requester']:
                    pending_requests[parsed['requester']] = new_record

                data.append(new_record)
                added_records.append(new_record)

        # 전달 응답 패턴
        elif any(keyword in line for keyword in ['전달드리겠습니다', '제가 전달', '전달하겠습니다']):
            parsed = parse_chat_message(line)
            # 가장 최근의 관련 요청 찾기
            for requester, request in pending_requests.items():
                if request['status'] == '진행중' and not request['transporter']:
                    request['transporter'] = parsed['requester'] or parsed['transporter'] or '미지정'
                    break

        # 완료 패턴
        elif any(keyword in line for keyword in ['받았습니다', '수령했습니다', '잘 받았습니다']):
            parsed = parse_chat_message(line)
            # 관련 요청 찾아서 완료 처리
            for requester, request in list(pending_requests.items()):
                if request['status'] == '진행중':
                    request['status'] = '완료'
                    request['accumulate_date'] = current_date or datetime.now().strftime('%Y-%m-%d')
                    del pending_requests[requester]
                    break

    save_data(data)
    return jsonify({'success': True, 'added': len(added_records), 'records': added_records})

@app.route('/logout')
def logout():
    """로그아웃"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/records', methods=['GET'])
def get_records():
    """기록 조회 API"""
    data = load_data()
    
    # 검색 필터
    search = request.args.get('search', '').lower()
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    filtered_data = []
    for record in data:
        # 텍스트 검색
        text_match = (not search or 
                     search in record['applicant'].lower() or
                     search in record['transporter'].lower())
        
        # 날짜 필터
        date_match = True
        if date_from and record['accumulate_date'] < date_from:
            date_match = False
        if date_to and record['accumulate_date'] > date_to:
            date_match = False
            
        if text_match and date_match:
            filtered_data.append(record)
    
    return jsonify(filtered_data)

@app.route('/api/records', methods=['POST'])
def add_record():
    """기록 추가 API"""
    if session.get('user_type') != 'admin':
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    data = load_data()
    new_record = request.json
    new_record['id'] = get_next_id(data)
    new_record['created_at'] = datetime.now().isoformat()
    
    # deadline_date 필드가 없으면 빈 문자열로 설정
    if 'deadline_date' not in new_record:
        new_record['deadline_date'] = ''
    
    data.append(new_record)
    save_data(data)
    
    return jsonify({'success': True, 'record': new_record})

@app.route('/api/records/<int:record_id>', methods=['PUT'])
def update_record(record_id):
    """기록 수정 API"""
    if session.get('user_type') != 'admin':
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    data = load_data()
    updated_data = request.json
    
    for i, record in enumerate(data):
        if record['id'] == record_id:
            # deadline_date 필드가 없으면 빈 문자열로 설정
            if 'deadline_date' not in updated_data:
                updated_data['deadline_date'] = ''
            data[i].update(updated_data)
            data[i]['updated_at'] = datetime.now().isoformat()
            save_data(data)
            return jsonify({'success': True, 'record': data[i]})
    
    return jsonify({'error': '기록을 찾을 수 없습니다.'}), 404

@app.route('/api/records/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """기록 삭제 API"""
    if session.get('user_type') != 'admin':
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    data = load_data()
    data = [record for record in data if record['id'] != record_id]
    save_data(data)
    
    return jsonify({'success': True})

@app.route('/api/employees', methods=['GET'])
def get_employees():
    """직원 목록 조회 API"""
    employees = load_employees()
    return jsonify(employees)

@app.route('/api/employees', methods=['POST'])
def add_employee():
    """직원 추가 API"""
    if session.get('user_type') != 'admin':
        return jsonify({'error': '권한이 없습니다.'}), 403

    employee_data = request.json
    employees = load_employees()

    emp_id = employee_data['id']
    if emp_id in employees:
        return jsonify({'error': '이미 존재하는 ID입니다.'}), 400

    employees[emp_id] = {
        'name': employee_data['name'],
        'department': employee_data['department'],
        'total_points': employee_data.get('total_points', 0)
    }

    save_employees(employees)
    return jsonify({'success': True})

@app.route('/api/employees/<emp_id>', methods=['PUT'])
def update_employee(emp_id):
    """직원 정보 수정 API"""
    if session.get('user_type') != 'admin':
        return jsonify({'error': '권한이 없습니다.'}), 403

    update_data = request.json
    employees = load_employees()

    if emp_id not in employees:
        return jsonify({'error': '직원을 찾을 수 없습니다.'}), 404

    employees[emp_id].update(update_data)
    save_employees(employees)

    return jsonify({'success': True})

@app.route('/api/employees/<emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    """직원 삭제 API"""
    if session.get('user_type') != 'admin':
        return jsonify({'error': '권한이 없습니다.'}), 403

    employees = load_employees()

    if emp_id not in employees:
        return jsonify({'error': '직원을 찾을 수 없습니다.'}), 404

    del employees[emp_id]
    save_employees(employees)

    return jsonify({'success': True})

@app.route('/api/employees/upload', methods=['POST'])
def upload_employees():
    """엑셀 파일로 직원 일괄 등록"""
    if session.get('user_type') != 'admin':
        return jsonify({'error': '권한이 없습니다.'}), 403

    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '파일을 선택해주세요.'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # 엑셀 파일 읽기
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath, encoding='utf-8-sig')
            else:
                df = pd.read_excel(filepath)

            employees = load_employees()
            added_count = 0
            updated_count = 0

            # 필수 컬럼 확인
            required_cols = ['ID', '이름', '부서']
            for col in required_cols:
                if col not in df.columns:
                    return jsonify({'error': f'필수 컬럼 {col}이(가) 없습니다.'}), 400

            # 직원 데이터 처리
            for _, row in df.iterrows():
                emp_id = str(row['ID'])
                if emp_id in employees:
                    updated_count += 1
                else:
                    added_count += 1

                employees[emp_id] = {
                    'name': row['이름'],
                    'department': row['부서'],
                    'total_points': int(row.get('포인트', 0))
                }

            save_employees(employees)
            os.remove(filepath)  # 처리 후 파일 삭제

            return jsonify({
                'success': True,
                'added': added_count,
                'updated': updated_count
            })

        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'파일 처리 중 오류: {str(e)}'}), 400

    return jsonify({'error': '허용되지 않은 파일 형식입니다.'}), 400

@app.route('/api/employees/<emp_id>/points', methods=['POST'])
def adjust_points(emp_id):
    """포인트 수동 조정 API"""
    if session.get('user_type') != 'admin':
        return jsonify({'error': '권한이 없습니다.'}), 403

    adjustment = request.json.get('adjustment', 0)
    reason = request.json.get('reason', '')

    employees = load_employees()

    if emp_id not in employees:
        return jsonify({'error': '직원을 찾을 수 없습니다.'}), 404

    employees[emp_id]['total_points'] = employees[emp_id].get('total_points', 0) + adjustment
    save_employees(employees)

    # 포인트 조정 기록 추가 (옵션)
    data = load_data()
    adjustment_record = {
        'id': get_next_id(data),
        'request_date': datetime.now().strftime('%Y-%m-%d'),
        'applicant': emp_id,
        'transporter': 'SYSTEM',
        'from_location': '관리자조정',
        'to_location': '관리자조정',
        'item': f'포인트 조정: {reason}',
        'applicant_amount': adjustment if adjustment > 0 else 0,
        'transporter_amount': 0,
        'accumulate_date': datetime.now().strftime('%Y-%m-%d'),
        'deadline_date': '',
        'status': '완료',
        'created_at': datetime.now().isoformat(),
        'source': 'admin_adjustment'
    }
    data.append(adjustment_record)
    save_data(data)

    return jsonify({'success': True, 'new_points': employees[emp_id]['total_points']})

@app.route('/api/download_template')
def download_template():
    """엑셀 템플릿 다운로드"""
    template_data = {
        'ID': ['예시1', '예시2', '예시3'],
        '이름': ['홍길동', '김철수', '이영희'],
        '부서': ['평촌', '판교', '광주'],
        '포인트': [0, 0, 0]
    }

    df = pd.DataFrame(template_data)
    template_path = os.path.join(app.config['UPLOAD_FOLDER'], 'employee_template.xlsx')
    df.to_excel(template_path, index=False)

    from flask import send_file
    return send_file(template_path, as_attachment=True, download_name='직원등록_템플릿.xlsx')

@app.route('/api/stats')
def get_stats():
    """통계 API"""
    search = request.args.get('search', '').lower()
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    data = load_data()
    
    # 필터링된 데이터
    filtered_data = []
    for record in data:
        text_match = (not search or 
                     search in record['applicant'].lower() or
                     search in record['transporter'].lower())
        
        date_match = True
        if date_from and record['accumulate_date'] < date_from:
            date_match = False
        if date_to and record['accumulate_date'] > date_to:
            date_match = False
            
        if text_match and date_match:
            filtered_data.append(record)
    
    total_applicant = sum(record['applicant_amount'] for record in filtered_data)
    total_transporter = sum(record['transporter_amount'] for record in filtered_data)
    total_records = len(filtered_data)
    
    return jsonify({
        'total_applicant_amount': total_applicant,
        'total_transporter_amount': total_transporter,
        'total_records': total_records
    })

def get_local_ip():
    """로컬 IP 주소 가져오기"""
    try:
        # 임시 소켓을 만들어서 로컬 IP 확인
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

if __name__ == '__main__':
    print("=" * 50)
    print("포인트 지급 현황 관리 시스템 서버 시작")
    print("=" * 50)

    local_ip = get_local_ip()
    port = int(os.environ.get('PORT', 8000))

    print(f"로컬 접속 주소: http://localhost:{port}")
    print(f"내부망 접속 주소: http://{local_ip}:{port}")
    print("\n관리자 계정:")
    print("- ID: admin1, 비밀번호: admin123")
    print("- ID: admin2, 비밀번호: admin123")
    print("\n메인 페이지에서 바로 현황 조회 가능")
    print("관리자 페이지는 우측 상단 '관리자' 버튼으로 접속")
    print("\n서버를 중지하려면 Ctrl+C를 누르세요.")
    print("=" * 50)

    # Flask 서버 실행
    app.run(host='0.0.0.0', port=port, debug=False)
