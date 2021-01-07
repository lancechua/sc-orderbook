import itertools as it
import typing

import pytest

from orderbook.core import SideOrderBook, Side
from tests import generate_data


def init(side, init_data):
    return SideOrderBook(side, init_data)


def add_orders(ob, orders):
    for price, qty in orders.items():
        ob[price] = qty


def add_orders_update(ob, orders):
    ob.update(orders)


def remove_orders(ob, prices):
    for price in prices:
        del ob[price]


def clear_orders(ob):
    ob.clear()


def get_price_stats(ob: SideOrderBook, args: typing.List[typing.List]):
    [ob.get_price_stats(*arg) for arg in args]


def get_quantity(ob: SideOrderBook, args: typing.List[typing.List]):
    [ob.get_quantity(*arg) for arg in args]


@pytest.mark.parametrize("side", [Side.BIDS, Side.ASKS])
@pytest.mark.parametrize("size", [10, 50, 100])
def test_bench_init(benchmark, side, size):
    data = generate_data.orderbook(size)
    benchmark(init, side, data)


@pytest.mark.parametrize("side", [Side.BIDS, Side.ASKS])
@pytest.mark.parametrize("size", [10, 50, 100])
@pytest.mark.parametrize("norders", [10, 50, 100])
def test_bench_add_orders(benchmark, side, size, norders):
    ob = SideOrderBook(side, generate_data.orderbook(size))
    orders = generate_data.orders(size, price_bounds=(100, 100 + norders * 10))
    benchmark(add_orders, ob, orders)


@pytest.mark.parametrize("side", [Side.BIDS, Side.ASKS])
@pytest.mark.parametrize("size", [10, 50, 100])
@pytest.mark.parametrize("norders", [10, 50, 100])
def test_bench_add_orders_update(benchmark, side, size, norders):
    ob = SideOrderBook(side, generate_data.orderbook(size))
    orders = generate_data.orders(size, price_bounds=(100, 100 + norders * 10))
    benchmark(add_orders_update, ob, orders)


@pytest.mark.parametrize("side", [Side.BIDS, Side.ASKS])
@pytest.mark.parametrize("size", [10, 50, 100])
def test_bench_remove_orders(benchmark, side, size):
    ob = SideOrderBook(side, generate_data.orderbook(size))
    prices = ob.keys()
    benchmark(remove_orders, ob, prices)


@pytest.mark.parametrize("side", [Side.BIDS, Side.ASKS])
@pytest.mark.parametrize("size", [10, 50, 100])
def test_bench_clear_orders(benchmark, side, size):
    ob = SideOrderBook(side, generate_data.orderbook(size))
    benchmark(clear_orders, ob)


@pytest.mark.parametrize("side", [Side.BIDS, Side.ASKS])
@pytest.mark.parametrize("size", [10, 50, 100])
def test_bench_get_price_stats(benchmark, side, size):
    ob = SideOrderBook(side, generate_data.orderbook(size))
    nitems = 50
    total_qty = sum(ob.values())
    args = [
        # quantity only
        ((0.05 + i / nitems) * total_qty,)
        for i in range(nitems)
    ] + [
        # quantity + buffer
        ((0.05 + i / nitems * 0.6) * total_qty, 0)
        for i in range(nitems)
    ]
    benchmark(get_price_stats, ob, args)


@pytest.mark.parametrize("side", [Side.BIDS, Side.ASKS])
@pytest.mark.parametrize("size", [10, 50, 100])
def test_bench_get_price_stats_buffer(benchmark, side, size):
    ob = SideOrderBook(side, generate_data.orderbook(size))
    nitems = 50
    total_qty = sum(ob.values())
    args = [
        # quantity only
        ((0.05 + i / nitems) * total_qty,)
        for i in range(nitems)
    ] + [
        # quantity + buffer
        ((0.05 + i / nitems * 0.6) * total_qty, (0.05 + i / nitems * 0.6) * total_qty)
        for i in range(nitems)
    ]
    benchmark(get_price_stats, ob, args)


@pytest.mark.parametrize("side", [Side.BIDS, Side.ASKS])
@pytest.mark.parametrize("size", [10, 50, 100])
def test_bench_get_quantity(benchmark, side, size):
    ob = SideOrderBook(side, generate_data.orderbook(size))
    lb, ub = ob.keys()[0], ob.keys()[-1]
    nitems = 50
    prices = [0.8 * lb + (i / nitems) * (1.2 * ub - 0.8 * lb) for i in range(nitems)]
    args = (
        [(price, None) for price in prices]  # worst_price only
        + [(None, price) for price in prices]  # best_price only
        + [
            (price, (0.5 if side == Side.BIDS else 1.5) * price) for price in prices
        ]  # worst_price + best_price
    )
    benchmark(get_quantity, ob, args)
