def get_book_data(data: dict) -> dict:
    dict_book = {}

    # 1. book
    if 'error' in data['response'].keys():
        print(data['response']['error'])
        return

    book = data["response"]["book"]
    dict_book["isbn13"] = book["isbn13"]
    dict_book["bookname"] = book["bookname"]
    dict_book["authors"] = book["authors"]
    dict_book["publisher"] = book["publisher"]
    dict_book["publication_year"] = book["publication_year"]
    dict_book["class_nm"] = book["class_nm"]
    dict_book["description"] = book["description"]

    # 2. loanGrp
    if data["response"]["loanGrps"] != None:
        if isinstance(data["response"]["loanGrps"]["loanGrp"], list):
            loanGrp = data["response"]["loanGrps"]["loanGrp"][0]
            dict_book["group"] = loanGrp["gender"] + '-' + loanGrp["age"]
        else:
            loanGrp = data["response"]["loanGrps"]["loanGrp"]
            dict_book["group"] = loanGrp["gender"] + '-' + loanGrp["age"]

    # 3. keywords
    if data["response"]["keywords"] != None:
        keywords = data["response"]["keywords"]["keyword"]
        if isinstance(keywords, list):
            list_keywords = [dict_word["word"] for dict_word in keywords]
            dict_book["keywords"] = list_keywords
        else:
            dict_book["keywords"] = keywords["word"]
    else:
        dict_book["keywords"] = None

    # 4. coLoanBooks
    if data["response"]["coLoanBooks"] != None:
        coLoanBooks = data["response"]["coLoanBooks"]["book"]
        if isinstance(coLoanBooks, list):
            list_coLoanBooks = [dict_isbn["isbn13"] for dict_isbn in coLoanBooks]
            dict_book["coLoanBooks"] = list_coLoanBooks
        else:
            dict_book["coLoanBooks"] = coLoanBooks["isbn13"]
    else:
        dict_book["coLoanBooks"] = None


    # 5. maniaRecBooks
    if data["response"]["maniaRecBooks"] != None:
        maniaRecBooks = data["response"]["maniaRecBooks"]["book"]
        if isinstance(maniaRecBooks, list):
            list_maniaRecBooks = [dict_isbn["isbn13"] for dict_isbn in maniaRecBooks]
            dict_book["maniaRecBooks"] = list_maniaRecBooks
        else:
            dict_book["maniaRecBooks"] = maniaRecBooks["isbn13"]
    else:
        dict_book["maniaRecBooks"] = None


    # 6. readerRecBooks
    if data["response"]["readerRecBooks"] != None:
        readerRecBooks = data["response"]["readerRecBooks"]["book"]
        if isinstance(readerRecBooks, list):
            list_readerRecBooks = [dict_isbn["isbn13"] for dict_isbn in readerRecBooks]
            dict_book["readerRecBooks"] = list_readerRecBooks
        else:
            dict_book["readerRecBooks"] = readerRecBooks["isbn13"]
    else:
        dict_book["readerRecBooks"] = None

    return dict_book
