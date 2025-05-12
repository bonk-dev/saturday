from enum import Enum


class SearchEidsResultResponseData:
    num_found: int
    docs: list[str]

    def __init__(self, num_found: int, docs: list[str]):
        self.num_found = num_found
        self.docs = docs


class SearchEidsResult:
    response: SearchEidsResultResponseData

    def __init__(self, json_data: dict):
        self.response = SearchEidsResultResponseData(
            num_found=json_data['response']['numFound'],
            docs=json_data['response']['docs'])


class ExportFileType(Enum):
    CSV = "CSV"
    RIS = "RIS"
    BIBTEX = "BIBTEX"
    PLAIN_TEXT = "PLAIN_TEXT"


class FieldGroupIdentifiers(Enum):
    AUTHORS = "authors"
    TITLES = "titles"
    YEAR = "year"
    EID = "eid"
    SOURCE_TITLE = "sourceTitle"
    VOLUME_ISSUE_PAGES = "volumeIssuePages"
    CITED_BY = "citedBy"
    SOURCE = "source"
    DOCUMENT_TYPE = "documentType"
    PUBLICATION_STAGE = "publicationStage"
    DOI = "doi"
    OPEN_ACCESS = "openAccess"
    AFFILIATIONS = "affiliations"
    SERIAL_IDENTIFIERS = "serialIdentifiers"
    PUB_MED_ID = "pubMedId"
    PUBLISHER = "publisher"
    EDITORS = "editors"
    ORIGINAL_LANGUAGE = "originalLanguage"
    CORRESPONDENCE_ADDRESS = "correspondenceAddress"
    ABBREVIATED_SOURCE_TITLE = "abbreviatedSourceTitle"
    ABSTRACT = "abstract"
    AUTHOR_KEYWORDS = "authorKeywords"
    INDEXED_KEYWORDS = "indexedKeywords"
    FUNDING_DETAILS = "fundingDetails"
    FUNDING_TEXTS = "fundingTexts"
    TRADENAMES_AND_MANUFACTURERS = "tradenamesAndManufacturers"
    ACCESSION_NUMBERS_AND_CHEMICALS = "accessionNumbersAndChemicals"
    CONFERENCE_INFORMATION = "conferenceInformation"
    REFERENCES = "references"


def all_identifiers() -> list[FieldGroupIdentifiers]:
    return [
        FieldGroupIdentifiers.AUTHORS,
        FieldGroupIdentifiers.TITLES,
        FieldGroupIdentifiers.YEAR,
        FieldGroupIdentifiers.EID,
        FieldGroupIdentifiers.SOURCE_TITLE,
        FieldGroupIdentifiers.VOLUME_ISSUE_PAGES,
        FieldGroupIdentifiers.CITED_BY,
        FieldGroupIdentifiers.SOURCE,
        FieldGroupIdentifiers.DOCUMENT_TYPE,
        FieldGroupIdentifiers.PUBLICATION_STAGE,
        FieldGroupIdentifiers.DOI,
        FieldGroupIdentifiers.OPEN_ACCESS,
        FieldGroupIdentifiers.AFFILIATIONS,
        FieldGroupIdentifiers.SERIAL_IDENTIFIERS,
        FieldGroupIdentifiers.PUB_MED_ID,
        FieldGroupIdentifiers.PUBLISHER,
        FieldGroupIdentifiers.EDITORS,
        FieldGroupIdentifiers.ORIGINAL_LANGUAGE,
        FieldGroupIdentifiers.CORRESPONDENCE_ADDRESS,
        FieldGroupIdentifiers.ABBREVIATED_SOURCE_TITLE,
        FieldGroupIdentifiers.ABSTRACT,
        FieldGroupIdentifiers.AUTHOR_KEYWORDS,
        FieldGroupIdentifiers.INDEXED_KEYWORDS,
        FieldGroupIdentifiers.FUNDING_DETAILS,
        FieldGroupIdentifiers.FUNDING_TEXTS,
        FieldGroupIdentifiers.TRADENAMES_AND_MANUFACTURERS,
        FieldGroupIdentifiers.ACCESSION_NUMBERS_AND_CHEMICALS,
        FieldGroupIdentifiers.CONFERENCE_INFORMATION,
        FieldGroupIdentifiers.REFERENCES
    ]