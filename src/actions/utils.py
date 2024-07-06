import re

def extract_urls(text):
    url_pattern = r"(https?://[^\s]+)"
    urls = re.findall(url_pattern, text)
    return urls


def extract_document_id(url):
    pattern = r"/d/([^/]+)/"
    match = re.search(pattern, url)
    if match:
        document_id = match.group(1)
        return document_id
    else:
        return None
    
def extract_id_from_message(url):
    urls = extract_urls(url)
    ids = list(filter(lambda x: x is not None, [extract_document_id(url) for url in urls]))

    if len(ids) == 1:
        return ids[0]
    return None