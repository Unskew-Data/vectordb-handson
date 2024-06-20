import os
import json
from typing import List
from html.parser import HTMLParser
from atlassian import Confluence

from dotenv import load_dotenv

load_dotenv()


class TagStripper(HTMLParser):
    text: List[str]
    strict: bool

    def __init__(self, *, convert_charrefs: bool = True) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.reset()
        self.strict = False
        self.text = []

    def handle_data(self, data: str) -> None:
        self.text.append(data)

    def get_data(self):
        return "".join(self.text)

    def strip_tags(self, html: str):
        self.feed(html)
        return self.get_data()


def get_pages(space: str, ancestor: int = 270073934):

    url = os.getenv("CONFLUENCE_URL")

    confluence = Confluence(
        url=url,
        username=os.getenv("CONFLUENCE_USERNAME"),
        password=os.getenv("CONFLUENCE_PAT"),
    )
    confluence.verify_ssl = False
    stripper = TagStripper()

    pages = []

    cql_query = f"space = '{space}' and type = page and ancestor = {ancestor}"

    content = confluence.cql(cql_query, expand="space", start=0, limit=200)

    page_ids = [x["content"]["id"] for x in content["results"]]

    for page in page_ids:
        content = confluence.get_page_by_id(page, expand="body.storage")
        pages.append(
            {
                "id": int(page),
                "space": space,
                "url": f"{url}/wiki/spaces/{space}/pages/{page}/{content['title'].replace(' ', '+')}",
                "content": stripper.strip_tags(content["body"]["storage"]["value"]),
            }
        )

    return pages


if __name__ == "__main__":
    pages = get_pages("NEWS")

    with open("../../data/confluence.json", "w") as f:
        for page in pages:
            json.dump(page, f)
            f.write("\n")
