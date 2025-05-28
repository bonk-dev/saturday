from dataclasses import dataclass
from typing import Optional


@dataclass
class GoogleScholarHtmlEntry:
    """Class for holding data scraped from the Google Scholar search HTML page"""
    id: str
    title: str
    link: str
    file_type: str
    authors: str
    bibtex_uri: str

    def to_debug_string(self) -> str:
        return (f'search_scholar: id={self.id!r} title={self.title!r}, link={self.link!r}, '
                f'file_type={self.file_type!r}, authors={self.authors!r}, bibtex_uri={self.bibtex_uri!r}')


@dataclass
class GoogleScholarBibtexScrapeEntry:
    """Class for holding BibTex entries downloaded from Google Scholar"""
    id: str
    bibtex_data: str


@dataclass
class GoogleScholarBibtexEntry:
    """Class for holding parsed BibTex entries"""
    google_id: str
    title: str
    author: str
    entry_type: str
    bibtex_id: str

    year: Optional[str]
    journal: Optional[str]
    organization: Optional[str]


@dataclass
class GoogleScholarEntry:
    """Class for holding Google Scholar entries merged from HTML and BibTex entries"""
    id: str
    title: str
    link: str
    file_type: str
    authors: str
    bibtex_uri: str

    entry_type: Optional[str] = None
    year: Optional[str] = None
    journal: Optional[str] = None
    organization: Optional[str] = None
