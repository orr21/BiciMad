from io import StringIO

import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

from bicimad import BiciMad

FAKE_CSV = """idBike;fleet;trip_minutes;geolocation_unlock;address_unlock;unlock_date;locktype;unlocktype;geolocation_lock;address_lock;lock_date;station_unlock;unlock_station_name;station_lock;lock_station_name
6623.0;1.0;7.80;{'type': 'Point', 'coordinates': [-3.6877227, 40.4251002]};'Calle Serrano nº 34';2022-05-01 00:25:29;STATION;STATION;{'type': 'Point', 'coordinates': [-3.7020842, 40.4239757]};'Plaza de San Ildefonso';2022-05-01 00:33:17;111a;106a - Colón A;59.0;55 - Plaza de San Ildefonso
6031.0;1.0;20.28;{'type': 'Point', 'coordinates': [-3.6877227, 40.4251002]};'Calle Serrano nº 32';2022-05-01 00:25:33;STATION;STATION;{'type': 'Point', 'coordinates': [-3.7032777, 40.4535]};'Calle Navarra nº 1';2022-05-01 00:45:50;112;106a - Colón A;213.0;205 - Estrecho
6456.0;1.0;6.78;{'type': 'Point', 'coordinates': [-3.6877227, 40.4251002]};'Calle Serrano nº 34';2022-05-01 02:53:26;STATION;STATION;{'type': 'Point', 'coordinates': [-3.70239, 40.42059]};'Calle Desengaño nº 1';2022-05-01 03:00:13;112b;106a - Colón A;219.0;211 - Desengaño
876.0;1.0;1.63;{'type': 'Point', 'coordinates': [-3.6877227, 40.4251002]};'Calle Serrano nº 33';2022-05-01 06:36:21;STATION;STATION;{'type': 'Point', 'coordinates': [-3.6877227, 40.4251002]};'Calle Serrano nº 34';2022-05-01 06:37:59;111.0;106a - Colón A;111.0;106a - Colón A
;;;;;;;;;;;;;;
"""

@pytest.fixture
def mock_get_csv():
    """Mock para UrlEMT.get_csv que devuelve un CSV falso"""
    with patch("bicimad.bicimad.UrlEMT") as MockUrlEMT:
        mock_instance = MockUrlEMT.return_value
        mock_instance.get_csv.return_value = StringIO(FAKE_CSV)
        yield

def test_get_data(mock_get_csv):
    df = BiciMad.get_data(5, 22)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'idBike' in df.columns
    assert df.index.name == 'unlock_date'
    assert pd.api.types.is_datetime64_any_dtype(df.index)

def test_data_property(mock_get_csv):
    b = BiciMad(5, 22)
    assert isinstance(b.data, pd.DataFrame)
    assert len(b.data) == 5

def test_data_property_after_clean(mock_get_csv):
    b = BiciMad(5, 22)
    b.clean()
    assert isinstance(b.data, pd.DataFrame)
    assert len(b.data) == 4

def test_str_output(mock_get_csv):
    b = BiciMad(5, 22)
    expected_output = b.data.to_string()
    actual_output = str(b)
    assert isinstance(actual_output, str)
    assert actual_output == expected_output

def test_str_output_after_clean(mock_get_csv):
    b = BiciMad(5, 22)
    b.clean()
    expected_output = b.data.to_string()
    actual_output = str(b)
    assert isinstance(actual_output, str)
    assert actual_output == expected_output

def test_clean(mock_get_csv):
    b = BiciMad(5, 22)
    b.clean()
    assert not b.data.isnull().all(axis=1).any()
    for col in ['fleet', 'idBike', 'station_lock', 'station_unlock']:
        assert b.data[col].dtype == object

def test_resume(mock_get_csv):
    b = BiciMad(5, 22)
    summary = b.resume()
    assert summary["year"] == 22
    assert summary["month"] == 5
    assert summary["total_uses"] == 5
    assert summary["total_time"] == 36.49 / 60
    assert {"'Calle Serrano nº 34'","'Calle Serrano nº 32'","'Calle Serrano nº 33'"} == summary["most_popular_station"]
    assert summary["uses_from_most_popular"] == 1

def test_resume_after_clean(mock_get_csv):
    b = BiciMad(5, 22)
    b.clean()
    summary = b.resume()
    assert summary["year"] == 22
    assert summary["month"] == 5
    assert summary["total_uses"] == 4
    assert summary["total_time"] == 36.49 / 60
    assert "'Calle Serrano nº 34'" in summary["most_popular_station"]
    assert summary["uses_from_most_popular"] == 2