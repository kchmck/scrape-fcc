### Building

Using [virtualenv](https://virtualenv.pypa.io/en/stable/installation/) and
[pip](https://pip.pypa.io/en/stable/installing/),

1. Clone the repo:

    ```sh
    git clone https://github.com/kchmck/scrape-fcc.git
    cd scrape-fcc
    ```

2. Create and activate a new environment:

    ```sh
    virtualenv -p python3 .venv
    source .venv/bin/activate
    ```

4. Install dependencies:

    ```sh
    pip install -r requirements.txt
    ```

Then you should be set to run `./scrape-fcc`!

### Scrape ULS Radio Licenses

Licenses are scraped by state and county, specified by the `-S` and `-C`
options, respectively (the state should be given as its two-letter
abbreviation.) Additionally, an sqlite database must be specified to write the
licenses into using `-d`.

First, do an initial "quick" scrape of all known licenses using `-I`. For
example,

```sh
./scrape-fcc -S oh -C athens -d records.db -I
```

Then, scrape the rest of the details with `-U`. For example,

```sh
./scrape-fcc -S oh -C athens -d records.db -U
```

Only active, non-microwave licenses are fully scraped, and licenses already in
the database aren't scraped again. Scraped information includes

- callsign and descriptive information
- associated frequencies and emission designators
- locations of transmitters (latitude and longitude)

See the [schema](https://github.com/kchmck/scrape-fcc/blob/master/sql.py) for
the complete picture.

All of the information associated with a license is saved to the database
atomically, so if a network error occurs while scraping a license, it won't be
stored in a half-correct state. To speed up scraping after an error, use the
`-L` option and pass the ID of a record previously printed to the console.

### Scrape ASR Radio Tower Licenses

Information on tower locations is scraped with `-A` along with the same `-S`,
`-C`, and `-d` options described in the previous section. For example,

```sh
./scrape-fcc -S oh -C athens -d records.db -A
```
