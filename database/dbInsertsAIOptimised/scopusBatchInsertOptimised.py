from fetcher.scopus_batch.parser_models import Publication
from database.dbContext import get_db
from typing import List, Dict, Set
from dataclasses import dataclass, field


def scopusBatchInsertOptimised(data: List[Publication]):
    db = get_db()
    cursor = db.cursor()

    try:
        insert_count = len(data)
        cursor.execute("INSERT INTO InsertLog (Source, articleInsertCount) VALUES (?, ?)", ("Scopus", insert_count))
        insert_id = cursor.lastrowid

        # Batch process all entities first - collect UNIQUE entities only
        all_authors = set()
        all_affiliations = set()
        all_keywords = set()
        all_dois = set()

        # Collect all unique entities with proper normalization
        for publication in data:
            # Normalize and deduplicate authors
            for author in publication.authors:
                author_clean = author.strip()
                if author_clean:
                    all_authors.add(author_clean)

            # Normalize and deduplicate affiliations
            for affiliation in publication.affiliations:
                affiliation_clean = affiliation.strip()
                if affiliation_clean:
                    all_affiliations.add(affiliation_clean)

            # Normalize and deduplicate keywords
            all_pub_keywords = (publication.author_keywords or []) + (publication.index_keywords or [])
            for keyword in all_pub_keywords:
                keyword_clean = keyword.strip()
                if keyword_clean:
                    all_keywords.add(keyword_clean)

            # Deduplicate DOIs
            if publication.doi and publication.doi.strip():
                all_dois.add(publication.doi.strip())

        # Batch lookup and insert entities
        author_cache = batch_process_authors(list(all_authors), insert_id, cursor)
        affiliation_cache = batch_process_affiliations(list(all_affiliations), insert_id, cursor)
        keyword_cache = batch_process_keywords(list(all_keywords), insert_id, cursor)
        existing_articles = batch_lookup_existing_articles(list(all_dois), cursor)

        # Process articles and relationships
        article_author_relations = []
        article_affiliation_relations = []
        article_keyword_relations = []

        for publication in data:
            # Skip if article already exists
            if publication.doi and publication.doi.strip() in existing_articles:
                continue

            # Insert article
            article_id = insert_publication_article(publication, insert_id, cursor)

            # Collect relationships for batch insert - with proper deduplication
            processed_authors = set()
            for author in (publication.authors or []):
                author_clean = author.strip()
                if author_clean and author_clean in author_cache and author_clean not in processed_authors:
                    article_author_relations.append((article_id, author_cache[author_clean]))
                    processed_authors.add(author_clean)

            processed_affiliations = set()
            for affiliation in (publication.affiliations or []):
                affiliation_clean = affiliation.strip()
                if affiliation_clean and affiliation_clean in affiliation_cache and affiliation_clean not in processed_affiliations:
                    article_affiliation_relations.append((article_id, affiliation_cache[affiliation_clean]))
                    processed_affiliations.add(affiliation_clean)

            processed_keywords = set()
            all_pub_keywords = (publication.author_keywords or []) + (publication.index_keywords or [])
            for keyword in all_pub_keywords:
                keyword_clean = keyword.strip()
                if keyword_clean and keyword_clean in keyword_cache and keyword_clean not in processed_keywords:
                    article_keyword_relations.append((article_id, keyword_cache[keyword_clean]))
                    processed_keywords.add(keyword_clean)

        # Batch insert all relationships
        batch_insert_relations(article_author_relations, "ArticlexAuthor", "ArticleID", "AuthorID", cursor)
        batch_insert_relations(article_affiliation_relations, "ArticlexAffiliation", "ArticleID", "AffiliationID",
                               cursor)
        batch_insert_relations(article_keyword_relations, "ArticlexKeywords", "ArticleID", "KeywordsID", cursor)

        db.commit()
        return insert_count

    except Exception as e:
        db.rollback()
        print(f"Database operation error: {e}")
        raise
    finally:
        cursor.close()


def batch_lookup_existing_articles(dois: List[str], cursor) -> Set[str]:
    """Batch lookup existing articles by DOI with chunking"""
    if not dois:
        return set()

    existing_dois = set()
    chunk_size = 999  # SQLite variable limit

    for i in range(0, len(dois), chunk_size):
        chunk = dois[i:i + chunk_size]
        placeholders = ','.join('?' * len(chunk))
        cursor.execute(f"SELECT DOI FROM Article WHERE DOI IN ({placeholders})", chunk)
        existing_dois.update(row[0] for row in cursor.fetchall())

    return existing_dois


def batch_process_authors(authors: List[str], insert_id: int, cursor) -> Dict[str, int]:
    """Batch process authors and return name->id mapping with chunking and deduplication"""
    if not authors:
        return {}

    # Remove duplicates at the start
    unique_authors = list(set(authors))

    author_cache = {}
    parsed_authors = {}
    scopus_ids = []
    full_names = []
    chunk_size = 999  # SQLite variable limit

    # Parse all unique authors first
    for author_name in unique_authors:
        full_name, first_name, surname, initials, scopus_id = parse_author_name(author_name)
        parsed_authors[author_name] = (full_name, first_name, surname, initials, scopus_id)
        if scopus_id:
            scopus_ids.append('s' + scopus_id)
        full_names.append(full_name)

    # Remove duplicate scopus_ids and full_names for lookup
    unique_scopus_ids = list(set(scopus_ids))
    unique_full_names = list(set(full_names))

    # Batch lookup by Scopus ID with chunking
    scopus_results = {}
    if unique_scopus_ids:
        for i in range(0, len(unique_scopus_ids), chunk_size):
            chunk = unique_scopus_ids[i:i + chunk_size]
            placeholders = ','.join('?' * len(chunk))
            cursor.execute(f"SELECT SourceID, ID FROM Author WHERE SourceID IN ({placeholders})", chunk)
            scopus_results.update({row[0]: row[1] for row in cursor.fetchall()})

    # Batch lookup by full name for authors without Scopus ID or not found
    remaining_names = []
    for author_name in unique_authors:
        _, _, _, _, scopus_id = parsed_authors[author_name]
        scopus_key = 's' + scopus_id if scopus_id else None
        if not scopus_key or scopus_key not in scopus_results:
            remaining_names.append(parsed_authors[author_name][0])  # full_name

    # Remove duplicates from remaining names
    unique_remaining_names = list(set(remaining_names))
    name_results = {}
    if unique_remaining_names:
        for i in range(0, len(unique_remaining_names), chunk_size):
            chunk = unique_remaining_names[i:i + chunk_size]
            placeholders = ','.join('?' * len(chunk))
            cursor.execute(f"SELECT FullName, ID FROM Author WHERE FullName IN ({placeholders})", chunk)
            name_results.update({row[0]: row[1] for row in cursor.fetchall()})

    # Prepare batch insert for new authors - ensure no duplicates
    new_authors = []
    new_author_names = []
    seen_authors = set()  # Track by (full_name, scopus_id) to prevent duplicates

    for author_name in unique_authors:
        full_name, first_name, surname, initials, scopus_id = parsed_authors[author_name]
        scopus_key = 's' + scopus_id if scopus_id else None

        # Create a unique key for this author
        author_key = (full_name, scopus_key)

        if scopus_key and scopus_key in scopus_results:
            author_cache[author_name] = scopus_results[scopus_key]
        elif full_name in name_results:
            author_cache[author_name] = name_results[full_name]
        elif author_key not in seen_authors:
            new_authors.append((scopus_key, None, full_name, first_name, surname, initials, insert_id))
            new_author_names.append(author_name)
            seen_authors.add(author_key)

    # Batch insert new authors with chunking
    if new_authors:
        for i in range(0, len(new_authors), chunk_size):
            chunk = new_authors[i:i + chunk_size]
            cursor.executemany("""
                INSERT INTO Author (SourceID, SourceURL, FullName, FirstName, SureName, Initials, InsertID)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, chunk)

        # Get IDs for newly inserted authors by looking them up
        if new_author_names:
            new_full_names = [parsed_authors[name][0] for name in new_author_names]
            unique_new_full_names = list(set(new_full_names))

            for i in range(0, len(unique_new_full_names), chunk_size):
                chunk = unique_new_full_names[i:i + chunk_size]
                placeholders = ','.join('?' * len(chunk))
                cursor.execute(f"SELECT FullName, ID FROM Author WHERE FullName IN ({placeholders}) AND InsertID = ?",
                               chunk + [insert_id])
                chunk_results = {row[0]: row[1] for row in cursor.fetchall()}

                # Map back to original author names
                for author_name in new_author_names:
                    full_name = parsed_authors[author_name][0]
                    if full_name in chunk_results:
                        author_cache[author_name] = chunk_results[full_name]

    return author_cache


def batch_process_affiliations(affiliations: List[str], insert_id: int, cursor) -> Dict[str, int]:
    """Batch process affiliations and return name->id mapping with chunking and deduplication"""
    if not affiliations:
        return {}

    # Remove duplicates at the start
    unique_affiliations = list(set(affiliations))

    chunk_size = 999  # SQLite variable limit
    existing = {}

    # Batch lookup existing affiliations with chunking
    for i in range(0, len(unique_affiliations), chunk_size):
        chunk = unique_affiliations[i:i + chunk_size]
        placeholders = ','.join('?' * len(chunk))
        cursor.execute(f"SELECT Name, ID FROM Affiliation WHERE Name IN ({placeholders})", chunk)
        existing.update({row[0]: row[1] for row in cursor.fetchall()})

    # Prepare batch insert for new affiliations - ensure no duplicates
    new_affiliations = []
    seen_affiliations = set()

    for name in unique_affiliations:
        if name not in existing and name not in seen_affiliations:
            new_affiliations.append((None, None, name, None, None, insert_id))
            seen_affiliations.add(name)

    if new_affiliations:
        # Batch insert with chunking
        for i in range(0, len(new_affiliations), chunk_size):
            chunk = new_affiliations[i:i + chunk_size]
            cursor.executemany("""
                INSERT INTO Affiliation (SourceID, SourceURL, Name, Country, City, InsertID)
                VALUES (?, ?, ?, ?, ?, ?)
            """, chunk)

        # Get IDs for newly inserted affiliations
        new_names = [name for name in unique_affiliations if name not in existing]
        unique_new_names = list(set(new_names))  # Remove duplicates again

        for i in range(0, len(unique_new_names), chunk_size):
            chunk = unique_new_names[i:i + chunk_size]
            placeholders = ','.join('?' * len(chunk))
            cursor.execute(f"SELECT Name, ID FROM Affiliation WHERE Name IN ({placeholders}) AND InsertID = ?",
                           chunk + [insert_id])
            existing.update({row[0]: row[1] for row in cursor.fetchall()})

    return existing


def batch_process_keywords(keywords: List[str], insert_id: int, cursor) -> Dict[str, int]:
    """Batch process keywords and return keyword->id mapping with chunking and deduplication"""
    if not keywords:
        return {}

    # Remove duplicates at the start
    unique_keywords = list(set(keywords))

    chunk_size = 999  # SQLite variable limit
    existing = {}

    # Batch lookup existing keywords with chunking
    for i in range(0, len(unique_keywords), chunk_size):
        chunk = unique_keywords[i:i + chunk_size]
        placeholders = ','.join('?' * len(chunk))
        cursor.execute(f"SELECT Keyword, ID FROM Keywords WHERE Keyword IN ({placeholders})", chunk)
        existing.update({row[0]: row[1] for row in cursor.fetchall()})

    # Prepare batch insert for new keywords - ensure no duplicates
    new_keywords = []
    seen_keywords = set()

    for keyword in unique_keywords:
        if keyword not in existing and keyword not in seen_keywords:
            new_keywords.append((keyword, insert_id))
            seen_keywords.add(keyword)

    if new_keywords:
        # Batch insert with chunking
        for i in range(0, len(new_keywords), chunk_size):
            chunk = new_keywords[i:i + chunk_size]
            cursor.executemany("INSERT INTO Keywords (Keyword, InsertID) VALUES (?, ?)", chunk)

        # Get IDs for newly inserted keywords
        new_keyword_list = [kw for kw in unique_keywords if kw not in existing]
        unique_new_keywords = list(set(new_keyword_list))  # Remove duplicates again

        for i in range(0, len(unique_new_keywords), chunk_size):
            chunk = unique_new_keywords[i:i + chunk_size]
            placeholders = ','.join('?' * len(chunk))
            cursor.execute(f"SELECT Keyword, ID FROM Keywords WHERE Keyword IN ({placeholders}) AND InsertID = ?",
                           chunk + [insert_id])
            existing.update({row[0]: row[1] for row in cursor.fetchall()})

    return existing


def batch_insert_relations(relations: List[tuple], table_name: str, col1: str, col2: str, cursor):
    """Batch insert relationship records with chunking"""
    if not relations:
        return

    # Remove duplicates
    unique_relations = list(set(relations))
    chunk_size = 999  # SQLite variable limit - but since we have 2 params per relation, we use 499
    actual_chunk_size = chunk_size // 2

    for i in range(0, len(unique_relations), actual_chunk_size):
        chunk = unique_relations[i:i + actual_chunk_size]
        cursor.executemany(f"""
            INSERT OR IGNORE INTO {table_name} ({col1}, {col2})
            VALUES (?, ?)
        """, chunk)


def insert_publication_article(publication: Publication, insert_id: int, cursor) -> int:
    """Insert a single article (DOI check already done in batch)"""
    publish_date = f"{publication.year}-01-01" if publication.year else None

    cursor.execute("""
        INSERT INTO Article (
            SourceID, SourceURL, Name, PublishDate, ISSN, EISSN, 
            Volume, Description, Type, SubType, CitedByCount, 
            Sponsor, DOI, Publisher, InsertID
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        None, publication.link, publication.source_title, publish_date,
        publication.issn, None, publication.volume, publication.abstract,
        None, publication.document_type, publication.cited_by,
        publication.funding_details, publication.doi, publication.publisher, insert_id
    ))
    return cursor.lastrowid


def parse_author_name(full_name: str) -> tuple:
    """Parse author name into components (unchanged from original)"""
    scopus_id = None
    if '(' in full_name and ')' in full_name:
        scopus_part = full_name[full_name.rfind('('):full_name.rfind(')') + 1]
        scopus_id = scopus_part.strip('()')
        name_part = full_name[:full_name.rfind('(')].strip()
    else:
        name_part = full_name.strip()

    if ',' in name_part:
        surname = name_part.split(',')[0].strip()
        given_names = name_part.split(',')[1].strip()
        name_parts = given_names.split()
        first_name = name_parts[0] if name_parts else None
        initials = ''.join([part[0] + '.' for part in name_parts if part])
    else:
        parts = name_part.split()
        surname = parts[0] if parts else name_part
        first_name = parts[1] if len(parts) > 1 else None
        initials = ''.join([part[0] + '.' for part in parts[1:] if part])

    return full_name, first_name, surname, initials, scopus_id