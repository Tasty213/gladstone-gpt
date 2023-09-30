import re

from requests import get
from bs4 import BeautifulSoup


DEFAULT_DETAILS = """Unable to identify details of local liberal democrats. 
Federal party can be contacted by filling out the form at https://www.libdems.org.uk/contact"""

LOCAL_PARTY_DETAILS_CSS_SELECTOR = "div.sub-block:nth-child(1)"
POSTCODE_NOT_FOUND_CSS_SELECTOR = "h2.text-red-600"


def get_local_party_details(postcode: str):
    response = get(
        "https://www.libdems.org.uk/in-your-community", params={"postcode": postcode}
    )
    if response.status_code > 299:
        return DEFAULT_DETAILS

    soup = BeautifulSoup(response.content)

    if len(soup.select(POSTCODE_NOT_FOUND_CSS_SELECTOR)) > 0:
        return DEFAULT_DETAILS

    details = "".join([result.text for result in soup.select(LOCAL_PARTY_DETAILS_CSS_SELECTOR)])

    details_stripped = re.sub(r'(\s{2,})', "\n", details)

    return re.sub(r'Local party area.+', "", details_stripped, flags=re.MULTILINE | re.DOTALL)
