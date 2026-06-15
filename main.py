import os
import requests
from bs4 import BeautifulSoup

# 인천도시공사 분양임대 공지사항 URL
TARGET_URL = "https://www.ih.co.kr/main/sale_lease/notice.jsp"

# 깃허브 환경변수(Secrets)에서 토큰과 챗 ID를 가져옵니다.
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
DB_FILE = "last_url.txt"

def get_latest_post():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(TARGET_URL, headers=headers)
    
    if response.status_code != 200:
        print(f"사이트 접속 실패 (상태코드: {response.status_code})")
        return None
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 인천도시공사 목록 테이블 구조 추출
    # tbody 안의 첫 번째 tr(공지글 제외한 최신글 또는 전체 최신글) 선택
    first_row = soup.select_one("tbody tr")
    if not first_row:
        print("게시글 목록을 찾을 수 없습니다.")
        return None
        
    # 제목과 링크가 있는 a 태그 추출
    title_element = first_row.select_one("td.subject a")
    if not title_element:
        # 사이트 구조에 따라 클래스명이 다를 수 있으므로 a 태그를 직접 찾음
        title_element = first_row.select_one("a")
        
    if not title_element:
        print("제목 링크를 찾을 수 없습니다.")
        return None
        
    title = title_element.text.strip()
    link = title_element.get("href", "")
    
    # 상대 경로인 경우 상대 주소를 붙여서 절대 경로로 변경
    if link and not link.startswith("http"):
        link = "https://www.ih.co.kr" + link
        
    return {"title": title, "link": link}

def send_telegram_message(message):
    send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(send_url, json=payload)

def main():
    latest_post = get_latest_post()
    if not latest_post:
        return
        
    current_url = latest_post["link"]
    current_title = latest_post["title"]
    
    # 1. 이전에 확인한 파일이 있는지 체크
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_url = f.read().strip()
    else:
        last_url = ""
        
    # 2. 비교 후 다르면 알림 발송
    if current_url != last_url:
        print(f"새 글 발견! 제목: {current_title}")
        
        # 텔레그램 알림 보내기
        msg = f"📢 [iH 인천도시공사] 새 분양/임대 공고\n\n📌 제목: {current_title}\n🔗 링크: {current_url}"
        send_telegram_message(msg)
        
        # 3. 새로운 링크를 파일에 업데이트
        with open(DB_FILE, "w", encoding="utf-8") as f:
            f.write(current_url)
    else:
        print("새로운 글이 없습니다.")

if __name__ == "__main__":
    main()
