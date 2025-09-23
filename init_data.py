import json
from datetime import datetime

# 초기 데이터 생성
initial_data = [
    {
        "id": 1,
        "request_date": "2025-09-12",
        "applicant": "Paul",
        "transporter": "L",
        "from_location": "평촌",
        "to_location": "판교",
        "item": "센서 2개",
        "applicant_amount": 5000,
        "transporter_amount": 5000,
        "accumulate_date": "2025-09-16",
        "deadline_date": "",
        "status": "완료",
        "created_at": "2025-09-12T10:00:00",
        "source": "manual"
    },
    {
        "id": 2,
        "request_date": "2025-09-13",
        "applicant": "Sammy",
        "transporter": "Kai",
        "from_location": "평촌",
        "to_location": "판교",
        "item": "박스",
        "applicant_amount": 5000,
        "transporter_amount": 5000,
        "accumulate_date": "2025-09-17",
        "deadline_date": "",
        "status": "완료",
        "created_at": "2025-09-13T14:00:00",
        "source": "manual"
    },
    {
        "id": 3,
        "request_date": "2025-09-14",
        "applicant": "Jack",
        "transporter": "Anna",
        "from_location": "판교",
        "to_location": "광주",
        "item": "박스",
        "applicant_amount": 5000,
        "transporter_amount": 10000,
        "accumulate_date": "2025-09-19",
        "deadline_date": "",
        "status": "완료",
        "created_at": "2025-09-14T09:00:00",
        "source": "manual"
    },
    {
        "id": 4,
        "request_date": "2025-09-15",
        "applicant": "Jake",
        "transporter": "James",
        "from_location": "광주",
        "to_location": "판교",
        "item": "ML-U 센서",
        "applicant_amount": 5000,
        "transporter_amount": 10000,
        "accumulate_date": "2025-09-19",
        "deadline_date": "",
        "status": "완료",
        "created_at": "2025-09-15T11:00:00",
        "source": "manual"
    },
    {
        "id": 5,
        "request_date": "2025-09-15",
        "applicant": "Jinie",
        "transporter": "James",
        "from_location": "판교",
        "to_location": "광주",
        "item": "SL-U 보드 세트",
        "applicant_amount": 5000,
        "transporter_amount": 10000,
        "accumulate_date": "2025-09-17",
        "deadline_date": "",
        "status": "완료",
        "created_at": "2025-09-15T15:00:00",
        "source": "manual"
    },
    {
        "id": 6,
        "request_date": "2025-09-16",
        "applicant": "Yup",
        "transporter": "Brown",
        "from_location": "평촌",
        "to_location": "판교",
        "item": "임시노트북",
        "applicant_amount": 5000,
        "transporter_amount": 5000,
        "accumulate_date": "2025-09-17",
        "deadline_date": "",
        "status": "완료",
        "created_at": "2025-09-16T10:00:00",
        "source": "manual"
    },
    {
        "id": 7,
        "request_date": "2025-09-20",
        "applicant": "Jayone",
        "transporter": "",
        "from_location": "판교",
        "to_location": "광주",
        "item": "ML-U 센서",
        "applicant_amount": 5000,
        "transporter_amount": 10000,
        "accumulate_date": "",
        "deadline_date": "",
        "status": "진행중",
        "created_at": "2025-09-20T16:00:00",
        "source": "manual"
    }
]

# JSON 파일로 저장
with open('point_data.json', 'w', encoding='utf-8') as f:
    json.dump(initial_data, f, ensure_ascii=False, indent=2)

print("초기 데이터가 생성되었습니다.")
print(f"총 {len(initial_data)}개의 레코드가 저장되었습니다.")

# 통계 출력
completed = [d for d in initial_data if d['status'] == '완료']
print(f"- 완료: {len(completed)}건")
print(f"- 진행중: {len(initial_data) - len(completed)}건")

# 요청자별 통계
from collections import defaultdict
requester_stats = defaultdict(lambda: {'count': 0, 'points': 0})
transporter_stats = defaultdict(lambda: {'count': 0, 'points': 0})

for record in completed:
    requester = record['applicant']
    transporter = record['transporter']

    requester_stats[requester]['count'] += 1
    requester_stats[requester]['points'] += record['applicant_amount']

    if transporter:
        transporter_stats[transporter]['count'] += 1
        transporter_stats[transporter]['points'] += record['transporter_amount']

print("\n최다 요청자:")
for name, stats in sorted(requester_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:3]:
    print(f"  {name}: {stats['count']}건, {stats['points']:,}P")

print("\n최다 전달자:")
for name, stats in sorted(transporter_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:3]:
    print(f"  {name}: {stats['count']}건, {stats['points']:,}P")