from dataclasses import dataclass
from typing import Optional, List

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase

from fetcher.gscholar.models import GoogleScholarBibtexScrapeEntry, GoogleScholarHtmlEntry, GoogleScholarEntry


@dataclass
class GoogleScholarBibtexEntry:
    google_id: str
    title: str
    author: str
    entry_type: str
    bibtex_id: str

    year: Optional[str]
    journal: Optional[str]
    organization: Optional[str]


def parse_bibtex_entry(e: GoogleScholarBibtexScrapeEntry) -> Optional[GoogleScholarBibtexEntry]:
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
