import dataclasses
import enum
import typing
from functools import wraps
import warnings

from sortedcontainers import SortedDict


class Side(enum.IntEnum):
    """BIDS / BUY = 0; ASKS / SELL = 1"""

    BIDS = 0
    ASKS = 1

    # alias
    BUY = 0
    SELL = 1


@dataclasses.dataclass
class SideOrderBook(SortedDict):
    """One side (bids or asks) of an order book

    Parameters
    ----------
    side: Side enum
        Side.BIDS/BUY or Side.ASKS/SELL
    init_data: dict[float, float], optional, defaults to None
        initial orderbook data; price:quantity
    meta: dict
        to store metadata; e.g. trading pair, precision info, etc.
    """

    side: Side
    init_data: dataclasses.InitVar[dict] = None
    meta: dict = dataclasses.field(default_factory=dict)
    _is_bids: typing.ClassVar[bool] = None

    def __post_init__(self, init_data):
        assert isinstance(self.side, Side), "please use Side enum for side parameter"
        self._is_bids = self.side == Side.BIDS
        super().__init__(init_data)

    @property
    def is_bids(self):
        return self._is_bids

    def purge(self) -> None:
        """Remove keys with 0 value"""
        del_keys = [k for k, v in self.items() if v == 0]
        for k in del_keys:
            del self[k]

    def get_quantity(
        self, worst_price: float = None, best_price: float = None
    ) -> float:
        """
        Returns the quantity in order book between the best / worst prices provided

        Parameters
        ----------
        best_price, worst_price: float, optional, defaults to `None`
            "best" price = near tip of orderbook; "worst" = deep in orderbook

        Returns
        -------
        float
            total quantity between prices
        """

        lb, ub = (
            (worst_price, best_price) if self._is_bids else (best_price, worst_price)
        )

        return sum(self[key] for key in self.irange(lb, ub))

    def get_price_stats(
        self, quantity: float, buffer: float = 0
    ) -> typing.Dict[str, float]:
        """
        Returns price statistics for a given quantity

        Parameters
        ----------
        qty: float
            quantity to check
        buffer : float, optional, defaults to 0
            buffer quantity from tip of orderbook before analysis

        Returns
        -------
        dict[str, float]
            * average: average price @ quantity
            * best: best price @ quantity
            * worst: worst price @ quantity
            * total_qty: min(quantity, total quantity in orderbook); catch if quantity > total order book volume
        """
        buffer_remain = buffer
        qty_remain = quantity
        total_amt, total_qty = 0, 0
        best_price, worst_price = None, None

        # pylint: disable=bad-reversed-sequence
        price_iter = reversed(self) if self._is_bids else iter(self)

        for price_i in price_iter:
            qty_i = self[price_i]

            if buffer_remain > 0:
                if buffer_remain >= qty_i:
                    buffer_remain -= qty_i
                    continue
                else:
                    qty_i -= buffer_remain
                    buffer_remain = 0

            best_price = best_price or price_i
            cur_qty = min(qty_remain, qty_i)
            total_amt += price_i * cur_qty
            total_qty += cur_qty
            qty_remain -= cur_qty

            if qty_remain <= 0:
                break
        else:
            warnings.warn("`quantity` exceeded orderbook depth!")

        worst_price = price_i
        return {
            "average": (total_amt / total_qty) if total_qty > 0 else None,
            "best": best_price,
            "worst": worst_price,
            "total_qty": total_qty,
        }
