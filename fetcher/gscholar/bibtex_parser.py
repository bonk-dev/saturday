from dataclasses import dataclass
from typing import Any, Optional

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase

from fetcher.gscholar.models import GoogleScholarBibtexScrapeEntry


@dataclass
class GoogleScholarBibtexEntry:
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
                                                year=fe.get('year', ''),
                                                journal=fe.get('journal', ''),
                                                organization=fe.get('organization', ''))
        return parsed_entry
    return None
