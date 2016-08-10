import bs4
import requests
import urllib.parse

import urls
import utils

class ULSRecords:
    def __init__(self, state, county):
        self.state = state
        self.county = county

    def __iter__(self):
        req = requests.get(urls.GEO_SEARCH)

        headers = {
            "Cookie": req.headers["set-cookie"],
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": urls.GEO_SEARCH,
        }

        req = requests.post(urls.RESULTS, headers=headers, data={
            "ulsState": self.state,
            "ulsCounty": utils.county_code(req.text, self.state, self.county),
            "hiddenForm": "hiddenForm",
        })

        while True:
            soup = bs4.BeautifulSoup(req.text, "html.parser")
            table = soup.select("table[summary~=License]")[0]

            for row in table.select("tr")[1:-1]:
                cells = row.find_all("td")
                link = cells[1].find_all("a")[0]
                service = cells[4].text.strip()
                status = cells[5].text.strip().lower()

                yield ULSRecord(parse_url(link["href"]), service, status)

            try:
                next = soup.select("[title~=Next]")[0]
            except IndexError:
                return

            req = requests.get("/".join((urls.SEARCH, next["href"])),
                headers=headers)

class ULSRecord:
    def __init__(self, rkey, service, status):
        self.rkey = rkey
        self.service = service
        self.status = status

    def insert(self, cursor):
        cursor.execute(
            """
            insert into records values (
                ?,
                ?,
                ?
            )
            """,
            (
                self.rkey,
                self.service,
                self.status,
            )
        )

def parse_url(str):
    parts = urllib.parse.urlparse(str)
    query = urllib.parse.parse_qs(parts.query)

    return int(query["licKey"][0])
