import os

import re

import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]

CHAT_ID = os.environ["CHAT_ID"]

URL = "https://www.ih.co.kr/main/sale_lease/notice.jsp"

STATE_FILE = "last_post.txt"

def send_telegram(text):

    requests.post(

        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",

        data={

            "chat_id": CHAT_ID,

            "text": text

        },

        timeout=30

    )

def get_latest_post():

    html = requests.get(URL, timeout=30).text

    matches = re.findall(r"msg_seq=(\d+)", html)

    if not matches:

        raise Exception("게시글 번호를 찾지 못했습니다.")

    latest_seq = max(matches, key=int)

    detail_url = (

        "https://www.ih.co.kr/main/bbs/bbsMsgDetail.do"

        f"?bcd=notice&msg_seq={latest_seq}"

    )

    return latest_seq, f"새 공고 ({latest_seq})", detail_url

def main():

    latest_seq, title, link = get_latest_post()

    if not os.path.exists(STATE_FILE):

        with open(STATE_FILE, "w") as f:

            f.write(latest_seq)

        print("최초 실행 - 기준값 저장")

        return

    with open(STATE_FILE, "r") as f:

        saved_seq = f.read().strip()

    if latest_seq != saved_seq:

        message = (

            f"🔔 인천도시공사 새 공고\n\n"

            f"{title}\n\n"

            f"{link}"

        )

        send_telegram(message)

        with open(STATE_FILE, "w") as f:

            f.write(latest_seq)

        print("새 글 발견")

    else:

        print("변경 없음")

if __name__ == "__main__":

    main()
