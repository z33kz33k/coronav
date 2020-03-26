"""

    coronav.py
    ~~~~~~~~~~~~~

    Scrape https://www.worldometers.info/coronavirus/ for data on coronavirus.

"""

from dataclasses import dataclass
from pathlib import Path
from typing import List

import requests
from bs4 import BeautifulSoup


URL = "https://www.worldometers.info/coronavirus/"


@dataclass
class DataRow:
    """A row of scraped data.
    """
    country: str
    total_cases: int
    new_cases: int
    total_deaths: int
    new_deaths: int
    total_recovered: int
    active_cases: int
    serious_cases: int
    total_cases_per_million: float
    total_deaths_per_million: float

    @property
    def hot_index(self) -> float:
        """Healthcare On Top Index - that is total cases / total deaths
        """

        return self.total_cases / self.total_deaths if self.total_deaths != 0 else 0

    @property
    def hot_index_str(self) -> str:
        """HOT index string-formatted.
        """
        return f"{self.hot_index:.1f}"


def strip_unneeded(text: str) -> str:
    """Get rid of unneeded characters in text and return it.
    """
    text = text.strip().replace("+", "").replace(",", "").replace(" ", "")
    if not text:
        text = "0"
    return text


def make_datarow(data: List[str]) -> DataRow:
    """Make a DataRow object from list of scraped data.
    """
    return DataRow(
        data[0],
        int(strip_unneeded(data[1])),
        int(strip_unneeded(data[2])),
        int(strip_unneeded(data[3])),
        int(strip_unneeded(data[4])),
        int(strip_unneeded(data[5])),
        int(strip_unneeded(data[6])),
        int(strip_unneeded(data[7])),
        float(strip_unneeded(data[8])),
        float(strip_unneeded(data[9]))
    )


content = requests.get(URL).text
bs = BeautifulSoup(content, "html5lib")
tables = bs.find_all("table", id="main_table_countries_today")
if len(tables) > 0:
    table = tables[0]
else:
    raise ValueError("Unexpected HTML structure.")
rows = [row for row in table.find_all("tr") if row.parent.name == "tbody"]
datarows = []
for row in rows:
    datarows.append(make_datarow([item.text for item in row.find_all("td")]))

sorted_datarows = sorted(datarows, key=lambda item: item.hot_index, reverse=True)

lines = ["HOT index for countries based on https://www.worldometers.info/coronavirus/:",
         "(Healthcare On Top = total cases / total deaths)"]
for i, dr in enumerate(sorted_datarows, start=1):
    lines.append(f"{i}. {dr.country}: {dr.hot_index_str}")

content = "\n".join(lines)
outputfile = Path("output/coronav.txt")
outputfile.write_text(content, encoding="utf-8")
print(content)


