from dataclasses import dataclass


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
