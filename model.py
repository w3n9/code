from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: str

class OutOfStock(Exception):
    pass


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]):
        self.ref = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations = set()

    def allocate(self, order_line: OrderLine):
        if self.can_allocate(order_line):
            self._allocations.add(order_line)

    def deallocate(self, order_line: OrderLine):
        if order_line in self._allocations:
            self._allocations.remove(order_line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, order_line: OrderLine) -> bool:
        return self.sku == order_line.sku and self.available_quantity >= order_line.qty

    def __gt__(self,other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta



def allocate(line:OrderLine,batches:List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.ref
    except StopIteration:
        raise OutOfStock(f'Out of stock for sku {line.sku}')