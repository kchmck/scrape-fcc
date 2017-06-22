import re
import functools

def dms_to_dec(dms, card):
    SIGNS = {
        "N": +1,
        "S": -1,
        "E": +1,
        "W": -1,
    }

    deg, min, sec = (float(n) for n in dms.split("-"))
    return SIGNS[card] * (deg + min / 60 + sec / 3600)

class ULSLatLongParser:
    def __init__(self, str):
        lat, long = str.split(", ")
        self.lat = self.parse(lat)
        self.long = self.parse(long)

    def parse(self, str):
        dms, card = str.split(" ")
        return dms_to_dec(dms, card)

class ASRLatLongParser:
    def __init__(self, str):
        lat, long = str.split(" ")
        self.lat = self.parse(lat)
        self.long = self.parse(long)

    def parse(self, str):
        return dms_to_dec(str[:-1], str[-1])

class Table:
    def __init__(self, node):
        self.cols = node.find_all("td")

    def __getitem__(self, regex):
        for title, val in zip(self.cols, self.cols[1:]):
            if re.search(regex, title.text):
                return val

class ColMap:
    def __init__(self, heading):
        self.cols = heading.find_all("td")

    @functools.lru_cache()
    def __getitem__(self, label):
        for i, col in enumerate(self.cols):
            if re.search(label, col.text):
                return i

        raise KeyError

def clean(str):
    return re.sub("\s+", " ", str.strip())

def county_code(text, state, county):
    return re.search('"(\d+):{}-{}"'.format(state, county), text).group(1)

def parse_fkey(link):
    return int(re.search("keyFreq=(\d+)", link).group(1))

def parse_lkey(link):
    return int(re.search("keyLoc=(\d+)", link).group(1))

