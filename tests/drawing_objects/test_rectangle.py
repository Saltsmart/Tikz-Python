from tikzpy import TikzPicture, Rectangle, Point
import pytest


@pytest.fixture
def tikz_rectangle():
    tikz = TikzPicture()
    rectangle = tikz.rectangle((2, 2), (3, 4), options="Blue")
    return rectangle


@pytest.fixture
def tikz_rectangle_left_greater_than_right():
    tikz = TikzPicture()
    rectangle = tikz.rectangle((3, 4), (2, 2), options="Blue")
    return rectangle


@pytest.fixture
def mock_rectangle():
    rectangle = Rectangle((2, 2), (3, 4), options="Blue")
    return rectangle


@pytest.mark.parametrize(
    "object",
    [
        "tikz_rectangle",
        "mock_rectangle",
    ],
)
def test_rectangle_constructor(object, request):
    rectangle = request.getfixturevalue(object)
    assert rectangle.left_corner.x == 2
    assert rectangle.left_corner.y == 2
    assert rectangle.right_corner.x == 3
    assert rectangle.right_corner.y == 4
    assert rectangle.options == "Blue"
    assert rectangle.height == 2
    assert rectangle.width == 1

    assert rectangle.center == Point(2.5, 3.0)
    assert rectangle.north == Point(2.5, 4)
    assert rectangle.east == Point(3, 3)
    assert rectangle.south == Point(2.5, 2)
    assert rectangle.west == Point(2, 3)

    assert rectangle.code == r"\draw[Blue] (2, 2) rectangle (3, 4);"


def test_left_corner_assignment(mock_rectangle):
    mock_rectangle.left_corner = (0, 0)
    assert mock_rectangle.left_corner == Point(0, 0)
    assert mock_rectangle.height == 4
    assert mock_rectangle.width == 3
    assert mock_rectangle.code == r"\draw[Blue] (0, 0) rectangle (3, 4);"


def test_right_corner_assignment(mock_rectangle):
    mock_rectangle.right_corner = (4, 4)
    assert mock_rectangle.right_corner == Point(4, 4)
    assert mock_rectangle.height == 2
    assert mock_rectangle.width == 2
    assert mock_rectangle.code == r"\draw[Blue] (2, 2) rectangle (4, 4);"


def test_rectangle_shift(mock_rectangle):
    mock_rectangle.shift(1, 1)
    assert mock_rectangle.left_corner == Point(3, 3)
    assert mock_rectangle.right_corner == Point(4, 5)
    assert mock_rectangle.code == r"\draw[Blue] (3, 3) rectangle (4, 5);"


def test_rectangle_scale(mock_rectangle):
    mock_rectangle.scale(2)
    assert mock_rectangle.left_corner == Point(4, 4)
    assert mock_rectangle.right_corner == Point(6, 8)
    assert mock_rectangle.code == r"\draw[Blue] (4, 4) rectangle (6, 8);"


@pytest.mark.parametrize(
    "left_corner,right_corner",
    [
        [(2, 2), (3, 4)],  # x_1 < x_2 and y_1 < y_2, good
        [(3, 2), (2, 4)],  # x_1 > x_2 but y_1 < y_2
        [(2, 4), (3, 2)],  # x_1 < x_2 but y_1 > y_2
        [(3, 4), (2, 2)],  # x_1 > x_2 and y_1 > y_2
    ],
)
def test_rectangle_attributes(left_corner, right_corner):
    rectangle = Rectangle(left_corner, right_corner)
    assert rectangle.north == Point(2.5, 4)
    assert rectangle.east == Point(3, 3)
    assert rectangle.south == Point(2.5, 2)
    assert rectangle.west == Point(2, 3)
