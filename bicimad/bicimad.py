import re

import pandas as pd

from .urlemt import UrlEMT

class BiciMad:
    __COLUMNS = [
        'idBike', 'fleet', 'trip_minutes', 'geolocation_unlock', 'address_unlock', 'unlock_date', 'locktype', 
        'unlocktype', 'geolocation_lock', 'address_lock', 'lock_date', 'station_unlock', 
        'unlock_station_name', 'station_lock', 'lock_station_name'
    ]

    def __init__(self, month: int, year: int):
        self.__month = month
        self.__year = year
        self.__data = self.get_data(month, year)

    @staticmethod
    def get_data(month: int, year: int) -> pd.DataFrame:
        '''
        Loads BiciMad trip data for a given month and year as a pandas DataFrame.

        :param month: integer from 1 to 12
        :param year: two-digit year, between 21 and 23
        :returns: a pandas DataFrame with parsed trip data indexed by unlock date
        :raises ValueError: if month/year are invalid or file is not found

        Examples
        --------
        >>> df = BiciMad.get_data(5, 22)
        >>> df.columns
        Index([...])

        >>> BiciMad.get_data(0, 22)
        Traceback (most recent call last):
            ...
        ValueError: Invalid month. Must be between 1 and 12.
        '''
        return pd.read_csv(
            UrlEMT().get_csv(month, year),
            sep=';',
            usecols=BiciMad.__COLUMNS,
            index_col='unlock_date',
            parse_dates=['unlock_date', 'lock_date']
        )
    @property
    def data(self) -> pd.DataFrame:
        '''
        Returns the trip data for the initialized month and year.

        :returns: pandas DataFrame containing the BiciMad trips
        '''
        return self.__data

    def __str__(self) -> str:
        '''
        Returns a string representation of the dataset.

        :returns: a string with the formatted DataFrame content

        Examples
        --------
        >>> b = BiciMad(5, 22)
        >>> str(b).startswith(' idBike')
        True
        '''
        return self.__data.to_string()

    def clean(self) -> None:
        '''
        Cleans the dataset in-place by:
        - Removing fully empty rows
        - Converting specified columns to string type

        :returns: None (modifies the internal DataFrame)

        Examples
        --------
        >>> b = BiciMad(5, 22)
        >>> b.clean()
        >>> b.data.isnull().all(axis=1).any()
        False
        '''
        self.__data.dropna(how='all', inplace=True)

        for col in ['fleet', 'idBike', 'station_lock', 'station_unlock']:
            self.__data[col] = self.__data[col].map(lambda x: str(int(x)) if pd.notna(x) and isinstance(x, (int, float)) else re.sub(r'[a-zA-Z]', '', str(x)) if pd.notna(x) else x)

    def resume(self) -> pd.Series:
        '''
        Summarizes key statistics from the trip data.

        :returns: pandas Series with the following:
          - year: the year of the dataset
          - month: the month of the dataset
          - total_uses: total number of trips
          - total_time: total trip time in hours
          - most_popular_station: list of station(s) with the most unlocks
          - uses_from_most_popular: number of uses from those stations

        Examples
        --------
        >>> b = BiciMad(5, 22)
        >>> b.resume()
            year                                                 22
            month                                                 5
            total_uses                                       955868
            total_time                                    160258.01
            most_popular_station      {'Plaza de la Cebada nº 16 '}
            uses_from_most_popular                             3553
            dtype: object
        '''
        return pd.Series({
            'year': self.__year,
            'month': self.__month,
            'total_uses': self.total_uses(),
            'total_time': self.total_time(),
            'most_popular_station': self.most_popular_stations(),
            'uses_from_most_popular': self.usage_from_most_popular_station()
        })
    
    def total_uses(self) -> int:
        '''
        Calculates the total number of trips in the dataset.

        :returns: integer representing the number of rows/trips

        Examples
        --------
        >>> b = BiciMad(5, 22)
        >>> b.total_uses()
        955868
        '''
        return len(self.__data)
    
    def total_time(self):
        '''
        Computes the total duration of all trips in hours.

        :returns: float representing the total trip time in hours

        Examples
        --------
        >>> b = BiciMad(5, 22)
        >>> b.total_time()
        160258.01
        '''    
        return self.__data['trip_minutes'].sum() / 60
    
    def most_popular_stations(self):
        '''
        Identifies the address(es) of the station(s) with the most unlocks.

        :returns: set of station address(es) with the highest number of unlocks

        Examples
        --------
        >>> b = BiciMad(5, 22)
        >>> b.most_popular_stations()
        {'Plaza de la Cebada nº 16 '}
        '''
        df = self.__data.copy()

        counts = df.groupby(["station_unlock", "address_unlock"]).size()

        max_uses = counts.max()

        most_popular = counts[counts == max_uses].index.get_level_values("address_unlock")

        return set(most_popular)
    
    def usage_from_most_popular_station(self):
        '''
        Returns the number of trips from the most popular unlock station(s).

        :returns: integer with the number of uses from the most used unlock station(s)

        Examples
        --------
        >>> b = BiciMad(5, 22)
        >>> b.usage_from_most_popular_station()
        3553
        '''
        df = self.__data.copy()

        station_counts = df.groupby("station_unlock").size()

        max_usage = station_counts.max()

        return int(max_usage)
