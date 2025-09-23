import requests
import json

# 잔디 웹훅 URL
JANDI_WEBHOOK_URL = 'https://wh.jandi.com/connect-api/webhook/14611962/0c004aecab37f46a168402c71d4cbaa7'

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

        response = requests.post(JANDI_WEBHOOK_URL, json=data, timeout=10)

        if response.status_code == 200:
            print(f"잔디 알림 전송 성공: {title}")
            return True
        else:
            print(f"잔디 알림 전송 실패: {response.status_code}")
            return False

    except Exception as e:
        print(f"잔디 알림 전송 중 오류: {str(e)}")
        return False

def notify_transport_request(requester, from_loc, to_loc, item):
    """운송 요청 알림"""
    message = f"📦 새로운 운송 요청\n요청자: {requester}\n경로: {from_loc} → {to_loc}\n물품: {item}\n\n전달해주실 분을 기다립니다!"
    return send_jandi_notification("물품 운송 요청", message, "#ffa502")

def notify_transport_completed(requester, transporter, from_loc, to_loc, item, req_points, trans_points):
    """운송 완료 알림"""
    message = f"✅ 운송 완료!\n요청자: {requester} (+{req_points:,}P)\n전달자: {transporter} (+{trans_points:,}P)\n경로: {from_loc} → {to_loc}\n물품: {item}\n\n감사합니다!"
    return send_jandi_notification("물품 운송 완료", message, "#27ae60")

def notify_point_adjustment(employee, adjustment, reason, new_total):
    """포인트 조정 알림"""
    emoji = "📈" if adjustment > 0 else "📉"
    action = "지급" if adjustment > 0 else "차감"
    message = f"{emoji} 포인트 {action}\n대상자: {employee}\n{action} 포인트: {adjustment:+,}P\n현재 총 포인트: {new_total:,}P\n사유: {reason}"
    color = "#27ae60" if adjustment > 0 else "#e74c3c"
    return send_jandi_notification("포인트 조정", message, color)

# 테스트 함수
def test_jandi_webhook():
    """웹훅 테스트"""
    return send_jandi_notification("🔔 테스트 알림", "물품 운송 시스템이 정상 작동 중입니다!", "#3498db")

if __name__ == "__main__":
    # 테스트 실행
    print("잔디 웹훅 테스트 중...")
    result = test_jandi_webhook()
    if result:
        print("✅ 잔디 알림 테스트 성공!")
    else:
        print("❌ 잔디 알림 테스트 실패!")