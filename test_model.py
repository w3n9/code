from datetime import date, timedelta
import pytest

from model import Batch, OrderLine, OutOfStock, allocate

# from model import ...

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch("batch-ref", sku, batch_qty, eta=today),
        OrderLine("order-ref", sku, line_qty),
    )


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", 20, eta=today)
    order_line = OrderLine("order-ref", "SMALL-TABLE", 2)
    batch.allocate(order_line)
    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
    batch, line = make_batch_and_line("SMALL-TABLE", 20, 18)
    assert batch.can_allocate(line)


def test_cannot_allocate_if_available_smaller_than_required():
    batch, line = make_batch_and_line("SMALL-TABLE", 18, 20)
    assert batch.can_allocate(line) is False


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("SMALL-TABLE", 20, 20)
    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_donot_match():
    batch = Batch("batch-ref", "BIG-TABLE", 20, eta=today)
    line = OrderLine("order-ref", "SMALL-TABLE", 18)
    assert batch.can_allocate(line) is False


def test_can_only_deallocate_allocated_lines():
    batch, line = make_batch_and_line("SMALL-TABLE", 20, 2)
    batch.deallocate(line)
    assert batch.available_quantity == 20


def test_prefers_warehouse_batches_to_shipments():
    batch,line = make_batch_and_line('SMALL-TABLE',20,2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18

def test_perfers_current_stock_batches_to_shipments():
    in_stock_batch = Batch('in-stock-batch','RETRO-CLOCK',100,eta=None)
    shipment_batch = Batch('shipment-batch','RETRO-CLOCK',100,eta=tomorrow)
    line = OrderLine('order-ref','RETRO-CLOCK',10)
    allocate(line,[in_stock_batch,shipment_batch])
    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100

def test_prefers_earlier_batches():
    today_batch = Batch('today-batch','RETRO-CLOCK',100,eta=today)
    tomorrow_batch = Batch('tomorrow-batch','RETRO-CLOCK',100,eta=tomorrow)
    later_batch = Batch('later-batch','RETRO-CLOCK',100,eta=later)
    line = OrderLine('order-ref','RETRO-CLOCK',10)
    allocate(line,[today_batch,tomorrow_batch,later_batch])
    assert today_batch.available_quantity ==90
    assert tomorrow_batch.available_quantity == 100
    assert later_batch.available_quantity == 100

def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch-ref", "HIGHBROW-POSTER", 100, eta=None)
    shipment_batch = Batch("shipment-batch-ref", "HIGHBROW-POSTER", 100, eta=tomorrow)
    line = OrderLine("oref", "HIGHBROW-POSTER", 10)
    allocation = allocate(line, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.ref


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch('batch1','SMALL-FORK',10,eta=today)
    allocate(OrderLine('order1','SMALL-FORK',10),[batch])
    with pytest.raises(OutOfStock,match="SMALL-FORK"):
        allocate(OrderLine('order2','SMALL-FORK',1),[batch])