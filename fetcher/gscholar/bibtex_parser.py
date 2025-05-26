from typing import Optional, List

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase

from fetcher.gscholar.models import GoogleScholarBibtexScrapeEntry, GoogleScholarHtmlEntry, GoogleScholarEntry, \
    GoogleScholarBibtexEntry


def parse_bibtex_entry(e: GoogleScholarBibtexScrapeEntry) -> Optional[GoogleScholarBibtexEntry]:
    """
    Parse a single BibTeX entry from a Google Scholar BibTeX scrape entry.

    This function loads the raw BibTeX data contained within a
    `GoogleScholarBibtexScrapeEntry`, extracts the first entry in the resulting
    `BibDatabase`, and constructs a `GoogleScholarBibtexEntry` from its fields.
    If no valid entry is found, returns `None`.

    :param e: A `GoogleScholarBibtexScrapeEntry` containing raw BibTeX text and
              its associated Google Scholar ID.
    :type e: GoogleScholarBibtexScrapeEntry
    :return: A `GoogleScholarBibtexEntry` populated with fields (title, author,
             entry type, BibTeX ID, Google Scholar ID, year, journal, organization)
             if parsing succeeds; otherwise, `None`.
    :rtype: Optional[GoogleScholarBibtexEntry]
    """

    bib_db: BibDatabase = bibtexparser.loads(e.bibtex_data, parser=bibtexparser.bparser)
    e_list = bib_db.get_entry_list()

    if e_list and len(e_list) > 0:
        fe = e_list[0]
        parsed_entry = GoogleScholarBibtexEntry(title=fe['title'],
                                                author=fe['author'],
                                                entry_type=fe['ENTRYTYPE'],
                                                bibtex_id=fe['ID'],
                                                google_id=e.id,
                                                year=fe.get('year', ''),
                                                journal=fe.get('journal', ''),
                                                organization=fe.get('organization', ''))
        return parsed_entry
    return None


def merge_entries(html_entries: List[GoogleScholarHtmlEntry], bibtex_entries: List[GoogleScholarBibtexEntry]):
    """
    Merge a list of HTML-based Google Scholar entries with their corresponding BibTeX entries.

    For each HTML-based entry in `html_entries`, this function attempts to find a matching
    BibTeX entry (by Google Scholar ID) within `bibtex_entries`. If a match is found,
    the more reliable fields (title, authors, journal, organization, entry type, year)
    from the BibTeX entry overwrite the HTML-derived values.

    :param html_entries: A list of `GoogleScholarHtmlEntry` objects obtained by scraping
                         the HTML results page, each containing basic metadata (id,
                         title, authors, file type, link, bibtex URI).
    :type html_entries: List[GoogleScholarHtmlEntry]
    :param bibtex_entries: A list of `GoogleScholarBibtexEntry` objects parsed from
                           individual BibTeX strings; these contain richer metadata
                           (author, title, journal, organization, entry type, year,
                           and Google Scholar ID).
    :type bibtex_entries: List[GoogleScholarBibtexEntry]
    :return: A list of `GoogleScholarEntry` objects where each entry in `html_entries`
             is combined with its matching BibTeX data (if available). The resulting
             entries will always include the HTML-derived fields (`id`, `file_type`,
             `link`, `bibtex_uri`), but if a BibTeX match exists, the `title` and
             `authors` are replaced by the BibTeX values, and additional fields
             (`journal`, `organization`, `entry_type`, `year`) are populated.
    :rtype: List[GoogleScholarEntry]
    """

    def find_bib(google_id: str) -> Optional[GoogleScholarBibtexEntry]:
        found_bib = None
        for e in bibtex_entries:
            if e.google_id == google_id:
                found_bib = e
                break
        if found_bib is not None:
            bibtex_entries.remove(found_bib)
        return found_bib

    merged_entries = []
    for h_entry in html_entries:
        bib_entry = find_bib(h_entry.id)
        merged_entry = GoogleScholarEntry(id=h_entry.id,
                                          title=h_entry.title,
                                          authors=h_entry.authors,
                                          file_type=h_entry.file_type,
                                          link=h_entry.link,
                                          bibtex_uri=h_entry.bibtex_uri)
        if bib_entry is not None:
            # authors and title are more reliable in BibTex
            # (HTML usually contains trimmed values)
            merged_entry.authors = bib_entry.author
            merged_entry.title = bib_entry.title

            merged_entry.journal = bib_entry.journal
            merged_entry.organization = bib_entry.organization
            merged_entry.entry_type = bib_entry.entry_type
            merged_entry.year = bib_entry.year
        merged_entries.append(merged_entry)
    return merged_entries
