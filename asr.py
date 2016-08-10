import requests
import urllib.parse
import bs4

import utils
import urls

class ASRTowers:
    def __init__(self, state, county):
        self.state = state
        self.county = county

    def __iter__(self):
        req = requests.get(urls.ASR)

        headers = {
            "Cookie": req.headers["set-cookie"],
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": urls.ASR,
        }

        req = requests.post(urls.ASR_RESULTS, headers=headers, data={
            "asr_r_state": self.state,
            "asr_r_county": utils.county_code(req.text, self.state, self.county),
            "fiExactMatchInd": "N"
        })

        while True:
            soup = bs4.BeautifulSoup(req.text, "html.parser")
            table = soup.select("table[summary~=Search]")[0]

            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")

                if "Constructed" not in cols[2].text:
                    continue

                link = cols[1].find_all("a")[0]["href"]
                parts = urllib.parse.urlparse(link)
                query = urllib.parse.parse_qs(parts.query)
                coords = utils.ASRLatLongParser(cols[5].text.strip())

                yield ASRTower(query["regKey"][0], coords.lat, coords.long)

            try:
                next = soup.select("a[title~=Next]")[0]["href"]
            except IndexError:
                break

            req = requests.get("/".join((urls.ASR_SEARCH, next)), headers=headers)

class ASRTower:
    def __init__(self, tkey, lat, long):
        self.tkey = tkey
        self.lat = lat
        self.long = long

    def insert(self, cursor):
        cursor.execute(
            """
            insert into towers values (
                ?,
                ?,
                ?
            )
            """,
            (
                self.tkey,
                self.lat,
                self.long,
            )
        )
