import numpy

from ichnaea.geocalc import (
    _radius_cache,
    add_meters_to_latitude,
    add_meters_to_longitude,
    aggregate_position,
    distance,
    maximum_country_radius,
)
from ichnaea import constants
from ichnaea.tests.base import TestCase


class TestAddMetersToLatitude(TestCase):

    def test_returns_min_lat(self):
        self.assertEqual(add_meters_to_latitude(1.0, -(10 ** 10)),
                         constants.MIN_LAT)

    def test_returns_max_lat(self):
        self.assertEqual(add_meters_to_latitude(1.0, 10 ** 10),
                         constants.MAX_LAT)

    def test_adds_meters_to_latitude(self):
        self.assertAlmostEqual(add_meters_to_latitude(1.0, 1000),
                               1.009000009, 9)


class TestAddMetersToLongitude(TestCase):

    def test_returns_min_lon(self):
        self.assertEqual(add_meters_to_longitude(1.0, 1.0, -(10 ** 10)),
                         constants.MIN_LON)

    def test_returns_max_lon(self):
        self.assertEqual(add_meters_to_longitude(1.0, 1.0, 10 ** 10),
                         constants.MAX_LON)

    def test_adds_meters_to_longitude(self):
        self.assertAlmostEqual(add_meters_to_longitude(1.0, 1.0, 1000),
                               1.0166573581, 9)


class TestAggregatePosition(TestCase):

    def test_same(self):
        circles = numpy.array([(1.0, 1.0, 100.0)], dtype=numpy.double)
        self.assertEqual(aggregate_position(circles, 100.0),
                         (1.0, 1.0, 100.0))

    def test_minimum(self):
        circles = numpy.array([(1.0, 1.0, 100.0)], dtype=numpy.double)
        self.assertEqual(aggregate_position(circles, 333.0),
                         (1.0, 1.0, 333.0))


class TestDistance(TestCase):

    def test_simple_distance(self):
        # This is a simple case where the points are close to each other.
        lat1 = 44.0337065
        lon1 = -79.4908184
        lat2 = 44.0347065
        lon2 = -79.4918184
        delta = distance(lat1, lon1, lat2, lon2)
        self.assertAlmostEqual(delta, 136.9483, 4)

    def test_antipodal(self):
        # Antipodal points (opposite sides of the planet) have a round off
        # error with the standard haversine calculation which is extremely
        # old and assumes we are using fixed precision math instead of IEEE
        # floats.
        self.assertAlmostEqual(distance(90.0, 0.0, -90.0, 0), 20015086.796, 4)

    def test_out_of_range(self):
        self.assertAlmostEqual(
            distance(-100.0, -186.0, 0.0, 0.0), 8901747.5973, 4)

    def test_non_float(self):
        self.assertAlmostEqual(distance(1.0, 1.0, 1, 1.1), 11117.7991, 4)
        with self.assertRaises(TypeError):
            distance(None, '0.1', 1, 1.1)


class TestMaximumRadius(TestCase):

    li_radius = 13000.0
    usa_radius = 2826000.0
    vat_radius = 1000.0

    def test_alpha2(self):
        r = maximum_country_radius('US')
        self.assertEqual(r, self.usa_radius)
        cached = _radius_cache['US']
        self.assertEqual(r, cached)

        r = maximum_country_radius('us')
        self.assertEqual(r, self.usa_radius)
        self.assertFalse('us' in _radius_cache)

    def test_alpha3(self):
        r = maximum_country_radius('USA')
        self.assertEqual(r, self.usa_radius)
        cached = _radius_cache['USA']
        self.assertEqual(r, cached)

        r = maximum_country_radius('usa')
        self.assertEqual(r, self.usa_radius)
        self.assertFalse('usa' in _radius_cache)

    def test_small_countries(self):
        r = maximum_country_radius('LI')
        self.assertEqual(r, self.li_radius)
        r = maximum_country_radius('VAT')
        self.assertEqual(r, self.vat_radius)

    def test_malformed_country(self):
        r = maximum_country_radius(None)
        self.assertTrue(r is None)

        r = maximum_country_radius(42)
        self.assertTrue(r is None)

        r = maximum_country_radius('A')
        self.assertTrue(r is None)

        r = maximum_country_radius('-#1-')
        self.assertTrue(r is None)

    def test_unknown_country(self):
        r = maximum_country_radius('AA')
        self.assertTrue(r is None)
        self.assertFalse('AA' in _radius_cache)

        r = maximum_country_radius('AAA')
        self.assertTrue(r is None)
        self.assertFalse('AAA' in _radius_cache)
