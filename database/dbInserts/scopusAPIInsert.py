from database.dbContext import get_db
from fetcher.scopus.models import *


def scopusAPIInsert(data: list[SearchEntry]) -> int:
    """
    Insert Scopus API search results into database with complete relational mapping.
    Performs transactional insertion of articles with their associated authors, affiliations,
    and keywords. Creates many-to-many relationships between entities and logs the operation.
    Uses database rollback on errors to maintain data integrity.

    :param list[SearchEntry] data: List of SearchEntry objects containing article data from Scopus API.
    :return: Number of articles successfully inserted into database.
    :rtype: int
    """
    db = get_db()
    cursor = db.cursor()

    try:
        insert_count = len(data)

        cursor.execute("INSERT INTO InsertLog (Source, articleInsertCount) VALUES (?, ?)", ("Scopus", insert_count))
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

        return insert_count
    except Exception as e:
        db.rollback()
        print(f"Database operation error: {e}")
        raise
    finally:
        cursor.close()


def bind_authors(author_ids: list[int], article_id: int, cursor) -> None:
    """
    Create many-to-many relationships between articles and authors in junction table.
    Inserts records into ArticlexAuthor table to establish associations between
    articles and their contributing authors using their respective database IDs.

    :param list[int] author_ids: List of author database IDs to associate with article.
    :param int article_id: Database ID of the article to bind authors to.
    :param cursor: Database cursor for executing SQL statements.
    :return: None
    :rtype: None
    """
    for author_id in author_ids:
        cursor.execute("""
            INSERT INTO ArticlexAuthor (ArticleID, AuthorID)
            VALUES (?, ?)
        """, (article_id, author_id))


def bind_keywords(keyword_ids: list[int], article_id: int, cursor) -> None:
    """
    Create many-to-many relationships between articles and keywords in junction table.
    Inserts records into ArticlexKeywords table to establish associations between
    articles and their associated keywords using their respective database IDs.

    :param list[int] keyword_ids: List of keyword database IDs to associate with article.
    :param int article_id: Database ID of the article to bind keywords to.
    :param cursor: Database cursor for executing SQL statements.
    :return: None
    :rtype: None
    """
    for keyword_id in keyword_ids:
        cursor.execute("""
            INSERT INTO ArticlexKeywords (ArticleID, KeywordsID)
            VALUES (?, ?)
        """, (article_id, keyword_id))


def bind_affiliations(affiliation_ids: list[int], article_id: int, cursor) -> None:
    """
    Create many-to-many relationships between articles and affiliations in junction table.
    Inserts records into ArticlexAffiliation table to establish associations between
    articles and their institutional affiliations using their respective database IDs.

    :param list[int] affiliation_ids: List of affiliation database IDs to associate with article.
    :param int article_id: Database ID of the article to bind affiliations to.
    :param cursor: Database cursor for executing SQL statements.
    :return: None
    :rtype: None
    """
    for affiliation_id in affiliation_ids:
        cursor.execute("""
            INSERT INTO ArticlexAffiliation (ArticleID, AffiliationID)
            VALUES (?, ?)
        """, (article_id, affiliation_id))


def insert_authors(authors: list[Author], insert_id: int, cursor) -> list[int]:
    """
    Insert or retrieve author records from database using upsert pattern based on Scopus ID.
    Checks for existing authors by SourceID to avoid duplicates, creates new records if needed.
    Stores comprehensive author information including names, identifiers, and URLs.

    :param list[Author] authors: List of Author objects containing author data from Scopus.
    :param int insert_id: Insert log ID for tracking this batch operation.
    :param cursor: Database cursor for executing SQL statements.
    :return: List of database IDs for processed authors.
    :rtype: list[int]
    """
    author_ids = []
    for author in authors:
        cursor.execute(
            "SELECT ID FROM Author WHERE SourceID = ?",
            ("s" + author.authid,)
        )
        result = cursor.fetchone()

        if result:
            author_id = result[0]
        else:
            cursor.execute("""
                INSERT INTO Author (
                    SourceID, SourceURL, FullName, 
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
    """
    Insert or retrieve affiliation records from database using upsert pattern based on Scopus ID.
    Checks for existing affiliations by SourceID to avoid duplicates, creates new records if needed.
    Stores institutional information including names, geographic location, and identifiers.

    :param list[Affiliation] affiliations: List of Affiliation objects containing institutional data from Scopus.
    :param int insert_id: Insert log ID for tracking this batch operation.
    :param cursor: Database cursor for executing SQL statements.
    :return: List of database IDs for processed affiliations.
    :rtype: list[int]
    """
    affiliation_ids = []
    for affiliation in affiliations:
        cursor.execute(
            "SELECT ID FROM Affiliation WHERE SourceID = ?",
            ('s'+affiliation.afid,)
        )
        result = cursor.fetchone()

        if result:
            affiliation_id = result[0]
        else:
            cursor.execute("""
                INSERT INTO Affiliation (
                    SourceID, SourceURL, Name, 
                    Country, City, InsertID
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                's'+affiliation.afid,
                affiliation.affiliation_url,
                affiliation.affilname,
                affiliation.affiliation_country,
                affiliation.affiliation_city,
                insert_id
            ))
            affiliation_id = cursor.lastrowid
        affiliation_ids.append(affiliation_id)
    return affiliation_ids


def insert_keywords(keywords: list[str], insert_id: int, cursor) -> list[int]:
    """
    Insert or retrieve keyword records from database using upsert pattern based on keyword text.
    Normalizes keywords by stripping whitespace, checks for existing keywords to avoid duplicates.
    Creates new keyword records if not found, maintaining referential integrity.

    :param list[str] keywords: List of keyword strings from article metadata.
    :param int insert_id: Insert log ID for tracking this batch operation.
    :param cursor: Database cursor for executing SQL statements.
    :return: List of database IDs for processed keywords.
    :rtype: list[int]
    """
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
    """
    Insert article record into database with comprehensive publication metadata.
    Stores complete article information including identifiers, bibliographic data,
    publication details, citation metrics, and funding information from Scopus API.

    :param SearchEntry article: SearchEntry object containing complete article data from Scopus.
    :param int insert_id: Insert log ID for tracking this batch operation.
    :param cursor: Database cursor for executing SQL statements.
    :return: Database ID of the newly inserted article record.
    :rtype: int
    """
    cursor.execute("""
                    INSERT INTO Article (
                        SourceID, SourceURL, Name, PublishDate,
                        ISSN, EISSN, Volume, Description, Type,
                        SubType, CitedByCount, Sponsor, 
                        InsertID
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
        's'+article.identifier,
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