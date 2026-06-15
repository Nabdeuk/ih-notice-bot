def send_telegram_message(message):
    send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        # 응답 결과를 response 변수에 담습니다.
        response = requests.post(send_url, json=payload, timeout=10)
        
        print(f"=== 텔레그램 서버 응답 결과 ===")
        print(f"상태 코드 (Status Code): {response.status_code}")
        print(f"서버 메시지 (Response Text): {response.text}")
        print(f"================================")
        
    except Exception as e:
        print(f"텔레그램 전송 중 완전 실패: {e}")

def main():
    # 조건 다 따지지 않고 실행하자마자 무조건 메시지 발송 시도
    print("텔레그램 전송 테스트를 시작합니다...")
    send_telegram_message("🔔 깃허브 액션에서 보내는 연결 테스트 메시지입니다!")
