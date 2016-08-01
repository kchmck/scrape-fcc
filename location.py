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
            except IndexError:
                return

class DefaultLocation:
    def __init__(self, rkey, cols, map):
        loc = cols[map["Location"]]

        self.rkey = rkey
        self.lkey = utils.parse_lkey(loc.find("a")["href"])
        self.type = parse_type(loc.text.strip())
        self.desc = cols[map["Transmitter Address"]].text.strip()

        coords = utils.LatLongParser(
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

class LocationTableError(Exception):
    pass

class LocationTable:
    def __init__(self, table):
        tab = utils.Table(table)

        coords = tab["Coordinates"]

        if not coords:
            raise LocationTableError

        self.desc = utils.clean(coords.find_previous_siblings("td")[1].text)

        try:
            coords = utils.LatLongParser(coords.text.strip())
        except ValueError:
            raise LocationTableError

        self.latitude = coords.lat
        self.longitude = coords.long

class PTPLocations:
    def __init__(self, rkey):
        self.rkey = rkey

    def __iter__(self):
        req = requests.get(urls.LOCS, params={"licKey": self.rkey})

        while True:
            soup = bs4.BeautifulSoup(req.text, "html.parser")

            main = soup.select("table[summary~=graphical] table[summary~=graphical]")[1]
            others = soup.select("table[summary~=Locations]")[1:-1]

            try:
                yield PTPLocation(main)
            except LocationTableError:
                return

            for table in others:
                try:
                    yield PTPLocation(table)
                except LocationTableError:
                    pass

            nav = soup.select("table[summary~=Locations]")[0]
            next = nav.select("a[title~=Next]")

            try:
                req = requests.get("/".join((urls.SEARCH, next[0]["href"])))
            except IndexError:
                return

class PTPLocation(LocationTable):
    def __init__(self, table):
        super().__init__(table)

    def insert(self, cursor):
        cursor.execute(
            """
            insert into locations values (
                null,
                ?,
                "microwave",
                ?,
                ?,
                ?
            )
            """,
            (
                rid,
                self.desc,
                self.latitude,
                self.longitude,
            )
        )

class NNLocations:
    def __init__(self, rkey):
        self.rkey = rkey

    def __iter__(self):
        req = requests.get(urls.LOCS, params={"licKey": self.rkey})

        while True:
            soup = bs4.BeautifulSoup(req.text, "html.parser")

            table = soup.select("table[summary~=graphical]")[3]
            table = table.find_all("table")[3]

            rows = table.find_all("tr")
            map = utils.ColMap(rows[0])

            for row in rows[1:-1]:
                cols = row.find_all("td")

                try:
                    yield NNLocation(cols, map)
                except IndexError:
                    pass

            nav = soup.select("table[summary~=Location]")[0]
            next = nav.select("a[title~=Next]")

            try:
                req = requests.get("/".join((urls.SEARCH, next[0]["href"])))
            except IndexError:
                return

class NNLocation:
    def __init__(self, cols, map):
        col = cols[map["Latitude,Longitude"] + 1]
        coords = utils.LatLongParser(col.text.strip())

        self.latitude = coords.lat
        self.longitude = coords.long

    def insert(self, cursor, rid):
        cursor.execute(
            """
            insert into locations values (
                null,
                ?,
                "microwave",
                null,
                ?,
                ?
            )
            """,
            (
                rid,
                self.latitude,
                self.longitude,
            )
        )
