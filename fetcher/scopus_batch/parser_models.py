from dataclasses import dataclass, field
from typing import List


@dataclass
class Publication:
    title: str
    year: str
    source_title: str
    volume: str
    issue: str
    article_number: str
    page_start: str
    page_end: str
    page_count: str
    cited_by: str
    doi: str
    link: str
    abstract: str
    funding_details: str
    funding_texts: str
    references: str
    correspondence_address: str
    publisher: str
    issn: str
    isbn: str
    coden: str
    pubmed_id: str
    language_of_orig_doc: str
    abbr_source_title: str
    document_type: str
    publication_stage: str
    source: str
    eid: str

    authors: List[str] = field(default_factory=list)
    affiliations: List[str] = field(default_factory=list)
    author_keywords: List[str] = field(default_factory=list)
    index_keywords: List[str] = field(default_factory=list)
    tradenames: List[str] = field(default_factory=list)
    manufacturers: List[str] = field(default_factory=list)
    editors: List[str] = field(default_factory=list)
    sponsors: List[str] = field(default_factory=list)
    open_access: List[str] = field(default_factory=list)

    def to_debug_string(self) -> str:
        lines = [
            f"authors={self.authors!r}",
            f"title={self.title!r}",
            f"year={self.year!r}",
            f"source_title={self.source_title!r}",
            f"abbr_source_title={self.abbr_source_title!r}",
            f"document_type={self.document_type!r}",
            f"publication_stage={self.publication_stage!r}",
            f"open_access={self.open_access!r}",
            f"volume={self.volume!r}",
            f"issue={self.issue!r}",
            f"article_number={self.article_number!r}",
            f"page_start={self.page_start!r}",
            f"page_end={self.page_end!r}",
            f"page_count={self.page_count!r}",
            f"issn={self.issn!r}",
            f"isbn={self.isbn!r}",
            f"coden={self.coden!r}",
            f"pubmed_id={self.pubmed_id!r}",
            f"eid={self.eid!r}",
            f"doi={self.doi!r}",
            f"link={self.link!r}",
            f"cited_by={self.cited_by!r}",
            f"author_keywords={self.author_keywords!r}",
            f"index_keywords={self.index_keywords!r}",
            f"affiliations={self.affiliations!r}",
            f"editors={self.editors!r}",
            f"sponsors={self.sponsors!r}",
            f"correspondence_address={self.correspondence_address!r}",
            f"publisher={self.publisher!r}",
            f"language_of_orig_doc={self.language_of_orig_doc!r}",
            f"tradenames={self.tradenames!r}",
            f"manufacturers={self.manufacturers!r}",
            f"funding_details={self.funding_details!r}",
            f"funding_texts={self.funding_texts!r}",
            f"references={self.references!r}",
            f"abstract={self.abstract!r}",
            f"source={self.source!r}"
        ]
        return "\n".join(lines)
