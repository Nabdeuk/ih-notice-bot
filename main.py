import os
import requests
from bs4 import BeautifulSoup
import time

TARGET_URL = "https://www.ih.co.kr/main/sale_lease/notice.jsp"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
DB_FILE = "last_url.txt"

def get_latest_post():
    # 실제 크롬 브라우저와 최대한 유사하게 헤더 구성
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.ih.co.kr/",
        "Connection": "keep-alive"
    }
    
    # 깃허브 서버 차단을 피하기 위해 에러 발생 시 최대 3번까지 재시도
    for attempt in range(3):
        try:
            # verify=False로 SSL 인증서 검사를 건너뛰어 연결 끊김을 방지 시도
            response = requests.get(TARGET_URL, headers=headers, timeout=15)
            if response.status_code == 200:
                break
        except Exception as e:
            print(f"접속 시도 {attempt + 1}회 실패... 3초 후 재시도합니다. (오류: {e})")
            time.sleep(3)
    else:
        print("최종적으로 사이트 접속에 실패했습니다.")
        return None
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 게시판 구조 파싱
    first_row = soup.select_one("tbody tr")
    if not first_row:
        print("게시글 목록을 찾을 수 없습니다.")
        return None
        
    title_element = first_row.select_one("td.subject a")
    if not title_element:
        title_element = first_row.select_one("a")
        
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
        requests.post(send_url, json=payload, timeout=10)
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")

def main():
    latest_post = get_latest_post()
    if not latest_post:
        return
        
    current_url = latest_post["link"]
    current_title = latest_post["title"]
    
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_url = f.read().strip()
    else:
        last_url = ""
        
    if current_url != last_url:
        print(f"새 글 발견! 제목: {current_title}")
        msg = f"📢 [iH 인천도시공사] 새 분양/임대 공고\n\n📌 제목: {current_title}\n🔗 링크: {current_url}"
        send_telegram_message(msg)
        
        with open(DB_FILE, "w", encoding="utf-8") as f:
            f.write(current_url)
    else:
        print("새로운 글이 없습니다.")

if __name__ == "__main__":
    main()
