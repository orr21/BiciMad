# BiciMAD Data Analysis Package

A Python package for retrieving, cleaning, and analyzing BiciMAD trip data from EMT Madrid's open data portal.

## Overview

BiciMAD is Madrid's public bicycle sharing system operated by EMT Madrid. This package provides tools to download historical trip data, clean it, and perform various analyses on bicycle usage patterns in Madrid.

## Features

- **Automated Data Retrieval**: Download BiciMAD trip data directly from EMT Madrid's open data portal
- **Data Cleaning**: Remove invalid entries and standardize data types
- **Statistical Analysis**: Calculate total usage, trip duration, and identify popular stations
- **Flexible Date Range**: Access data from 2021 to 2023 by month
- **Pandas Integration**: All data is returned as pandas DataFrames for easy manipulation

## Installation

### Prerequisites

- Python 3.12 or higher
- pip package manager

### Install from source

```bash
pip install .
```

### Install dependencies only

```bash
pip install pandas requests
```

## Data Source

This package retrieves data from [EMT Madrid's Open Data Portal](https://opendata.emtmadrid.es), specifically from the BiciMAD trip datasets. The data includes:

- Bike ID and fleet information
- Trip duration
- Unlock and lock locations (coordinates and addresses)
- Station information
- Timestamps for trip start and end

## Project Structure

```
bicimad/
├── bicimad/
│   ├── __init__.py       # Package initialization
│   ├── bicimad.py        # Main BiciMad class for data analysis
│   └── urlemt.py         # UrlEMT class for data retrieval
├── tests/
│   ├── test_bicimad.py   # Tests for BiciMad class
│   └── test_urlemt.py    # Tests for UrlEMT class
├── bicimad.ipynb         # Jupyter notebook with analysis examples
├── bicimad-1.0.0-py3-none-any.whl # Package wheel
├── pyproject.toml        # Package configuration
└── README.md             # This file
```

## API Reference

### BiciMad Class

#### Constructor
```python
BiciMad(month: int, year: int)
```
- `month`: Integer from 1 to 12
- `year`: Two-digit year (21-23)

#### Methods

- `clean()`: Remove invalid rows and standardize column types
- `resume()`: Get a summary with key statistics
- `total_uses()`: Return total number of trips
- `total_time()`: Return total trip duration in hours
- `most_popular_stations()`: Return set of most popular unlock stations
- `usage_from_most_popular_station()`: Return usage count from most popular station

#### Properties

- `data`: Access the underlying pandas DataFrame

### UrlEMT Class

#### Methods

- `get_url(month: int, year: int)`: Get the download URL for a specific month/year
- `get_csv(month: int, year: int)`: Download and return CSV file as TextIOWrapper
- `get_links(html: str)`: Extract all links from HTML (static method)
- `select_valid_urls()`: Scrape EMT website for valid trip file URLs (static method)

## Examples

### Basic Usage

```python
from bicimad import BiciMad

# Load data for May 2022
bike_data = BiciMad(month=5, year=22)

# Clean the data
bike_data.clean()

# Get a summary of the data
summary = bike_data.resume()
print(summary)
```

### Working with the DataFrame

```python
# Access the raw DataFrame
df = bike_data.data

# Get specific information
total_trips = bike_data.total_uses()
total_hours = bike_data.total_time()
popular_stations = bike_data.most_popular_stations()
```

### Analyzing February 2023 Data

```python
from bicimad import BiciMad

# Load February 2023 data
feb_data = BiciMad(2, 23)
feb_data.clean()

# Get summary statistics
summary = feb_data.resume()
print(f"Total trips: {summary['total_uses']}")
print(f"Total hours: {summary['total_time']:.2f}")
print(f"Most popular stations: {summary['most_popular_station']}")
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Building the Package

```bash
python -m build
```

## License

This project is provided as-is for educational and analytical purposes.

## Author

Óscar Rico Rodríguez

## Acknowledgments

- Data provided by [EMT Madrid](https://www.emtmadrid.es/)