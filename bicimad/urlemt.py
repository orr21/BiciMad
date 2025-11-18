import re
from io import BytesIO, TextIOWrapper
from typing import Set
from zipfile import ZipFile
import calendar

import requests

class UrlEMT:
    EMT = 'https://opendata.emtmadrid.es'
    GENERAL = '/Datos-estaticos/Datos-generales-(1)'

    def __init__(self):
        self._valid_urls = UrlEMT.select_valid_urls()

    @staticmethod
    def get_links(html: str) -> Set[str]:
        '''
        Extracts all hyperlinks from a given HTML string.

        :param html: string representation of an HTML page
        :returns: a set containing all href links found in the HTML

        Examples
        --------
        >>> UrlEMT.get_links('<a href="page.html">Link</a>')
        {'page.html'}

        >>> UrlEMT.get_links('<a href="file.csv">CSV</a><a href="other.pdf">PDF</a>')
        {'file.csv', 'other.pdf'}

        >>> UrlEMT.get_links('no links here')
        set()
        '''
        pattern = r'href=[\'"]?([^\'" >]+)'
        links = re.findall(pattern, html)
        return set(links)

    def get_url(self, month: int, year: int) -> str:
        '''
        Returns the full URL for the CSV file of a given month and year.
    
        :param month: integer between 1 and 12
        :param year: two-digit year (e.g. 21 for 2021, 22 for 2022)
        :returns: a string with the full URL to the corresponding CSV download page
        :raises ValueError: if
          - month is not between 1 and 12
          - year is not between 21 and 23
          - no valid URL is found for the given month/year

        Examples
        --------
        >>> UrlEMT.get_url(1, 21)
        'https://opendata.emtmadrid.es/Datos-estaticos/Datos-generales-(1)/trips_21_01_January-csv.aspx'
        '''
        if not (1 <= month <= 12):
            raise ValueError("Invalid month. Must be between 1 and 12.")
        if not (21 <= year <= 23):
            raise ValueError("Invalid year. Must be between 21 and 23.")
    
        month_name = calendar.month_name[month]
        pattern = f"trips_{year:02d}_{month:02d}_{month_name}-csv.aspx"
    
        for url in self._valid_urls:
            if pattern in url:
                return url
    
        raise ValueError(f"No valid link found for {month:02d}/{year:02d}")
    
    def get_csv(self, month: int, year: int) -> TextIOWrapper:
        '''
        Downloads and returns a CSV file stream for a specific month and year.
    
        :param month: integer between 1 and 12
        :param year: two-digit year between 21 and 23
        :returns: a text stream (TextIOWrapper) of the CSV file
        :raises ConnectionError: if the download request fails (non-200 response)
        :raises ValueError: if the URL does not exist for the given date

        Examples
        --------
        >>> UrlEMT.get_csv(1, 21)
        '''
        url = self.get_url(month, year)
        response = requests.get(url)
        if response.status_code != 200:
            raise ConnectionError(f"Failed to download the file, status code: {response.status_code}")
    
        zipfile = ZipFile(BytesIO(response.content))
        csv_name = [f for f in zipfile.namelist() if f.endswith(".csv")][0]
        return TextIOWrapper(zipfile.open(csv_name), encoding="utf-8")
    
    @staticmethod
    def select_valid_urls() -> Set[str]:
        '''
        Scrapes the EMT Madrid website for links matching the valid trips file pattern.
    
        :returns: a set of full URLs to valid trip files
        :raises ConnectionError: if the request to the EMT page fails (non-200 response)

        Examples
        --------
        >>> UrlEMT.select_valid_urls()
        {'https://opendata.emtmadrid.es/Datos-estaticos/Datos-generales-(1)/trips_21_01_January-csv.aspx', ...}
        '''
        url = UrlEMT.EMT + UrlEMT.GENERAL
        response = requests.get(url)
        if response.status_code != 200:
            raise ConnectionError(f"Could not access {url}, status code: {response.status_code}")
    
        all_links = UrlEMT.get_links(response.text)
        valid_pattern = re.compile(r'trips_\d{2}_\d{2}_[\w\-]+\.aspx')
        valid_urls = {UrlEMT.EMT + link for link in all_links if valid_pattern.search(link)}
        return valid_urls