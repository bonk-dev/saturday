from database.dbContext import get_db
from typing import List


# Import your scholar models here
from fetcher.gscholar.models import GoogleScholarEntry


def scholarInsert(data: List[GoogleScholarEntry]) -> int:
    """
    Insert Google Scholar Publication objects into database with complete relational mapping.
    Performs transactional insertion of publications with their associated authors, affiliations,
    and keywords. Creates many-to-many relationships between entities and logs the operation.
    Uses database rollback on errors to maintain data integrity.

    :param List[Publication] data: List of Publication objects from Google Scholar API.
    :return: Number of publications successfully inserted into database.
    :rtype: int
    """
    db = get_db()
    cursor = db.cursor()

    try:
        insert_count = len(data)

        cursor.execute("INSERT INTO InsertLog (Source, articleInsertCount) VALUES (?, ?)",
                       ("Google Scholar", insert_count))
        insert_id = cursor.lastrowid

        for publication in data:
            _insert_publication(publication, insert_id, cursor)

        db.commit()
        return insert_count

    except Exception as e:
        db.rollback()
        print(f"Database operation error: {e}")
        raise
    finally:
        cursor.close()


def _insert_publication(publication: GoogleScholarEntry, insert_id: int, cursor) -> int:
    """
    Insert a single publication with its associated data.

    :param Publication publication: Publication object from Google Scholar.
    :param int insert_id: Insert log ID for tracking this batch operation.
    :param cursor: Database cursor for executing SQL statements.
    :return: Database ID of the newly inserted article.
    :rtype: int
    """

    # Extract keywords from abstract or other sources if available
    keywords = []
    # if bib.get('abstract'):
    #     # Simple keyword extraction
    #     abstract_words = bib.get('abstract', '').split()
    #     keywords = [word.strip('.,!?;:') for word in abstract_words if len(word) > 5][:10]

    # Insert article
    article_id = _insert_scholar_article(publication, insert_id, cursor)

    # Handle authors
    author_ids = []
    # Parse author string (Google Scholar often provides comma-separated author names)
    author_names = [name.strip() for name in publication.authors.split(',')]
    for author_name in author_names:
        if author_name:
            author_id = _insert_author_by_name(author_name, insert_id, cursor)
            author_ids.append(author_id)

    # Handle affiliations (limited info available from Google Scholar)
    affiliation_ids = []
    # if bib.get('publisher'):
    #     affiliation_id = _insert_affiliation_by_name(bib.get('publisher'), insert_id, cursor)
    #     affiliation_ids.append(affiliation_id)

    # Handle keywords
    keyword_ids = _insert_scholar_keywords(keywords, insert_id, cursor)

    # Create relationships
    _bind_authors(author_ids, article_id, cursor)
    _bind_affiliations(affiliation_ids, article_id, cursor)
    _bind_keywords(keyword_ids, article_id, cursor)

    return article_id


def _insert_scholar_article(publication: GoogleScholarEntry, insert_id: int, cursor) -> int:
    """
    Insert article record from Google Scholar Publication object.

    :param Publication publication: Publication object containing article data.
    :param int insert_id: Insert log ID for tracking this batch operation.
    :param cursor: Database cursor for executing SQL statements.
    :return: Database ID of the newly inserted article record.
    :rtype: int
    """

    # Extract DOI from pub_url if available
    doi = None
    pub_url = publication.link
    if 'doi.org' in pub_url:
        doi = pub_url.split('doi.org/')[-1]

    cursor.execute("""
        INSERT INTO Article (
            SourceID, SourceURL, Name, PublishDate,
            ISSN, EISSN, DOI, Publisher, Volume, Description, 
            Type, SubType, CitedByCount, Sponsor, InsertID
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'g'+publication.id,
        publication.link,
        publication.title,
        publication.year,
        None,
        None,
        doi,
        None,  # TODO: bib.get('publisher', ''),
        None,  # bib.get('volume'),
        None,
        publication.entry_type,
        None,
        None,  # TODO: publication.get('num_citations', 0),
        None,
        insert_id
    ))

    return cursor.lastrowid



def _insert_author_by_name(author_name: str, insert_id: int, cursor) -> int:
    """
    Insert or retrieve author record by name only (when detailed author data not available).

    :param str author_name: Full name of the author.
    :param int insert_id: Insert log ID for tracking this batch operation.
    :param cursor: Database cursor for executing SQL statements.
    :return: Database ID of the author record.
    :rtype: int
    """
    # Check if author already exists by full name
    cursor.execute("SELECT ID FROM Author WHERE FullName = ?", (author_name,))
    result = cursor.fetchone()
    if result:
        return result[0]

    # Parse name components
    name_parts = author_name.split()
    first_name = name_parts[0] if name_parts else ''
    surname = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
    initials = ''.join([part[0] + '.' for part in name_parts if part]) if name_parts else ''

    cursor.execute("""
        INSERT INTO Author (
            SourceID, SourceURL, FullName, 
            FirstName, SureName, Initials, InsertID
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        None,
        None,
        author_name,
        first_name,
        surname,
        initials,
        insert_id
    ))

    return cursor.lastrowid


def _insert_affiliation_by_name(affiliation_name: str, insert_id: int, cursor) -> int:
    """
    Insert or retrieve affiliation record by name only.

    :param str affiliation_name: Name of the affiliation/publisher.
    :param int insert_id: Insert log ID for tracking this batch operation.
    :param cursor: Database cursor for executing SQL statements.
    :return: Database ID of the affiliation record.
    :rtype: int
    """
    # Check if affiliation already exists by name
    cursor.execute("SELECT ID FROM Affiliation WHERE Name = ?", (affiliation_name,))
    result = cursor.fetchone()
    if result:
        return result[0]

    cursor.execute("""
        INSERT INTO Affiliation (
            SourceID, SourceURL, Name, 
            Country, City, InsertID
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        None,  # No Scopus ID available
        None,  # No URL available
        affiliation_name,
        None,  # Country not available
        None,  # City not available
        insert_id
    ))

    return cursor.lastrowid


def _insert_scholar_keywords(keywords: List[str], insert_id: int, cursor) -> List[int]:
    """
    Insert or retrieve keyword records from database.

    :param List[str] keywords: List of keyword strings.
    :param int insert_id: Insert log ID for tracking this batch operation.
    :param cursor: Database cursor for executing SQL statements.
    :return: List of database IDs for processed keywords.
    :rtype: List[int]
    """
    keyword_ids = []

    for keyword in keywords:
        keyword = keyword.strip()
        if not keyword:
            continue

        cursor.execute("SELECT ID FROM Keywords WHERE Keyword = ?", (keyword,))
        result = cursor.fetchone()

        if result:
            keyword_id = result[0]
        else:
            cursor.execute("""
                INSERT INTO Keywords (Keyword, InsertID) VALUES (?, ?)
            """, (keyword, insert_id))
            keyword_id = cursor.lastrowid

        keyword_ids.append(keyword_id)

    return keyword_ids


def _bind_authors(author_ids: List[int], article_id: int, cursor) -> None:
    """Create many-to-many relationships between articles and authors."""
    for author_id in author_ids:
        cursor.execute("""
            INSERT INTO ArticlexAuthor (ArticleID, AuthorID)
            VALUES (?, ?)
        """, (article_id, author_id))


def _bind_keywords(keyword_ids: List[int], article_id: int, cursor) -> None:
    """Create many-to-many relationships between articles and keywords."""
    for keyword_id in keyword_ids:
        cursor.execute("""
            INSERT INTO ArticlexKeywords (ArticleID, KeywordsID)
            VALUES (?, ?)
        """, (article_id, keyword_id))


def _bind_affiliations(affiliation_ids: List[int], article_id: int, cursor) -> None:
    """Create many-to-many relationships between articles and affiliations."""
    for affiliation_id in affiliation_ids:
        cursor.execute("""
            INSERT INTO ArticlexAffiliation (ArticleID, AffiliationID)
            VALUES (?, ?)
        """, (article_id, affiliation_id))
