def main():
    latest_post = get_latest_post()
    if not latest_post:
        return
        
    current_url = latest_post["link"]
    current_title = latest_post["title"]
    
    # 묻지도 따지지도 않고 무조건 테스트 메시지 전송!
    print("테스트 메시지를 전송합니다.")
    msg = f"📢 [테스트] 연결 확인용\n제목: {current_title}"
    send_telegram_message(msg)
