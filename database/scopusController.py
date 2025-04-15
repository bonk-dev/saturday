from database.dbContext import get_db
from fetcher.scopus.models import *

def scopusBatchInsert(data: list[SearchEntry]):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("BEGIN TRANSACTION")

        cursor.execute("INSERT INTO InsertLog (Source) Values (?)", ("Scopus",))
        insert_id = cursor.lastrowid

        for article in data:
            author_ids = insert_authors(article.authors, insert_id, cursor)
            affiliation_ids = insert_affiliations(article.affiliations, insert_id, cursor)


            keyword_ids = insert_keywords(article.authkeywords, insert_id, cursor)
            article_id = insert_article(article, insert_id, cursor)


            bind_authors(author_ids, article_id, cursor)
            bind_affiliations(affiliation_ids, article_id, cursor)
            bind_keywords(keyword_ids, article_id, cursor)
        db.commit()

    except Exception as e:
        db.rollback()
        print(f"Database operation error: {e}")
        raise
    finally:
        cursor.close()


def bind_authors(author_ids: list[int], article_id, cursor):
    for author_id in author_ids:
        cursor.execute("""
            INSERT INTO ArticlexAuthor (ArticleID, AuthorID)
            VALUES (?, ?)
        """, (article_id, author_id))

def bind_keywords(keyword_ids: list[int], article_id, cursor):
    for keyword_id in keyword_ids:
        cursor.execute("""
            INSERT INTO ArticlexKeywords (ArticleID, KeywordsID)
            VALUES (?, ?)
        """, (article_id, keyword_id))

def bind_affiliations(affiliation_ids: list[int], article_id, cursor):
    for affiliation_id in affiliation_ids:
        cursor.execute("""
            INSERT INTO ArticlexAffiliation (ArticleID, AffiliationID)
            VALUES (?, ?)
        """, (article_id, affiliation_id))


def insert_authors(authors: list[Author], insert_id: int, cursor) -> list[int]:
    author_ids = []
    for author in authors:
        cursor.execute(
            "SELECT ID FROM Author WHERE ScopusID = ?",
            (author.authid,)
        )
        result = cursor.fetchone()

        if result:
            author_id = result[0]
        else:
            cursor.execute("""
                INSERT INTO Author (
                    ScopusID, ScopusURL, FullName, 
                    FirstName, SureName, Initials, InsertID
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                author.authid,
                author.author_url,
                author.authname,
                author.surname,
                author.given_name,
                author.initials,
                insert_id
            ))
            author_id = cursor.lastrowid
        author_ids.append(author_id)
    return author_ids

def insert_affiliations(affiliations: list[Affiliation], insert_id: int, cursor) -> list[int]:
    affiliation_ids = []
    for affiliation in affiliations:
        cursor.execute(
            "SELECT ID FROM Affiliation WHERE ScopusID = ?",
            (affiliation.afid,)
        )
        result = cursor.fetchone()

        if result:
            affiliation_id = result[0]
        else:
            cursor.execute("""
                INSERT INTO Affiliation (
                    ScopusID, ScopusURL, Name, 
                    Country, City, InsertID
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                affiliation.afid,
                affiliation.affiliation_url,
                affiliation.affilname,
                affiliation.affiliation_country,
                affiliation.affiliation_city,
                insert_id
            ))
            affiliation_id = cursor.lastrowid
        affiliation_ids.append(affiliation_id)
    return affiliation_ids

def insert_keywords(keywords, insert_id: int, cursor) -> list[int]:
    keyword_ids = []

    for keyword in keywords:
        keyword = keyword.strip()

        cursor.execute(
            "SELECT Id FROM keywords WHERE keyword = ?",
            (keyword,)
        )
        result = cursor.fetchone()

        if result:
            keyword_id = result[0]
        else:
            cursor.execute("""
                INSERT INTO Keywords (
                    Keyword, InsertID
                ) VALUES (?, ?)
            """, (
                keyword,
                insert_id
            ))
            keyword_id = cursor.lastrowid
        keyword_ids.append(keyword_id)
    return keyword_ids
def insert_article(article: SearchEntry, insert_id: int, cursor) -> int:
    cursor.execute("""
                    INSERT INTO Article (
                        ScopusID, ScopusURL, Name, PublishDate,
                        ISSN, EISSN, Volume, Description, Type,
                        SubType, CitedByCount, Sponsor, 
                        InsertID
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
        article.identifier,
        article.url,
        article.title,
        article.cover_date,
        article.issn,
        article.eissn,
        article.volume,
        article.description,
        article.aggregation_type,
        article.subtype_description,
        article.citedby_count,
        article.fundSponsor,
        insert_id
    ))
    article_id = cursor.lastrowid
    return article_id
