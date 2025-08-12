import pandas as pd


# 서울도서관 장서 대출목록 (2025년 07월) 파일을 seoul_library_202507로 이름 변경
df = pd.read_csv(
    "data/seoul_library_202507.csv", 
    encoding="cp949",
    dtype={"ISBN": str}
)

# 조건
condition = (df['대출건수'] > 3) | (df['발행년도'] == '2025')
rows = df[condition].shape[0]
cut = rows // 3

# ISBN만 추출
df[condition].iloc[:cut, 5].to_csv("data/data_cut_1.csv", index=False)
print(f"{df[condition].iloc[:cut, 5].shape[0]} 행 데이터 추출 완료")

df[condition].iloc[cut:cut*2, 5].to_csv("data/data_cut_2.csv", index=False)
print(f"{df[condition].iloc[cut:cut*2, 5].shape[0]} 행 데이터 추출 완료")

df[condition].iloc[cut*2:, 5].to_csv("data/data_cut_3.csv", index=False)
print(f"{df[condition].iloc[cut*2:, 5].shape[0]} 행 데이터 추출 완료")
