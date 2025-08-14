import requests
import json
import xmltodict
import pandas as pd
from src.crawler.tool import get_book_data
import os
import datetime
import time
import threading
import asyncio
import aiohttp
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
with open("config/sample_api_key.json", "r") as f:
    api_key = json.load(f)["api_key"]

# ISBN 13 가져오기
list_isbn = pd.read_csv(f"data/data_cut_{num}.csv")['ISBN'].to_list()

# 이미 처리된 ISBN 확인 및 필터링
def get_processed_isbns():
    """book_data 폴더에서 이미 처리된 ISBN들을 가져옵니다."""
    processed_isbns = set()
    book_data_dir = "output/book_data"
    
    if os.path.exists(book_data_dir):
        csv_files = [f for f in os.listdir(book_data_dir) if f.endswith('.csv')]
        print(f"발견된 CSV 파일: {csv_files}")
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(os.path.join(book_data_dir, csv_file))
                print(f"{csv_file}: {len(df)}행, 컬럼: {df.columns.tolist()}")
                
                if 'isbn13' in df.columns:
                    isbn_count = len(df['isbn13'].dropna())
                    processed_isbns.update(df['isbn13'].dropna().astype(str).tolist())
                    print(f"  → {csv_file}에서 {isbn_count}개 ISBN 추가")
                else:
                    print(f"  → {csv_file}에 isbn13 컬럼이 없습니다")
                    
            except Exception as e:
                print(f"CSV 파일 읽기 실패 ({csv_file}): {e}")
    
    return processed_isbns

# 이미 처리된 ISBN 제외
processed_isbns = get_processed_isbns()
print(f"기존 CSV에서 발견된 처리된 ISBN 개수: {len(processed_isbns)}")

original_count = len(list_isbn)
list_isbn = [isbn for isbn in list_isbn if str(isbn) not in processed_isbns]
filtered_count = len(list_isbn)

print(f"전체 ISBN: {original_count}개")
print(f"이미 처리된 ISBN: {original_count - filtered_count}개")
print(f"처리할 ISBN: {filtered_count}개")

# 디버깅: 처리된 ISBN과 남은 ISBN 샘플 확인
if processed_isbns:
    sample_processed = list(processed_isbns)[:5]
    print(f"처리된 ISBN 샘플: {sample_processed}")

if list_isbn:
    sample_remaining = list_isbn[:5]
    print(f"처리할 ISBN 샘플: {sample_remaining}")

if not list_isbn:
    print("처리할 ISBN이 없습니다!")
    exit()

# API 제한 (남은 ISBN 수와 20,000 중 작은 값 사용)
limit_api = min(20_000, len(list_isbn))

# 데이터 담을 리스트
list_book_data = []

# save 플래그
save_flag = False

def save_data():
    """현재까지 수집한 데이터를 저장하는 함수"""
    global list_book_data, save_flag, today, user
    
    if list_book_data:
        df_new = pd.DataFrame(list_book_data)
        output_file = f"output/book_data/{today}-{user}-crawling.csv"
        
        # 기존 파일이 있는지 확인
        if os.path.exists(output_file):
            try:
                # 기존 파일 읽기
                df_existing = pd.read_csv(output_file)
                
                # 중복 제거 (isbn13 기준)
                if 'isbn13' in df_existing.columns and 'isbn13' in df_new.columns:
                    # 기존 데이터에 없는 새로운 데이터만 추가
                    df_new = df_new[~df_new['isbn13'].isin(df_existing['isbn13'])]
                    
                # 기존 데이터와 새 데이터 결합
                if not df_new.empty:
                    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                    df_combined.to_csv(output_file, index=False)
                    print(f"기존 파일에 {len(df_new)}개의 새로운 데이터가 추가되었습니다.")
                else:
                    print("추가할 새로운 데이터가 없습니다 (모두 중복).")
                    
            except Exception as e:
                print(f"기존 파일 처리 중 오류 발생: {e}")
                # 오류 발생 시 새 파일로 저장
                df_new.to_csv(output_file, index=False)
        else:
            # 새 파일 생성
            df_new.to_csv(output_file, index=False)
            print(f"새 파일이 생성되었습니다: {len(df_new)}개 데이터 저장")
    else:
        print("저장할 데이터가 없습니다.")

def check_user_input():
    """사용자 입력을 체크하는 함수"""
    global save_flag
    while not save_flag:
        user_input = input().strip().lower()
        if user_input == "save":
            print("\n'save' 명령을 받았습니다. 데이터를 저장하고 종료합니다...")
            save_flag = True
            break

async def fetch_book_data(session, isbn13, semaphore):
    """비동기로 단일 책 데이터를 가져오는 함수"""
    async with semaphore:  # 동시 요청 수 제한
        params = {
            "authKey": api_key,
            "isbn13": isbn13,
        }
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    content = await response.text()
                    if content.strip():
                        data = xmltodict.parse(content)
                        dict_book = get_book_data(data)
                        if dict_book:
                            print(f"성공: {isbn13}")
                            return dict_book
                        else:
                            print(f"데이터 없음: {isbn13}")
                    else:
                        print(f"응답 비어있음: {isbn13}")
                else:
                    print(f"HTTP 오류 {response.status}: {isbn13}")
        except Exception as e:
            print(f"오류 {isbn13}: {e}")
        
        return None

async def process_batch(isbn_batch, batch_num, total_batches):
    """ISBN 배치를 비동기로 처리하는 함수"""
    global save_flag, list_book_data
    
    print(f"배치 {batch_num}/{total_batches} 시작 ({len(isbn_batch)}개 ISBN)")
    
    # 동시 요청 수 제한 (API 서버 부하 방지)
    semaphore = asyncio.Semaphore(10)  # 최대 10개 동시 요청
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for isbn in isbn_batch:
            if save_flag:
                break
            task = fetch_book_data(session, isbn, semaphore)
            tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 성공한 결과만 추가
            for result in results:
                if result and not isinstance(result, Exception):
                    list_book_data.append(result)
    
    print(f"배치 {batch_num}/{total_batches} 완료")

# 시작번호, 끝번호
start_isbn = list_isbn[0]
end_isbn = list_isbn[min(limit_api - 1, len(list_isbn) - 1)]

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
time.sleep(0.75)
print("※ 중간에 'save'를 입력하면 현재까지 데이터를 저장하고 종료합니다.")
time.sleep(1)
print("=============================================")
print()
time.sleep(0.5)

# 사용자 입력 체크 스레드 시작
input_thread = threading.Thread(target=check_user_input, daemon=True)
input_thread.start()

# 비동기 배치 처리
async def main_crawling():
    """메인 크롤링 함수"""
    global save_flag, list_isbn, limit_api
    
    # 배치 크기 설정 (한 번에 처리할 ISBN 수)
    batch_size = 50
    processed_count = 0
    
    # ISBN을 배치로 나누기
    batches = []
    for i in range(0, min(limit_api, len(list_isbn)), batch_size):
        batch = list_isbn[i:i+batch_size]
        batches.append(batch)
    
    total_batches = len(batches)
    
    for batch_num, batch in enumerate(batches, 1):
        if save_flag:
            print("사용자 요청에 의해 작업을 중단합니다.")
            break
            
        await process_batch(batch, batch_num, total_batches)
        processed_count += len(batch)
        
        # 배치 간 잠깐 대기 (API 서버 부하 방지)
        await asyncio.sleep(0.5)
        
        # 진행 상황 출력
        print(f"진행률: {processed_count}/{min(limit_api, len(list_isbn))}")
    
    # 처리된 ISBN들을 원본 리스트에서 제거
    list_isbn = list_isbn[processed_count:]

# 비동기 크롤링 실행
try:
    asyncio.run(main_crawling())
except KeyboardInterrupt:
    print("\nKeyboard Interrupt - 작업을 중단합니다.")
    save_flag = True

# 데이터 저장 (함수 호출)
save_data()

# 남은 ISBN 저장
df_remain = pd.DataFrame(list_isbn, columns=["ISBN"])
# df_remain.to_csv("data/data_cut_remained.csv", index=False)
df_remain.to_csv(f"data/data_cut_{num}.csv", index=False)

print()
print("=============================================")
if save_flag:
    print(f"사용자 요청으로 {today}의 Crawling 작업이 중단되었습니다.")
else:
    print(f"{today}의 Crawling 작업이 완료되었습니다.")
print(f"{user} 군, 수고했어요!")
print("Happy Coding! (˶ᵔ ᵕ ᵔ˶)")
print("=============================================")
