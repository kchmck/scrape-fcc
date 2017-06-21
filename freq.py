import bs4
import re
import requests

import urls
import utils

class Frequencies:
    def __init__(self, rkey):
        self.rkey = rkey

    def __iter__(self):
        req = requests.get(urls.FREQS, params={"licKey": self.rkey})
        req.raise_for_status()

        while True:
            soup = bs4.BeautifulSoup(req.text, "html.parser")

            table = soup.select("table[summary~=graphical]")[3]
            table = table.find_all("table")[4]

            rows = table.find_all("tr")
            cmap = utils.ColMap(rows[0])

            for row in rows[1:]:
                yield Frequency(self.rkey, row, cmap)

            try:
                nav = soup.select("table[summary~=Locations]")[0]
                next = nav.select("a[title~=Next]")

                if not next:
                    return

                req = requests.get("/".join((urls.SEARCH, next[0]["href"])))
                req.raise_for_status()
            except IndexError:
                break

class Frequency:
    def __init__(self, rkey, row, cmap):
        cols = row.find_all("td")

        flink = cols[cmap["Frequency"]].find_all("a")[0]
        freq = flink.text.split(",")[0].split("-")[0]

        llink = cols[cmap["Loc#"]].find_all("a")[0]

        self.rkey = rkey
        self.fkey = utils.parse_fkey(flink["href"])
        self.lkey = utils.parse_lkey(llink["href"])
        self.freq = parse_freq(freq)

        op = cmap["Output\s*Power"]

        try:
            merp = cmap["Maximum\s*ERP"]
        except KeyError:
            merp = None

        self.power = calc_power(
            op and cols[op].text.strip(),
            merp and cols[merp].text.strip()
        )

    def emissions(self):
        return Emissions(self.rkey, self.fkey)

    def insert(self, cursor):
        cursor.execute(
            """
            insert into frequencies values (
                null,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            (
                self.rkey,
                self.fkey,
                self.lkey,
                self.freq,
                self.power,
            )
        )

class Emissions:
    def __init__(self, rkey, fkey):
        self.rkey = rkey
        self.fkey = fkey

    def __iter__(self):
        req = requests.get(urls.FREQ, params={
            "licKey": self.rkey,
            "keyFreq": self.fkey,
        })
        req.raise_for_status()

        soup = bs4.BeautifulSoup(req.text, "html.parser")
        cells = soup.findAll(text="FCC Admin Serial Number")

        for cell in cells:
            row = cell.parent.parent
            em = row.findAll("td")[0].text

            yield Emission(self.rkey, self.fkey, em.strip())

class Emission:
    def __init__(self, rkey, fkey, em):
        self.rkey = rkey
        self.fkey = fkey
        self.em = em

    def insert(self, cursor):
        cursor.execute(
            """
            insert into emissions values (
                null,
                ?,
                ?,
                ?
            )
            """,
            (
                self.rkey,
                self.fkey,
                self.em,
            )
        )

# Parses frequency into Hertz
def parse_freq(s):
    n, d = (int(x) for x in s.split("."))
    return n * 1000000 + d // 100

# Parses power into milliwatts
def parse_power(s):
    n, d = (int(x) for x in s.split("."))
    return n * 1000 + d

def calc_power(power, max_erp):
    if not power and not max_erp:
        return None

    if not power:
        return parse_power(max_erp)

    if not max_erp:
        return parse_power(power)

    return min(parse_power(power), parse_power(max_erp))
