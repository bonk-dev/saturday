import csv

from fetcher.scopus_batch.parser_models import Publication


class ScopusCsvParser:
    def __init__(self, text_data: str):
        # TODO: Find a more elegant solution for handling BOM?
        self._lines = text_data.removeprefix('\ufeff').splitlines()

    @staticmethod
    def _split_cell(cell: str) -> list:
        if not cell or len(cell) <= 0:
            return []
        return [cv.strip() for cv in cell.split(';')]

    def read_all_publications(self) -> list:
        publications = []

        reader = csv.reader(self._lines)
        expected_header_row = ['Authors', 'Author full names', 'Author(s) ID', 'Title', 'Year', 'Source title',
                               'Volume', 'Issue', 'Art. No.', 'Page start', 'Page end', 'Page count', 'Cited by', 'DOI',
                               'Link', 'Affiliations', 'Authors with affiliations', 'Abstract', 'Author Keywords',
                               'Index Keywords', 'Molecular Sequence Numbers', 'Chemicals/CAS', 'Tradenames',
                               'Manufacturers', 'Funding Details', 'Funding Texts', 'References',
                               'Correspondence Address', 'Editors', 'Publisher', 'Sponsors', 'Conference name',
                               'Conference date', 'Conference location', 'Conference code', 'ISSN', 'ISBN', 'CODEN',
                               'PubMed ID', 'Language of Original Document', 'Abbreviated Source Title',
                               'Document Type', 'Publication Stage', 'Open Access', 'Source', 'EID']
        actual_header_row = next(reader)
        print(actual_header_row)
        if actual_header_row != expected_header_row:
            raise ValueError('The actual CSV header row does not match the expected header row.')

        for row in reader:
            (_, authors, _, title, year, source_title, volume, issue, article_number, page_start,
             page_end, page_count, cited_by, doi, link, affiliations, _, abstract, author_keywords,
             index_keywords, _, _, tradenames, manufacturers, funding_details, funding_texts, references,
             correspondence_address, editors, publisher, sponsors, _, _, _, _, issn, isbn, coden, pubmed_id,
             language_of_orig_doc, abbr_source_title, document_type, publication_stage, open_access, source, eid) = row

            authors = self._split_cell(authors)
            affiliations = self._split_cell(affiliations)
            author_keywords = self._split_cell(author_keywords)
            index_keywords = self._split_cell(index_keywords)
            tradenames = self._split_cell(tradenames)
            manufacturers = self._split_cell(manufacturers)
            # TODO: References (also separated by ';', each ref might contain ';' inside the name)
            editors = self._split_cell(editors.strip())
            sponsors = self._split_cell(sponsors.strip())
            open_access = self._split_cell(open_access)

            publications.append(Publication(
                authors=authors,
                title=title,
                year=year,
                source_title=source_title,
                volume=volume,
                issue=issue,
                article_number=article_number,
                page_start=page_start,
                page_end=page_end,
                page_count=page_count,
                cited_by=cited_by,
                doi=doi,
                link=link,
                abstract=abstract,
                funding_details=funding_details,
                funding_texts=funding_texts,
                references=references,
                correspondence_address=correspondence_address,
                publisher=publisher,
                issn=issn,
                isbn=isbn,
                coden=coden,
                pubmed_id=pubmed_id,
                language_of_orig_doc=language_of_orig_doc,
                abbr_source_title=abbr_source_title,
                document_type=document_type,
                publication_stage=publication_stage,
                source=source,
                eid=eid,

                affiliations=affiliations,
                author_keywords=author_keywords,
                index_keywords=index_keywords,
                tradenames=tradenames,
                manufacturers=manufacturers,
                editors=editors,
                sponsors=sponsors,
                open_access=open_access,
            ))

        return publications
