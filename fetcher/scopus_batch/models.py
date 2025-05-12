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
