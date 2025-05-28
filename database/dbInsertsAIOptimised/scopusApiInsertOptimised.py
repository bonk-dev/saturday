from database.dbContext import get_db
from fetcher.scopus.models import *


def scopusAPIInsertOptimised(data: list[SearchEntry]) -> int:
    """
    Optimized version with batch operations and reduced database roundtrips.
    """
    db = get_db()
    cursor = db.cursor()

    try:
        insert_count = len(data)

        cursor.execute("INSERT INTO InsertLog (Source, articleInsertCount) VALUES (?, ?)", ("Scopus", insert_count))
        insert_id = cursor.lastrowid

        # Pre-load existing entities to minimize database lookups
        existing_authors, existing_affiliations, existing_keywords = preload_existing_entities(data, cursor)

        # Batch insert new entities
        new_author_ids = batch_insert_authors(data, existing_authors, insert_id, cursor)
        new_affiliation_ids = batch_insert_affiliations(data, existing_affiliations, insert_id, cursor)
        new_keyword_ids = batch_insert_keywords(data, existing_keywords, insert_id, cursor)

        # Combine existing and new IDs
        all_authors = {**existing_authors, **new_author_ids}
        all_affiliations = {**existing_affiliations, **new_affiliation_ids}
        all_keywords = {**existing_keywords, **new_keyword_ids}

        # Batch insert articles and relationships
        batch_insert_articles_and_relationships(data, all_authors, all_affiliations, all_keywords, insert_id, cursor)

        db.commit()
        return insert_count
    except Exception as e:
        db.rollback()
        print(f"Database operation error: {e}")
        raise
    finally:
        cursor.close()


def preload_existing_entities(data: list[SearchEntry], cursor):
    """
    Pre-load all existing entities to avoid individual lookups during insertion.
    """
    # Collect all unique IDs
    author_source_ids = set()
    affiliation_source_ids = set()
    keywords = set()

    for article in data:
        for author in article.authors:
            author_source_ids.add("s" + author.authid)
        for affiliation in article.affiliations:
            affiliation_source_ids.add("s" + affiliation.afid)
        for keyword in article.authkeywords:
            keywords.add(keyword.strip())

    # Batch load existing authors
    existing_authors = {}
    if author_source_ids:
        placeholders = ','.join(['?' for _ in author_source_ids])
        cursor.execute(f"SELECT ID, SourceID FROM Author WHERE SourceID IN ({placeholders})",
                       tuple(author_source_ids))
        existing_authors = {source_id: id for id, source_id in cursor.fetchall()}

    # Batch load existing affiliations
    existing_affiliations = {}
    if affiliation_source_ids:
        placeholders = ','.join(['?' for _ in affiliation_source_ids])
        cursor.execute(f"SELECT ID, SourceID FROM Affiliation WHERE SourceID IN ({placeholders})",
                       tuple(affiliation_source_ids))
        existing_affiliations = {source_id: id for id, source_id in cursor.fetchall()}

    # Batch load existing keywords
    existing_keywords = {}
    if keywords:
        placeholders = ','.join(['?' for _ in keywords])
        cursor.execute(f"SELECT Id, Keyword FROM Keywords WHERE Keyword IN ({placeholders})",
                       tuple(keywords))
        existing_keywords = {keyword: id for id, keyword in cursor.fetchall()}

    return existing_authors, existing_affiliations, existing_keywords


def batch_insert_authors(data: list[SearchEntry], existing_authors: dict, insert_id: int, cursor) -> dict:
    """
    Batch insert new authors that don't exist in the database.
    """
    new_authors = []
    new_author_ids = {}

    for article in data:
        for author in article.authors:
            source_id = "s" + author.authid
            if source_id not in existing_authors and source_id not in new_author_ids:
                new_authors.append((
                    source_id,
                    author.author_url,
                    author.authname,
                    author.surname,
                    author.given_name,
                    author.initials,
                    insert_id
                ))

    if new_authors:
        cursor.executemany("""
            INSERT INTO Author (SourceID, SourceURL, FullName, FirstName, SureName, Initials, InsertID)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, new_authors)

        # Get the IDs of newly inserted authors
        first_id = cursor.lastrowid - len(new_authors) + 1
        for i, (source_id, *_) in enumerate(new_authors):
            new_author_ids[source_id] = first_id + i

    return new_author_ids


def batch_insert_affiliations(data: list[SearchEntry], existing_affiliations: dict, insert_id: int, cursor) -> dict:
    """
    Batch insert new affiliations that don't exist in the database.
    """
    new_affiliations = []
    new_affiliation_ids = {}

    for article in data:
        for affiliation in article.affiliations:
            source_id = "s" + affiliation.afid
            if source_id not in existing_affiliations and source_id not in new_affiliation_ids:
                new_affiliations.append((
                    source_id,
                    affiliation.affiliation_url,
                    affiliation.affilname,
                    affiliation.affiliation_country,
                    affiliation.affiliation_city,
                    insert_id
                ))

    if new_affiliations:
        cursor.executemany("""
            INSERT INTO Affiliation (SourceID, SourceURL, Name, Country, City, InsertID)
            VALUES (?, ?, ?, ?, ?, ?)
        """, new_affiliations)

        # Get the IDs of newly inserted affiliations
        first_id = cursor.lastrowid - len(new_affiliations) + 1
        for i, (source_id, *_) in enumerate(new_affiliations):
            new_affiliation_ids[source_id] = first_id + i

    return new_affiliation_ids


def batch_insert_keywords(data: list[SearchEntry], existing_keywords: dict, insert_id: int, cursor) -> dict:
    """
    Batch insert new keywords that don't exist in the database.
    """
    new_keywords = []
    new_keyword_ids = {}

    for article in data:
        for keyword in article.authkeywords:
            keyword = keyword.strip()
            if keyword not in existing_keywords and keyword not in new_keyword_ids:
                new_keywords.append((keyword, insert_id))

    if new_keywords:
        cursor.executemany("""
            INSERT INTO Keywords (Keyword, InsertID)
            VALUES (?, ?)
        """, new_keywords)

        # Get the IDs of newly inserted keywords
        first_id = cursor.lastrowid - len(new_keywords) + 1
        for i, (keyword, _) in enumerate(new_keywords):
            new_keyword_ids[keyword] = first_id + i

    return new_keyword_ids


def batch_insert_articles_and_relationships(data: list[SearchEntry], all_authors: dict,
                                            all_affiliations: dict, all_keywords: dict,
                                            insert_id: int, cursor):
    """
    Batch insert articles and all their relationships.
    """
    # Prepare article data
    article_data = []
    author_relationships = []
    affiliation_relationships = []
    keyword_relationships = []

    for article in data:
        # Insert article data
        article_data.append((
            's' + article.identifier,
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

    # Batch insert articles
    cursor.executemany("""
        INSERT INTO Article (SourceID, SourceURL, Name, PublishDate, ISSN, EISSN, 
                           Volume, Description, Type, SubType, CitedByCount, Sponsor, InsertID)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, article_data)

    # Get article IDs (assuming sequential IDs)
    first_article_id = cursor.lastrowid - len(article_data) + 1

    # Prepare relationship data
    for i, article in enumerate(data):
        article_id = first_article_id + i

        # Author relationships
        for author in article.authors:
            source_id = "s" + author.authid
            if source_id in all_authors:
                author_relationships.append((article_id, all_authors[source_id]))

        # Affiliation relationships
        for affiliation in article.affiliations:
            source_id = "s" + affiliation.afid
            if source_id in all_affiliations:
                affiliation_relationships.append((article_id, all_affiliations[source_id]))

        # Keyword relationships
        for keyword in article.authkeywords:
            keyword = keyword.strip()
            if keyword in all_keywords:
                keyword_relationships.append((article_id, all_keywords[keyword]))

    # Batch insert relationships
    if author_relationships:
        cursor.executemany("INSERT INTO ArticlexAuthor (ArticleID, AuthorID) VALUES (?, ?)",
                           author_relationships)

    if affiliation_relationships:
        cursor.executemany("INSERT INTO ArticlexAffiliation (ArticleID, AffiliationID) VALUES (?, ?)",
                           affiliation_relationships)

    if keyword_relationships:
        cursor.executemany("INSERT INTO ArticlexKeywords (ArticleID, KeywordsID) VALUES (?, ?)",
                           keyword_relationships)


# Alternative version using chunking for very large datasets
def scopusAPIInsertChunked(data: list[SearchEntry], chunk_size: int = 1000) -> int:
    """
    Process data in chunks to avoid memory issues with very large datasets.
    """
    total_inserted = 0

    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        total_inserted += scopusAPIInsert(chunk)

    return total_inserted