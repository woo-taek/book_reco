import requests
import json
import xmltodict
import pandas as pd
from src.crawler.tool import get_book_data
import os
import datetime
import time
from configparser import ConfigParser


# 사용자 명시
config_parser = ConfigParser()
config_parser.read("config/config.ini")
user = config_parser["user"]["active_user"]
num = config_parser["user"]["number_cut"]

# 오늘 날짜
today = datetime.date.today()

# 책 데이터 저장 폴더
os.makedirs("output/book_data", exist_ok=True)

# API URL
url = "http://data4library.kr/api/usageAnalysisList"

# API Key 가져오기
with open("config/book_api.json", "r") as f:
    api_key = json.load(f)["api_key"]

# ISBN 13 가져오기
list_isbn = pd.read_csv(f"data/data_cut_{num}.csv")['ISBN'].to_list()

# API 제한
limit_api = 30_000

# 데이터 담을 리스트
list_book_data = []

# 시작번호, 끝번호
start_isbn = list_isbn[0]
end_isbn = list_isbn[29_999]

# 작업 시작 멘트
print()
print("=============================================")
time.sleep(1)
print(f"{today}의 Crawling 작업을 시작합니다.")
time.sleep(0.75)
print(f"ISBN {start_isbn}부터 {end_isbn}까지 수집합니다.")
time.sleep(1)
print(f"{user} 군, 오늘도 힘내봐요!")
time.sleep(0.75)
print("Let's Get It! *⸜( •ᴗ• )⸝*")
time.sleep(1)
print("=============================================")
print()
time.sleep(0.5)

while limit_api > 0:
    try:
        # ISBN
        isbn13 = list_isbn.pop(0)
        # Parameter
        params = {
            "authKey": api_key,
            "isbn13": isbn13,
            # "format": "xml"
        }
        print(f"try: {isbn13}, limit: {limit_api}")

        limit_api -= 1
        get_response = requests.get(url, params=params)
        get_response.raise_for_status()     # HTTP 상태 코드(200, 404, 500 등) 확인

        dict_book = {}
        if get_response.content.strip():
            data = xmltodict.parse(get_response.content)
            dict_book = get_book_data(data)
        else:
            print(f"{isbn13}에 대한 응답이 비어있습니다.")    

        if dict_book:
            list_book_data.append(dict_book)
        time.sleep(0.5)

    except requests.exceptions.RequestException as e:
        print("API 호출 실패:", e)

# 데이터 프레임 저장
df = pd.DataFrame(list_book_data)
df.to_csv(f"output/book_data/{today}-{user}-crawling.csv", index=False)

# 남은 ISBN 저장
df_remain = pd.DataFrame(list_isbn, columns=["ISBN"])
# df_remain.to_csv("data/data_cut_remained.csv", index=False)
df_remain.to_csv(f"data/data_cut_{num}.csv", index=False)

print()
print("=============================================")
print(f"{today}의 Crawling 작업이 완료되었습니다.")
print(f"{user} 군, 수고했어요!")
print("Happy Coding! (˶ᵔ ᵕ ᵔ˶)")
print("=============================================")
