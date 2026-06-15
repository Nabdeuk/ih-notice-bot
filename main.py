import os
import requests
from bs4 import BeautifulSoup
import time

TARGET_URL = "https://www.ih.co.kr/main/sale_lease/notice.jsp"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
DB_FILE = "last_url.txt"

def get_latest_post():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.ih.co.kr/",
        "Connection": "keep-alive"
    }
    
    for attempt in range(3):
        try:
            response = requests.get(TARGET_URL, headers=headers, timeout=15)
            if response.status_code == 200:
                break
        except Exception as e:
            print(f"접속 시도 {attempt + 1}회 실패... (오류: {e})")
            time.sleep(3)
    else:
        print("최종적으로 사이트 접속에 실패했습니다.")
        return None
        
    soup = BeautifulSoup(response.text, 'html.parser')
    first_row = soup.select_one("tbody tr")
    if not first_row:
        print("게시글 목록을 찾을 수 없습니다.")
        return None
        
    title_element = first_row.select_one("td.subject a") or first_row.select_one("a")
    if not title_element:
        print("제목 링크를 찾을 수 없습니다.")
        return None
        
    title = title_element.text.strip()
    link = title_element.get("href", "")
    if link and not link.startswith("http"):
        link = "https://www.ih.co.kr" + link
        
    return {"title": title, "link": link}

def send_telegram_message(message):
    send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(send_url, json=payload, timeout=10)
        print(f"=== 텔레그램 서버 응답 결과 ===")
        print(f"상태 코드 (Status Code): {response.status_code}")
        print(f"서버 메시지 (Response Text): {response.text}")
        print(f"================================")
    except Exception as e:
        print(f"텔레그램 전송 중 완전 실패: {e}")

def main():
    print("프로그램을 시작합니다.")
    latest_post = get_latest_post()
    if not latest_post:
        print("공지사항을 가져오지 못해 종료합니다.")
        return
        
    current_url = latest_post["link"]
    current_title = latest_post["title"]
    
    # 디버깅용 로그 출력
    print(f"가져온 최신글: {current_title}")
    
    # 테스트를 위해 무조건 메시지 전송 로직 실행
    print("텔레그램 전송 테스트를 시작합니다...")
    msg = f"📢 [iH 인천도시공사] 연결 테스트\n\n📌 최신글 제목: {current_title}\n🔗 링크: {current_url}"
    send_telegram_message(msg)
    
    # 파일 기록은 정상적으로 수행
    with open(DB_FILE, "w", encoding="utf-8") as f:
        f.write(current_url)

if __name__ == "__main__":
    main()
