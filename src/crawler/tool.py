def get_book_data(data: dict) -> dict:
    dict_book = {}

    # 1. book
    book = data["response"]["book"]
    dict_book["isbn13"] = book["isbn13"]
    dict_book["bookname"] = book["bookname"]
    dict_book["authors"] = book["authors"]
    dict_book["publisher"] = book["publisher"]
    dict_book["publication_year"] = book["publication_year"]
    dict_book["class_nm"] = book["class_nm"]
    dict_book["description"] = book["description"]

    # 2. loanGrp
    loanGrp = data["response"]["loanGrps"]["loanGrp"][0]
    dict_book["group"] = loanGrp["gender"] + '-' + loanGrp["age"]

    # 3. keywords
    keywords = data["response"]["keywords"]["keyword"]
    list_keywords = [dict_word["word"] for dict_word in keywords]
    dict_book["keywords"] = list_keywords

    # 4. coLoanBooks
    coLoanBooks = data["response"]["coLoanBooks"]["book"]
    list_coLoanBooks = [dict_isbn["isbn13"] for dict_isbn in coLoanBooks]
    dict_book["coLoanBooks"] = list_coLoanBooks

    # 5. maniaRecBooks
    maniaRecBooks = data["response"]["maniaRecBooks"]["book"]
    list_maniaRecBooks = [dict_isbn["isbn13"] for dict_isbn in maniaRecBooks]
    dict_book["maniaRecBooks"] = list_maniaRecBooks

    # 6. readerRecBooks
    readerRecBooks = data["response"]["readerRecBooks"]["book"]
    list_readerRecBooks = [dict_isbn["isbn13"] for dict_isbn in readerRecBooks]
    dict_book["readerRecBooks"] = list_readerRecBooks

    return dict_book