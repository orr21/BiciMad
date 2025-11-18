import re
import pytest
from io import BytesIO, TextIOWrapper
from zipfile import ZipFile

from unittest.mock import patch, Mock

from bicimad import UrlEMT

HTML = '''
<html>
  <body>
    <a href="file1.csv">CSV</a>
    <a href="trips_21_03_March-csv.aspx">March Trips</a>
    <a href="something_else.pdf">PDF</a>
  </body>
</html>
'''

@pytest.mark.parametrize("html, expected", [
    ('<a href="page.html">Link</a>', {'page.html'}),
    ('<a href="a.csv">A</a><a href="b.pdf">B</a>', {'a.csv', 'b.pdf'}),
    ('no links here', set()),
])
def test_get_links(html, expected):
    assert UrlEMT.get_links(html) == expected


@patch("requests.get")
def test_select_valid_urls(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = HTML

    urls = UrlEMT.select_valid_urls()
    assert any("trips_21_03_March-csv.aspx" in url for url in urls)
    assert all(url.startswith(UrlEMT.EMT) for url in urls)

@patch("requests.get")
def test_select_valid_urls_connection_error(mock_get):
    mock_get.return_value.status_code = 500
    with pytest.raises(ConnectionError, match="Could not access"):
        UrlEMT.select_valid_urls()

@patch("requests.get")
def test_get_url_valid(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = HTML

    emt = UrlEMT()
    url = emt.get_url(3, 21)
    assert url.endswith("trips_21_03_March-csv.aspx")

@pytest.mark.parametrize("month", [0, 13])
def test_get_url_invalid_month(month):
    emt = UrlEMT()
    with pytest.raises(ValueError, match="Invalid month"):
        emt.get_url(month, 21)

@pytest.mark.parametrize("year", [20, 24])
def test_get_url_invalid_year(year):
    emt = UrlEMT()
    with pytest.raises(ValueError, match="Invalid year"):
        emt.get_url(3, year)

@patch("requests.get")
def test_get_url_not_found(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = '<a href="some_file.aspx"></a>'

    emt = UrlEMT()
    with pytest.raises(ValueError, match="No valid link found"):
        emt.get_url(3, 21)

@patch("requests.get")
def test_get_csv(mock_get):
    mem_zip = BytesIO()
    with ZipFile(mem_zip, mode="w") as zf:
        zf.writestr("fake.csv", "col1,col2\n1,2")

    mem_zip.seek(0)

    mock_get.side_effect = [
        Mock(status_code=200, text='<a href="trips_21_03_March-csv.aspx">'),
        Mock(status_code=200, content=mem_zip.read())
    ]

    emt = UrlEMT()
    file = emt.get_csv(3, 21)
    assert isinstance(file, TextIOWrapper)
    assert "col1" in file.readline()

@patch("requests.get")
def test_get_csv_connection_error(mock_get):
    mock_get.side_effect = [
        Mock(status_code=200, text='<a href="trips_21_03_March-csv.aspx">'),
        Mock(status_code=404)
    ]

    emt = UrlEMT()
    with pytest.raises(ConnectionError, match="Failed to download the file"):
        emt.get_csv(3, 21)