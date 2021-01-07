import typing

import pytest

from orderbook.core import SideOrderBook, Side
from tests import generate_data

TEST_DATA = generate_data.testing_data()

# test accuracy
@pytest.mark.parametrize("side", [Side.BIDS, Side.ASKS])
def test_orderbook(side):
    """Test basic orderbook functionality

    Notes
    -----
    Ideally, the side should not have an impact
    """

    data = TEST_DATA["data-orderbook"][10]

    with pytest.raises(AssertionError):
        SideOrderBook("asdf")

    ob = SideOrderBook(side, init_data=data)
    repr(ob)  # check if it prints

    # test get / set / del / update
    assert ob[100] == 1, "getitem failed"
    ob[90] = 90
    del ob[90]
    # TODO: update

    zero_qty = [1, 2, 3, 4, 5]
    for price in zero_qty:
        ob[price] = 0

    ob.purge()
    assert ob.keys().isdisjoint(zero_qty), "purge failed"


def test_get_price_stats():
    """Test `get_price_stats` method"""

    data = TEST_DATA["data-orderbook"][10]
    ob_asks = TEST_DATA["orderbook-asks"][10]
    ob_bids = TEST_DATA["orderbook-bids"][10]

    # typical scenario
    assert ob_asks.get_price_stats(4) == {
        "average": (100 * 1 + 110 * 2 + 120 * 1) / 4,
        "best": 100,
        "worst": 120,
        "total_qty": 4,
    }, "Failed `get_price_stats` for 'asks'"

    assert ob_bids.get_price_stats(14) == {
        "average": (190 * 10 + 180 * 4) / 14,
        "best": 190,
        "worst": 180,
        "total_qty": 14,
    }, "Failed `get_price_stats` for 'bids'"

    # overflow scenario
    with pytest.warns(Warning):
        ob_asks.get_price_stats(60)

    assert ob_asks.get_price_stats(60) == {
        "average": sum(k * v for k, v in data.items()) / sum(data.values()),
        "best": min(data),
        "worst": max(data),
        "total_qty": sum(data.values()),
    }

    assert ob_bids.get_price_stats(60) == {
        "average": sum(k * v for k, v in data.items()) / sum(data.values()),
        "best": max(data),
        "worst": min(data),
        "total_qty": sum(data.values()),
    }

    # test buffer
    assert ob_asks.get_price_stats(8, buffer=6) == {
        "average": (130 * 4 + 140 * 4) / 8,
        "best": 130.0,
        "worst": 140.0,
        "total_qty": 8.0,
    }

    assert ob_bids.get_price_stats(8, buffer=6) == {
        "average": (190 * 4 + 180 * 4) / 8,
        "best": 190.0,
        "worst": 180.0,
        "total_qty": 8.0,
    }


def test_get_quantity():
    """Test `get_quantity` method"""
    ob_asks = TEST_DATA["orderbook-asks"][10]
    ob_bids = TEST_DATA["orderbook-bids"][10]

    for price_i in [120, 129]:
        assert (
            ob_asks.get_quantity(price_i)
            == ob_bids.get_quantity(best_price=price_i)
            == 6
        ), "get_quantity low to high test failed"

    for price_i in [171, 180]:
        assert (
            ob_asks.get_quantity(best_price=price_i)
            == ob_bids.get_quantity(price_i)
            == 19
        ), "get_quantity high to low test failed"

    for lb_i, ub_i in [(130, 160), (121, 169)]:
        assert (
            ob_asks.get_quantity(ub_i, lb_i) == ob_bids.get_quantity(lb_i, ub_i) == 22
        ), "get_quantity middle test failed"
