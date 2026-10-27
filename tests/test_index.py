from app.index import GeoIndex, Point


def test_nearest_orders_by_distance_and_respects_radius():
    index = GeoIndex(0.25)
    index.add([Point("near", 51.5, -0.1, {}), Point("far", 52.5, -0.1, {})])
    result = index.nearest(51.5, -0.11, 20, 10)
    assert [point.id for point, _ in result] == ["near"]
