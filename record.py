import bs4
import requests

import freq
import location
import urls
import utils

INVALID = [
    "CN", "WS", "CW", "YD", "BC", "AW", "WU", "CZ", "QA", "TC", "AD", "BR",
    "ED", "PC", "LS", "YC", "YH", "TN", "WX", "MS", "CP", "WZ", "CJ", "BB",
    "BA", "WY", "CY", "GC", "AH", "TP", "CT",

    # These parse correctly, but are microwave so not really useful
    "CF", "MG", "MW", "NN", "PA", "RS", "TI", "TS", "AS", "CE", "AI", "LD",
]

class Record:
    def __init__(self, rkey):
        req = requests.get(urls.MAIN, params={"licKey": rkey})
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        title = soup.select("span[class=h2]")[0].text
        table = utils.Table(soup.select("table[summary~=License]")[0])

        self.rkey = rkey
        self.title = title
        self.callsign = table["Call Sign"].text.strip()
        self.service = table["Radio Service"].text.strip()[:2]
        self.status = table["Status"].text.strip().lower()

    def __bool__(self):
        return not self.service in INVALID

    def locs(self):
        return location.DefaultLocations(self.rkey)

    def freqs(self):
        return freq.Frequencies(self.rkey)

    def insert(self, cursor):
        cursor.execute(
            """
            insert into records values (
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            (
                self.rkey,
                self.title,
                self.callsign,
                self.status,
                self.service,
            )
        )
