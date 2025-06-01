from fetcher.scopus_batch.parser_models import Publication

from database.dbContext import get_db
from typing import List
from dataclasses import dataclass, field


def scopusBatchInsert(data: List[Publication]):
    db = get_db()
    cursor = db.cursor()

    try:
        insert_count = len(data)

        cursor.execute("INSERT INTO InsertLog (Source, articleInsertCount) VALUES (?, ?)", ("Scopus", insert_count))
        insert_id = cursor.lastrowid

        for publication in data:
            author_ids = insert_publication_authors(publication.authors, insert_id, cursor)
            affiliation_ids = insert_publication_affiliations(publication.affiliations, insert_id, cursor)

            all_keywords = publication.author_keywords + publication.index_keywords
            keyword_ids = insert_publication_keywords(all_keywords, insert_id, cursor)

            article_id = insert_publication_article(publication, insert_id, cursor)

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


def insert_publication_article(publication: Publication, insert_id: int, cursor) -> int:
    cursor.execute("SELECT ID FROM Article WHERE DOI = ?", (publication.doi,))
    result = cursor.fetchone()

    if result:
        return result[0]
    else:
        # if we get only year convert it to 1st of january
        publish_date = f"{publication.year}-01-01" if publication.year else None

        cursor.execute("""
            INSERT INTO Article (
                SourceID, SourceURL, Name, PublishDate, ISSN, EISSN, 
                Volume, Description, Type, SubType, CitedByCount, 
                Sponsor, DOI, Publisher, InsertID
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            None,
            publication.link,
            publication.source_title,
            publish_date,
            publication.issn,
            None,
            publication.volume,
            publication.abstract,
            None,
            publication.document_type,
            publication.cited_by,
            publication.funding_details,
            publication.doi,
            publication.publisher,
            insert_id
        ))
        return cursor.lastrowid


def parse_author_name(full_name: str) -> tuple:
    """
    Parse author name to extract components and Scopus ID.

    :param str full_name: Full author name potentially with Scopus ID in parentheses
    :return: Tuple of (full_name, first_name, surname, initials, scopus_id)
    :rtype: tuple
    """
    # Extract Scopus ID from parentheses
    scopus_id = None
    if '(' in full_name and ')' in full_name:
        scopus_part = full_name[full_name.rfind('('):full_name.rfind(')') + 1]
        scopus_id = scopus_part.strip('()')
        # Remove the Scopus ID part from the name
        name_part = full_name[:full_name.rfind('(')].strip()
    else:
        name_part = full_name.strip()

    # Split by comma to separate surname from given names
    if ',' in name_part:
        surname = name_part.split(',')[0].strip()
        given_names = name_part.split(',')[1].strip()

        # Extract first name and create initials
        name_parts = given_names.split()
        first_name = name_parts[0] if name_parts else None

        # Create initials from all given names
        initials = ''.join([part[0] + '.' for part in name_parts if part])

    else:
        # Fallback if no comma
        parts = name_part.split()
        surname = parts[0] if parts else name_part
        first_name = parts[1] if len(parts) > 1 else None
        initials = ''.join([part[0] + '.' for part in parts[1:] if part])

    return full_name, first_name, surname, initials, scopus_id


def insert_publication_authors(authors: List[str], insert_id: int, cursor) -> List[int]:
    """
    Insert or retrieve author records from database using upsert pattern.
    First checks by Scopus ID if available, then by full name.

    :param List[str] authors: List of author name strings
    :param int insert_id: Insert log ID for tracking this batch operation
    :param cursor: Database cursor for executing SQL statements
    :return: List of database IDs for processed authors
    :rtype: List[int]
    """
    author_ids = []

    for author_name in authors:
        author_name = author_name.strip()
        if not author_name:
            continue

        full_name, first_name, surname, initials, scopus_id = parse_author_name(author_name)

        if scopus_id:
            cursor.execute("SELECT ID FROM Author WHERE SourceID = ?", ('s' + scopus_id,))
            result = cursor.fetchone()
        else:
            result = None

        if not result:
            cursor.execute("SELECT ID FROM Author WHERE FullName = ?", (full_name,))
            result = cursor.fetchone()

        if result:
            author_id = result[0]
        else:
            cursor.execute("""
                INSERT INTO Author (
                    SourceID, SourceURL, FullName, FirstName, 
                    SureName, Initials, InsertID
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                's' + scopus_id if scopus_id else None,
                None,
                full_name,
                first_name,
                surname,
                initials,
                insert_id
            ))
            author_id = cursor.lastrowid
        author_ids.append(author_id)
    return author_ids


def insert_publication_affiliations(affiliations: List[str], insert_id: int, cursor) -> List[int]:
    """
    Insert or retrieve affiliation records from database using upsert pattern based on name.

    :param List[str] affiliations: List of affiliation name strings
    :param int insert_id: Insert log ID for tracking this batch operation
    :param cursor: Database cursor for executing SQL statements
    :return: List of database IDs for processed affiliations
    :rtype: List[int]
    """
    affiliation_ids = []
    for affiliation_name in affiliations:
        affiliation_name = affiliation_name.strip()
        if not affiliation_name:
            continue

        cursor.execute("SELECT ID FROM Affiliation WHERE Name = ?", (affiliation_name,))
        result = cursor.fetchone()

        if result:
            affiliation_id = result[0]
        else:
            cursor.execute("""
                INSERT INTO Affiliation (
                    SourceID, SourceURL, Name, Country, City, InsertID
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                None,
                None,
                affiliation_name,
                None,
                None,
                insert_id
            ))
            affiliation_id = cursor.lastrowid
        affiliation_ids.append(affiliation_id)
    return affiliation_ids


def insert_publication_keywords(keywords: List[str], insert_id: int, cursor) -> List[int]:
    """
    Insert or retrieve keyword records from database using upsert pattern based on keyword text.
    Normalizes keywords by stripping whitespace and converting to lowercase.

    :param List[str] keywords: List of keyword strings
    :param int insert_id: Insert log ID for tracking this batch operation
    :param cursor: Database cursor for executing SQL statements
    :return: List of database IDs for processed keywords
    :rtype: List[int]
    """
    keyword_ids = []
    for keyword in keywords:
        keyword = keyword.strip().lower()
        if not keyword:
            continue

        cursor.execute("SELECT ID FROM Keywords WHERE Keyword = ?", (keyword,))
        result = cursor.fetchone()

        if result:
            keyword_id = result[0]
        else:
            cursor.execute("""
                INSERT INTO Keywords (Keyword, InsertID)
                VALUES (?, ?)
            """, (keyword, insert_id))
            keyword_id = cursor.lastrowid
        keyword_ids.append(keyword_id)
    return keyword_ids


def bind_authors(author_ids: List[int], article_id: int, cursor):
    """
    Create many-to-many relationships between articles and authors in junction table.
    Checks for existing relationships before inserting to ensure uniqueness.

    :param List[int] author_ids: List of author database IDs to associate with article
    :param int article_id: Database ID of the article to bind authors to
    :param cursor: Database cursor for executing SQL statements
    :return: None
    """
    for author_id in author_ids:
        try:
            # Check if relationship already exists
            cursor.execute("""
                SELECT 1 FROM ArticlexAuthor 
                WHERE ArticleID = ? AND AuthorID = ?
            """, (article_id, author_id))

            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO ArticlexAuthor (ArticleID, AuthorID)
                    VALUES (?, ?)
                """, (article_id, author_id))
        except Exception as e:
            print(f"Error binding author {author_id} to article {article_id}: {e}")
            raise


def bind_affiliations(affiliation_ids: List[int], article_id: int, cursor):
    """
    Create many-to-many relationships between articles and affiliations in junction table.
    Checks for existing relationships before inserting to ensure uniqueness.

    :param List[int] affiliation_ids: List of affiliation database IDs to associate with article
    :param int article_id: Database ID of the article to bind affiliations to
    :param cursor: Database cursor for executing SQL statements
    :return: None
    """
    for affiliation_id in affiliation_ids:
        try:
            # Check if relationship already exists
            cursor.execute("""
                SELECT 1 FROM ArticlexAffiliation 
                WHERE ArticleID = ? AND AffiliationID = ?
            """, (article_id, affiliation_id))

            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO ArticlexAffiliation (ArticleID, AffiliationID)
                    VALUES (?, ?)
                """, (affiliation_id, affiliation_id))
        except Exception as e:
            print(f"Error binding affiliation {affiliation_id} to article {article_id}: {e}")
            raise


def bind_keywords(keyword_ids: List[int], article_id: int, cursor):
    """
    Create many-to-many relationships between articles and keywords in junction table.
    Checks for existing relationships before inserting to ensure uniqueness.

    :param List[int] keyword_ids: List of keyword database IDs to associate with article
    :param int article_id: Database ID of the article to bind keywords to
    :param cursor: Database cursor for executing SQL statements
    :return: None
    """
    for keyword_id in keyword_ids:
        try:
            # Check if relationship already exists
            cursor.execute("""
                SELECT 1 FROM ArticlexKeywords 
                WHERE ArticleID = ? AND KeywordsID = ?
            """, (article_id, keyword_id))

            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO ArticlexKeywords (ArticleID, KeywordsID)
                    VALUES (?, ?)
                """, (article_id, keyword_id))
        except Exception as e:
            print(f"Error binding keyword {keyword_id} to article {article_id}: {e}")
            raise