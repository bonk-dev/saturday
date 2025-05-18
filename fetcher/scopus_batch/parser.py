import csv


class ScopusCsvParser:
    def __init__(self, text_data: str):
        # TODO: Find a more elegant solution for handling BOM?
        self._lines = text_data.removeprefix('\ufeff').splitlines()

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
            (_, authors_full_name_raw, _, title, year, source_title, volume, issue, article_number, page_start,
             page_end, page_count, cited_by, doi, link, affiliations_raw, _, abstract, author_keywords_raw,
             index_keywords, _, _, tradenames, manufacturers, funding_details, funding_texts, references,
             correspondence_address, editors, publisher, sponsors, _, _, _, _, issn, isbn, coden, pubmed_id,
             language_of_orig_doc, abbr_source_title, document_type, publication_stage, open_access, source, eid) = row

            print('=====================================================')
            print('authors_full_name_raw =', authors_full_name_raw)
            print('title =', title)
            print('year =', year)
            print('source_title =', source_title)
            print('volume =', volume)
            print('issue =', issue)
            print('article_number =', article_number)
            print('page_start =', page_start)
            print('page_end =', page_end)
            print('page_count =', page_count)
            print('cited_by =', cited_by)
            print('doi =', doi)
            print('link =', link)
            print('affilations_raw =', affiliations_raw)
            print('abstract =', abstract)
            print('author_keywords_raw =', author_keywords_raw)
            print('index_keywords =', index_keywords)
            print('tradenames =', tradenames)
            print('manufacturers =', manufacturers)
            print('funding_details =', funding_details)
            print('funding_texts =', funding_texts)
            print('references =', references)
            print('correspondence_address =', correspondence_address)
            print('editors =', editors)
            print('publisher =', publisher)
            print('sponsors =', sponsors)
            print('issn =', issn)
            print('isbn =', isbn)
            print('coden =', coden)
            print('pubmed_id =', pubmed_id)
            print('language_of_orig_doc =', language_of_orig_doc)
            print('abbr_source_title =', abbr_source_title)
            print('document_type =', document_type)
            print('publication_stage =', publication_stage)
            print('open_access =', open_access)
            print('source =', source)
            print('eid =', eid)
            print('=====================================================')

        return publications
