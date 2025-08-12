import requests
import json
import xmltodict
import pandas as pd
from tool import get_book_data
import os
import datetime


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
list_isbn = pd.read_csv("data/data_cut_1.csv")['ISBN'].to_list()

# API 제한
limit_api = 30_000

# 데이터 담을 리스트
list_book_data = []

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
        data = xmltodict.parse(get_response.content)
        dict_book = get_book_data(data)
        list_book_data.append(dict_book)

    except requests.exceptions.RequestException as e:
        print("API 호출 실패:", e)

# 데이터 프레임 저장
df = pd.DataFrame(list_book_data)
df.to_csv(f"output/book_data/{today}-book-crawling.csv", index=False)

# 남은 ISBN 저장
df_remain = pd.DataFrame(list_isbn, columns=["ISBN"])
df_remain.to_csv("data/data_cut_remained.csv", index=False)

print()
print("=============================================")
print(f"{today}의 Crawling 작업이 완료되었습니다.")
print("ISBN 부터 까지의 데이터를 저장했습니다.")
print("Happy Coding! (˶ᵔ ᵕ ᵔ˶)")
print("=============================================")
