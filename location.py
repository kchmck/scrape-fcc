import bs4
import re
import requests
import urllib.parse

import urls
import utils

class DefaultLocations:
    def __init__(self, rkey):
        self.rkey = rkey

    def __iter__(self):
        req = requests.get(urls.LOCS, params={"licKey": self.rkey})
        req.raise_for_status()

        while True:
            soup = bs4.BeautifulSoup(req.text, "html.parser")
            table = soup.select("table[summary~=graphical]")[3]
            table = table.find_all("table")[4]

            rows = table.find_all("tr")
            map = utils.ColMap(rows[0])

            for row in rows[1:]:
                cols = row.find_all("td")

                try:
                    yield DefaultLocation(self.rkey, cols, map)
                except ValueError:
                    pass

            nav = soup.select("table[summary~=Locations]")[0]
            next = nav.select("a[title~=Next]")

            try:
                req = requests.get("/".join((urls.SEARCH, next[0]["href"])))
                req.raise_for_status()
            except IndexError:
                return

class DefaultLocation:
    def __init__(self, rkey, cols, map):
        loc = cols[map["Location"]]

        self.rkey = rkey
        self.lkey = utils.parse_lkey(loc.find("a")["href"])
        self.type = parse_type(loc.text.strip())
        self.desc = cols[map["Transmitter Address"]].text.strip()

        coords = utils.ULSLatLongParser(
            cols[map["Latitude, Longitude"]].text.strip())
        self.latitude = coords.lat
        self.longitude = coords.long

    def insert(self, cursor):
        cursor.execute(
            """
            insert into locations values (
                null,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            (
                self.rkey,
                self.lkey,
                self.type,
                self.desc,
                self.latitude,
                self.longitude,
            )
        )

def parse_type(str):
    return re.search("^\d+\s+-\s+(.+)$", str).group(1).lower()
