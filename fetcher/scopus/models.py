class Author:
    def __init__(self, json_data):
        self.seq = json_data.get('@seq')
        self.author_url = json_data.get('author-url')
        self.authid = json_data.get('authid')
        self.authname = json_data.get('authname')
        self.surname = json_data.get('surname')
        self.given_name = json_data.get('given-name')
        self.initials = json_data.get('initials')
        self.afid = json_data.get('afid', [])

    def __str__(self):
        return f"{self.authname} ({self.authid})"

    def to_dict(self):
        return {
            "seq": self.seq,
            "author_url": self.author_url,
            "authid": self.authid,
            "authname": self.authname,
            "surname": self.surname,
            "given_name": self.given_name,
            "initials": self.initials,
            "afid": self.afid
        }


class Affiliation:
    def __init__(self, json_data):
        self.affiliation_url = json_data.get('affiliation-url')
        self.afid = json_data.get('afid')
        self.affilname = json_data.get('affilname')
        self.affiliation_city = json_data.get('affiliation-city')
        self.affiliation_country = json_data.get('affiliation-country')

    def __str__(self):
        return f"{self.affilname}, {self.affiliation_city}, {self.affiliation_country}"

    def to_dict(self):
        return {
            "affiliation_url": self.affiliation_url,
            "afid": self.afid,
            "affilname": self.affilname,
            "affiliation_city": self.affiliation_city,
            "affiliation_country": self.affiliation_country
        }


class Link:
    def __init__(self, json_data):
        self.ref = json_data.get('@ref')
        self.href = json_data.get('@href')

    def __str__(self):
        return f"{self.ref}: {self.href}"

    def to_dict(self):
        return {
            'ref': self.ref,
            'href': self.href
        }


class SearchEntry:
    def __init__(self, json_data):
        self.eid = json_data.get('eid')
        self.title = json_data.get('dc:title')
        self.creator = json_data.get('dc:creator')
        self.description = json_data.get('dc:description')
        self.identifier = json_data.get('dc:identifier')
        self.publication_name = json_data.get('prism:publicationName')
        self.issn = json_data.get('prism:issn')
        self.eissn = json_data.get('prism:eIssn')
        self.volume = json_data.get('prism:volume')
        self.issue = json_data.get('prism:issueIdentifier')
        self.page_range = json_data.get('prism:pageRange')
        self.cover_date = json_data.get('prism:coverDate')
        self.cover_display_date = json_data.get('prism:coverDisplayDate')
        self.doi = json_data.get('prism:doi')
        self.citedby_count = json_data.get('citedby-count')
        self.aggregation_type = json_data.get('prism:aggregationType')
        self.subtype = json_data.get('subtype')
        self.subtype_description = json_data.get('subtypeDescription')
        self.authkeywords = json_data.get('authkeywords', '').split(' | ') if json_data.get('authkeywords') else []
        self.article_number = json_data.get('article-number')
        self.source_id = json_data.get('source-id')
        self.openaccess = json_data.get('openaccess')
        self.openaccess_flag = json_data.get('openaccessFlag')
        self.freetoread = json_data.get('freetoread', {}).get('value', [])
        self.freetoread_label = json_data.get('freetoreadLabel', {}).get('value', [])
        self.fundNo = json_data.get('fund-no')
        self.fundAcr = json_data.get('fund-acr')
        self.fundSponsor = json_data.get('fund-sponsor')
        self.url = json_data.get('prism:url')

        self.links = [Link(link) for link in json_data.get('link', [])]
        self.affiliations = [Affiliation(affil) for affil in json_data.get('affiliation', [])]
        self.authors = [Author(author) for author in json_data.get('author', [])]

    def __str__(self):
        return f"{self.eid}: {self.title} by {self.creator} in {self.publication_name}"

    def to_dict(self):
        return {
            "eid": self.eid,
            "title": self.title,
            "creator": self.creator,
            "description": self.description,
            "identifier": self.identifier,
            "publication_name": self.publication_name,
            "issn": self.issn,
            "eissn": self.eissn,
            "volume": self.volume,
            "issue": self.issue,
            "page_range": self.page_range,
            "cover_date": self.cover_date,
            "cover_display_date": self.cover_display_date,
            "doi": self.doi,
            "citedby_count": self.citedby_count,
            "aggregation_type": self.aggregation_type,
            "subtype": self.subtype,
            "subtype_description": self.subtype_description,
            "authkeywords": self.authkeywords,
            "article_number": self.article_number,
            "source_id": self.source_id,
            "openaccess": self.openaccess,
            "openaccess_flag": self.openaccess_flag,
            "freetoread": self.freetoread,
            "freetoread_label": self.freetoread_label,
            "fundNo": self.fundNo,
            "fundAcr": self.fundAcr,
            "fundSponsor": self.fundSponsor,
            "url": self.url,
            "links": [link.to_dict() for link in self.links],
            "affiliations": [aff.to_dict() for aff in self.affiliations],
            "authors": [author.to_dict() for author in self.authors]
        }


class SearchResults:
    def __init__(self, json_data: dict):
        self.totalResults = int(json_data['search-results']['opensearch:totalResults'])
        self.startIndex = int(json_data['search-results']['opensearch:startIndex'])
        self.itemsPerPage = int(json_data['search-results']['opensearch:itemsPerPage'])

        self.entry = [SearchEntry(e) for e in json_data['search-results']['entry']]

    def __str__(self):
        s = f'Total: {self.totalResults}; index: {self.startIndex}, per page: {self.itemsPerPage} Entries: \n'
        for entry in self.entry:
            s += str(entry)
            s += '\n'
        return s

    def to_dict(self):
        return {
            'totalResults': self.totalResults,
            'startIndex': self.startIndex,
            'itemsPerPage': self.itemsPerPage,
            'entry': [e.to_dict() for e in self.entry]
        }

