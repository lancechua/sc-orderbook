"""Generate Data for Tests"""
import random
import typing

from orderbook.core import SideOrderBook, Side


def orderbook(size: int) -> typing.Dict[float, float]:
    """Generate Orderbook data"""
    return {100 + (a * 10.0): (a + 1.0) for a in range(size)}


def orders(
    size: int,
    price_bounds: typing.Tuple[float, float] = (0, 1000),
    qty_bounds: typing.Tuple[float, float] = (5, 10),
) -> typing.Dict[float, float]:
    """Generate random Orders data"""
    p_lb, p_ub = price_bounds
    q_lb, q_ub = qty_bounds
    return {
        (p_lb + (p_ub - p_lb) * random.random()): (
            q_lb + (q_ub - q_lb) * random.random()
        )
        for a in range(size)
    }


def testing_data():
    """Generate data for testing"""
    # raw data: orderbook, orders
    data = {
        "data-orderbook": {size: orderbook(size) for size in [10, 30, 50, 100]},
        "data-orders": {size: orders(size) for size in [10, 30, 50, 100]},
    }

    # orderbook: bids / asks
    data["orderbook-bids"] = {
        size: SideOrderBook(Side.BIDS, init_data=data)
        for size, data in data["data-orderbook"].items()
    }
    data["orderbook-asks"] = {
        size: SideOrderBook(Side.ASKS, init_data=data)
        for size, data in data["data-orderbook"].items()
    }

    return data
