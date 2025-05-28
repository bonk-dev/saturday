from database.dbContext import get_db
from typing import List
from fetcher.gscholar.models import GoogleScholarEntry


def scholarInsertOptimised(data: List[GoogleScholarEntry]) -> int:
    """
    Optimized insert for Google Scholar publications with batch operations.
    """
    db = get_db()
    cursor = db.cursor()

    try:
        insert_count = len(data)

        cursor.execute("INSERT INTO InsertLog (Source, articleInsertCount) VALUES (?, ?)",
                       ("Google Scholar", insert_count))
        insert_id = cursor.lastrowid

        # Pre-load existing entities to minimize database lookups
        existing_authors, existing_affiliations, existing_keywords = preload_existing_scholar_entities(data, cursor)

        # Batch insert new entities
        new_author_ids = batch_insert_scholar_authors(data, existing_authors, insert_id, cursor)
        new_affiliation_ids = batch_insert_scholar_affiliations(data, existing_affiliations, insert_id, cursor)
        new_keyword_ids = batch_insert_scholar_keywords(data, existing_keywords, insert_id, cursor)

        # Combine existing and new IDs
        all_authors = {**existing_authors, **new_author_ids}
        all_affiliations = {**existing_affiliations, **new_affiliation_ids}
        all_keywords = {**existing_keywords, **new_keyword_ids}

        # Batch insert articles and relationships
        batch_insert_scholar_articles_and_relationships(data, all_authors, all_affiliations, all_keywords, insert_id,
                                                        cursor)

        db.commit()
        return insert_count

    except Exception as e:
        db.rollback()
        print(f"Database operation error: {e}")
        raise
    finally:
        cursor.close()


def preload_existing_scholar_entities(data: List[GoogleScholarEntry], cursor):
    """
    Pre-load all existing entities to avoid individual lookups during insertion.
    """
    # Collect all unique names and keywords
    author_names = set()
    affiliation_names = set()
    keywords = set()

    for publication in data:
        # Parse author names
        if publication.authors:
            for author_name in publication.authors.split(','):
                author_name = author_name.strip()
                if author_name:
                    author_names.add(author_name)

        # Extract keywords from abstract or other sources if available
        # For now, keeping empty as per original code
        publication_keywords = extract_keywords(publication)
        for keyword in publication_keywords:
            if keyword.strip():
                keywords.add(keyword.strip())

    # Batch load existing authors by name
    existing_authors = {}
    if author_names:
        placeholders = ','.join(['?' for _ in author_names])
        cursor.execute(f"SELECT ID, FullName FROM Author WHERE FullName IN ({placeholders})",
                       tuple(author_names))
        existing_authors = {name: id for id, name in cursor.fetchall()}

    # Batch load existing affiliations by name
    existing_affiliations = {}
    if affiliation_names:
        placeholders = ','.join(['?' for _ in affiliation_names])
        cursor.execute(f"SELECT ID, Name FROM Affiliation WHERE Name IN ({placeholders})",
                       tuple(affiliation_names))
        existing_affiliations = {name: id for id, name in cursor.fetchall()}

    # Batch load existing keywords
    existing_keywords = {}
    if keywords:
        placeholders = ','.join(['?' for _ in keywords])
        cursor.execute(f"SELECT ID, Keyword FROM Keywords WHERE Keyword IN ({placeholders})",
                       tuple(keywords))
        existing_keywords = {keyword: id for id, keyword in cursor.fetchall()}

    return existing_authors, existing_affiliations, existing_keywords


def extract_keywords(publication: GoogleScholarEntry) -> List[str]:
    """
    Extract keywords from publication data.
    Currently returns empty list as per original implementation.
    """
    keywords = []
    # Placeholder for future keyword extraction logic
    # if publication has abstract or other text fields:
    #     keywords = extract_from_text(publication.abstract)
    return keywords


def batch_insert_scholar_authors(data: List[GoogleScholarEntry], existing_authors: dict, insert_id: int,
                                 cursor) -> dict:
    """
    Batch insert new authors that don't exist in the database.
    """
    new_authors = []
    new_author_ids = {}

    for publication in data:
        if publication.authors:
            author_names = [name.strip() for name in publication.authors.split(',')]
            for author_name in author_names:
                if (author_name and
                        author_name not in existing_authors and
                        author_name not in new_author_ids):
                    # Parse name components
                    name_parts = author_name.split()
                    first_name = name_parts[0] if name_parts else ''
                    surname = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                    initials = ''.join([part[0] + '.' for part in name_parts if part]) if name_parts else ''

                    new_authors.append((
                        None,  # SourceID
                        None,  # SourceURL
                        author_name,  # FullName
                        first_name,  # FirstName
                        surname,  # SureName
                        initials,  # Initials
                        insert_id
                    ))

    if new_authors:
        cursor.executemany("""
            INSERT INTO Author (SourceID, SourceURL, FullName, FirstName, SureName, Initials, InsertID)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, new_authors)

        # Get the IDs of newly inserted authors
        first_id = cursor.lastrowid - len(new_authors) + 1
        for i, (_, _, full_name, *_) in enumerate(new_authors):
            new_author_ids[full_name] = first_id + i

    return new_author_ids


def batch_insert_scholar_affiliations(data: List[GoogleScholarEntry], existing_affiliations: dict, insert_id: int,
                                      cursor) -> dict:
    """
    Batch insert new affiliations that don't exist in the database.
    Currently returns empty dict as affiliations are not extracted from Google Scholar data.
    """
    new_affiliation_ids = {}
    # Google Scholar data typically doesn't include detailed affiliation info
    # This is a placeholder for future enhancement
    return new_affiliation_ids


def batch_insert_scholar_keywords(data: List[GoogleScholarEntry], existing_keywords: dict, insert_id: int,
                                  cursor) -> dict:
    """
    Batch insert new keywords that don't exist in the database.
    """
    new_keywords = []
    new_keyword_ids = {}

    for publication in data:
        keywords = extract_keywords(publication)
        for keyword in keywords:
            keyword = keyword.strip()
            if (keyword and
                    keyword not in existing_keywords and
                    keyword not in new_keyword_ids):
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


def batch_insert_scholar_articles_and_relationships(data: List[GoogleScholarEntry], all_authors: dict,
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

    for publication in data:
        # Extract DOI from pub_url if available
        doi = None
        pub_url = publication.link
        if pub_url and 'doi.org' in pub_url:
            doi = pub_url.split('doi.org/')[-1]

        # Insert article data
        article_data.append((
            'g' + publication.id,
            publication.link,
            publication.title,
            publication.year,
            None,  # ISSN
            None,  # EISSN
            doi,
            None,  # Publisher
            None,  # Volume
            None,  # Description
            publication.entry_type,
            None,  # SubType
            None,  # CitedByCount
            None,  # Sponsor
            insert_id
        ))

    # Batch insert articles
    cursor.executemany("""
        INSERT INTO Article (SourceID, SourceURL, Name, PublishDate, ISSN, EISSN, 
                           DOI, Publisher, Volume, Description, Type, SubType, 
                           CitedByCount, Sponsor, InsertID)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, article_data)

    # Get article IDs (assuming sequential IDs)
    first_article_id = cursor.lastrowid - len(article_data) + 1

    # Prepare relationship data
    for i, publication in enumerate(data):
        article_id = first_article_id + i

        # Author relationships
        if publication.authors:
            author_names = [name.strip() for name in publication.authors.split(',')]
            for author_name in author_names:
                if author_name and author_name in all_authors:
                    author_relationships.append((article_id, all_authors[author_name]))

        # Affiliation relationships (placeholder for future enhancement)
        # Currently Google Scholar data doesn't provide detailed affiliation info

        # Keyword relationships
        keywords = extract_keywords(publication)
        for keyword in keywords:
            keyword = keyword.strip()
            if keyword and keyword in all_keywords:
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
def scholarInsertChunked(data: List[GoogleScholarEntry], chunk_size: int = 1000) -> int:
    """
    Process data in chunks to avoid memory issues with very large datasets.
    """
    total_inserted = 0

    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        total_inserted += scholarInsert(chunk)

    return total_inserted


# Enhanced keyword extraction function (placeholder for future implementation)
def extract_keywords_from_text(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text using simple heuristics.
    This is a placeholder for more sophisticated keyword extraction.
    """
    if not text:
        return []

    # Simple keyword extraction
    words = text.split()
    keywords = [word.strip('.,!?;:()[]{}') for word in words if len(word) > 5]

    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword.lower() not in seen:
            seen.add(keyword.lower())
            unique_keywords.append(keyword)
            if len(unique_keywords) >= max_keywords:
                break

    return unique_keywords