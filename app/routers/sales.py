from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from app.database import get_db
from app.schemas.sales import (
    StoreCreate, StoreUpdate, StoreResponse,
    TaxCreate, TaxUpdate, TaxResponse,
    PaymentMethodCreate, PaymentMethodUpdate, PaymentMethodResponse,
    OrderCreate, OrderUpdate, OrderResponse,
    OrderItemCreate, OrderItemResponse,
    PaymentCreate, PaymentUpdate, PaymentResponse,
    OrderReturnCreate, OrderReturnUpdate, OrderReturnResponse,
    OrderReturnItemCreate, OrderReturnItemResponse
)
from app.models.sales import (
    Store, Order, OrderItem, Tax, PaymentMethod, Payment,
    OrderReturn, OrderReturnItem
)
from app.core.security import generate_public_id

router = APIRouter(prefix="/sales", tags=["Sales"])


# Store endpoints
@router.post("/stores/", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
def create_store(store: StoreCreate, db: Session = Depends(get_db)):
    """Create a new store."""
    new_store = Store(
        public_id=generate_public_id(),
        **store.model_dump()
    )
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    return StoreResponse(
        id=new_store.public_id,
        name=new_store.name,
        code=new_store.code,
        phone=new_store.phone,
        is_default=new_store.is_default,
        status=new_store.status,
        address_id=new_store.address_id,
        created_at=new_store.created_at,
        updated_at=new_store.updated_at,
        deleted_at=new_store.deleted_at,
    )


@router.get("/stores/", response_model=List[StoreResponse])
def get_stores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all stores with pagination."""
    stores = db.query(Store).offset(skip).limit(limit).all()
    return [
        StoreResponse(
            id=store.public_id,
            name=store.name,
            code=store.code,
            phone=store.phone,
            is_default=store.is_default,
            status=store.status,
            address_id=store.address_id,
            created_at=store.created_at,
            updated_at=store.updated_at,
            deleted_at=store.deleted_at,
        )
        for store in stores
    ]


@router.get("/stores/{id}", response_model=StoreResponse)
def get_store(id: str, db: Session = Depends(get_db)):
    """Get a store by public_id."""
    store = db.query(Store).filter(Store.public_id == id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    return StoreResponse(
        id=store.public_id,
        name=store.name,
        code=store.code,
        phone=store.phone,
        is_default=store.is_default,
        status=store.status,
        address_id=store.address_id,
        created_at=store.created_at,
        updated_at=store.updated_at,
        deleted_at=store.deleted_at,
    )


@router.put("/stores/{id}", response_model=StoreResponse)
def update_store(id: str, store_update: StoreUpdate, db: Session = Depends(get_db)):
    """Update a store."""
    store = db.query(Store).filter(Store.public_id == id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )

    update_data = store_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(store, field, value)

    db.commit()
    db.refresh(store)
    return StoreResponse(
        id=store.public_id,
        name=store.name,
        code=store.code,
        phone=store.phone,
        is_default=store.is_default,
        status=store.status,
        address_id=store.address_id,
        created_at=store.created_at,
        updated_at=store.updated_at,
        deleted_at=store.deleted_at,
    )


@router.delete("/stores/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_store(id: str, db: Session = Depends(get_db)):
    """Soft delete a store."""
    store = db.query(Store).filter(Store.public_id == id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )

    store.deleted_at = datetime.now(timezone.utc)
    db.commit()

    return None


# Tax endpoints
@router.post("/taxes/", response_model=TaxResponse, status_code=status.HTTP_201_CREATED)
def create_tax(tax: TaxCreate, db: Session = Depends(get_db)):
    """Create a new tax rate."""
    new_tax = Tax(**tax.model_dump())
    db.add(new_tax)
    db.commit()
    db.refresh(new_tax)
    return new_tax


@router.get("/taxes/", response_model=List[TaxResponse])
def get_taxes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all taxes with pagination."""
    taxes = db.query(Tax).offset(skip).limit(limit).all()
    return taxes


@router.get("/taxes/{id}", response_model=TaxResponse)
def get_tax(id: int, db: Session = Depends(get_db)):
    """Get a tax by ID."""
    tax = db.query(Tax).filter(Tax.id == id).first()
    if not tax:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax not found"
        )
    return tax


@router.put("/taxes/{id}", response_model=TaxResponse)
def update_tax(id: int, tax_update: TaxUpdate, db: Session = Depends(get_db)):
    """Update a tax."""
    tax = db.query(Tax).filter(Tax.id == id).first()
    if not tax:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax not found"
        )

    update_data = tax_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tax, field, value)

    db.commit()
    db.refresh(tax)
    return tax


@router.delete("/taxes/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tax(id: int, db: Session = Depends(get_db)):
    """Delete a tax."""
    tax = db.query(Tax).filter(Tax.id == id).first()
    if not tax:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax not found"
        )

    db.delete(tax)
    db.commit()

    return None


# Payment Method endpoints
@router.post("/payment-methods/", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED)
def create_payment_method(payment_method: PaymentMethodCreate, db: Session = Depends(get_db)):
    """Create a new payment method."""
    new_payment_method = PaymentMethod(**payment_method.model_dump())
    db.add(new_payment_method)
    db.commit()
    db.refresh(new_payment_method)
    return new_payment_method


@router.get("/payment-methods/", response_model=List[PaymentMethodResponse])
def get_payment_methods(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all payment methods with pagination."""
    payment_methods = db.query(PaymentMethod).offset(skip).limit(limit).all()
    return payment_methods


@router.get("/payment-methods/{id}", response_model=PaymentMethodResponse)
def get_payment_method(id: int, db: Session = Depends(get_db)):
    """Get a payment method by ID."""
    payment_method = db.query(PaymentMethod).filter(PaymentMethod.id == id).first()
    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    return payment_method


@router.put("/payment-methods/{id}", response_model=PaymentMethodResponse)
def update_payment_method(id: int, payment_method_update: PaymentMethodUpdate, db: Session = Depends(get_db)):
    """Update a payment method."""
    payment_method = db.query(PaymentMethod).filter(PaymentMethod.id == id).first()
    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )

    update_data = payment_method_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(payment_method, field, value)

    db.commit()
    db.refresh(payment_method)
    return payment_method


@router.delete("/payment-methods/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment_method(id: int, db: Session = Depends(get_db)):
    """Delete a payment method."""
    payment_method = db.query(PaymentMethod).filter(PaymentMethod.id == id).first()
    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )

    db.delete(payment_method)
    db.commit()

    return None


# Order endpoints
@router.post("/orders/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order."""
    new_order = Order(
        public_id=generate_public_id(),
        **order.model_dump()
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return OrderResponse(
        id=new_order.public_id,
        order_number=new_order.order_number,
        channel=new_order.channel,
        status=new_order.status,
        payment_status=new_order.payment_status,
        subtotal=new_order.subtotal,
        discount_total=new_order.discount_total,
        tax_total=new_order.tax_total,
        grand_total=new_order.grand_total,
        amount_paid=new_order.amount_paid,
        currency=new_order.currency,
        notes=new_order.notes,
        business_id=new_order.business_id,
        store_id=new_order.store_id,
        customer_id=new_order.customer_id,
        served_by=new_order.served_by,
        ordered_at=new_order.ordered_at,
        completed_at=new_order.completed_at,
        created_at=new_order.created_at,
        updated_at=new_order.updated_at,
        deleted_at=new_order.deleted_at,
    )


@router.get("/orders/", response_model=List[OrderResponse])
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all orders with pagination."""
    orders = db.query(Order).offset(skip).limit(limit).all()
    return [
        OrderResponse(
            id=order.public_id,
            order_number=order.order_number,
            channel=order.channel,
            status=order.status,
            payment_status=order.payment_status,
            subtotal=order.subtotal,
            discount_total=order.discount_total,
            tax_total=order.tax_total,
            grand_total=order.grand_total,
            amount_paid=order.amount_paid,
            currency=order.currency,
            notes=order.notes,
            business_id=order.business_id,
            store_id=order.store_id,
            customer_id=order.customer_id,
            served_by=order.served_by,
            ordered_at=order.ordered_at,
            completed_at=order.completed_at,
            created_at=order.created_at,
            updated_at=order.updated_at,
            deleted_at=order.deleted_at,
        )
        for order in orders
    ]


@router.get("/orders/{id}", response_model=OrderResponse)
def get_order(id: str, db: Session = Depends(get_db)):
    """Get an order by public_id."""
    order = db.query(Order).filter(Order.public_id == id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return OrderResponse(
        id=order.public_id,
        order_number=order.order_number,
        channel=order.channel,
        status=order.status,
        payment_status=order.payment_status,
        subtotal=order.subtotal,
        discount_total=order.discount_total,
        tax_total=order.tax_total,
        grand_total=order.grand_total,
        amount_paid=order.amount_paid,
        currency=order.currency,
        notes=order.notes,
        business_id=order.business_id,
        store_id=order.store_id,
        customer_id=order.customer_id,
        served_by=order.served_by,
        ordered_at=order.ordered_at,
        completed_at=order.completed_at,
        created_at=order.created_at,
        updated_at=order.updated_at,
        deleted_at=order.deleted_at,
    )


@router.put("/orders/{id}", response_model=OrderResponse)
def update_order(id: str, order_update: OrderUpdate, db: Session = Depends(get_db)):
    """Update an order."""
    order = db.query(Order).filter(Order.public_id == id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    update_data = order_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)

    db.commit()
    db.refresh(order)
    return OrderResponse(
        id=order.public_id,
        order_number=order.order_number,
        channel=order.channel,
        status=order.status,
        payment_status=order.payment_status,
        subtotal=order.subtotal,
        discount_total=order.discount_total,
        tax_total=order.tax_total,
        grand_total=order.grand_total,
        amount_paid=order.amount_paid,
        currency=order.currency,
        notes=order.notes,
        business_id=order.business_id,
        store_id=order.store_id,
        customer_id=order.customer_id,
        served_by=order.served_by,
        ordered_at=order.ordered_at,
        completed_at=order.completed_at,
        created_at=order.created_at,
        updated_at=order.updated_at,
        deleted_at=order.deleted_at,
    )


@router.delete("/orders/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(id: str, db: Session = Depends(get_db)):
    """Soft delete an order."""
    order = db.query(Order).filter(Order.public_id == id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    order.deleted_at = datetime.now(timezone.utc)
    db.commit()

    return None


# Order Item endpoints
@router.post("/orders/{order_id}/items/", response_model=OrderItemResponse, status_code=status.HTTP_201_CREATED)
def create_order_item(order_id: str, item: OrderItemCreate, db: Session = Depends(get_db)):
    """Create an order item."""
    order = db.query(Order).filter(Order.public_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    new_item = OrderItem(
        order_id=order.id,
        **item.model_dump()
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("/orders/{order_id}/items/", response_model=List[OrderItemResponse])
def get_order_items(order_id: str, db: Session = Depends(get_db)):
    """Get all items for an order."""
    order = db.query(Order).filter(Order.public_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    return items


@router.get("/orders/{order_id}/items/{id}", response_model=OrderItemResponse)
def get_order_item(order_id: str, id: int, db: Session = Depends(get_db)):
    """Get an order item by ID."""
    order = db.query(Order).filter(Order.public_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    item = db.query(OrderItem).filter(
        OrderItem.order_id == order.id,
        OrderItem.id == id
    ).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found"
        )
    return item


@router.delete("/orders/{order_id}/items/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_item(order_id: str, id: int, db: Session = Depends(get_db)):
    """Delete an order item."""
    order = db.query(Order).filter(Order.public_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    item = db.query(OrderItem).filter(
        OrderItem.order_id == order.id,
        OrderItem.id == id
    ).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found"
        )

    db.delete(item)
    db.commit()

    return None


# Payment endpoints
@router.post("/orders/{order_id}/payments/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(order_id: str, payment: PaymentCreate, db: Session = Depends(get_db)):
    """Create a payment for an order."""
    order = db.query(Order).filter(Order.public_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    new_payment = Payment(
        order_id=order.id,
        public_id=generate_public_id(),
        **payment.model_dump()
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return PaymentResponse(
        id=new_payment.public_id,
        amount=new_payment.amount,
        reference=new_payment.reference,
        status=new_payment.status,
        business_id=new_payment.business_id,
        order_id=new_payment.order_id,
        payment_method_id=new_payment.payment_method_id,
        received_by=new_payment.received_by,
        paid_at=new_payment.paid_at,
        created_at=new_payment.created_at,
    )


@router.get("/orders/{order_id}/payments/", response_model=List[PaymentResponse])
def get_payments(order_id: str, db: Session = Depends(get_db)):
    """Get all payments for an order."""
    order = db.query(Order).filter(Order.public_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    payments = db.query(Payment).filter(Payment.order_id == order.id).all()
    return [
        PaymentResponse(
            id=payment.public_id,
            amount=payment.amount,
            reference=payment.reference,
            status=payment.status,
            business_id=payment.business_id,
            order_id=payment.order_id,
            payment_method_id=payment.payment_method_id,
            received_by=payment.received_by,
            paid_at=payment.paid_at,
            created_at=payment.created_at,
        )
        for payment in payments
    ]


@router.get("/orders/{order_id}/payments/{id}", response_model=PaymentResponse)
def get_payment(order_id: str, id: str, db: Session = Depends(get_db)):
    """Get a payment by public_id."""
    order = db.query(Order).filter(Order.public_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    payment = db.query(Payment).filter(
        Payment.order_id == order.id,
        Payment.public_id == id
    ).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return PaymentResponse(
        id=payment.public_id,
        amount=payment.amount,
        reference=payment.reference,
        status=payment.status,
        business_id=payment.business_id,
        order_id=payment.order_id,
        payment_method_id=payment.payment_method_id,
        received_by=payment.received_by,
        paid_at=payment.paid_at,
        created_at=payment.created_at,
    )


@router.put("/orders/{order_id}/payments/{id}", response_model=PaymentResponse)
def update_payment(order_id: str, id: str, payment_update: PaymentUpdate, db: Session = Depends(get_db)):
    """Update a payment."""
    order = db.query(Order).filter(Order.public_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    payment = db.query(Payment).filter(
        Payment.order_id == order.id,
        Payment.public_id == id
    ).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    update_data = payment_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(payment, field, value)

    db.commit()
    db.refresh(payment)
    return PaymentResponse(
        id=payment.public_id,
        amount=payment.amount,
        reference=payment.reference,
        status=payment.status,
        business_id=payment.business_id,
        order_id=payment.order_id,
        payment_method_id=payment.payment_method_id,
        received_by=payment.received_by,
        paid_at=payment.paid_at,
        created_at=payment.created_at,
    )


@router.delete("/orders/{order_id}/payments/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(order_id: str, id: str, db: Session = Depends(get_db)):
    """Delete a payment."""
    order = db.query(Order).filter(Order.public_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    payment = db.query(Payment).filter(
        Payment.order_id == order.id,
        Payment.public_id == id
    ).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    db.delete(payment)
    db.commit()

    return None


# Order Return endpoints
@router.post("/orders/{order_id}/returns/", response_model=OrderReturnResponse, status_code=status.HTTP_201_CREATED)
def create_order_return(order_id: str, order_return: OrderReturnCreate, db: Session = Depends(get_db)):
    """Create an order return."""
    order = db.query(Order).filter(Order.public_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    new_return = OrderReturn(
        order_id=order.id,
        public_id=generate_public_id(),
        **order_return.model_dump()
    )
    db.add(new_return)
    db.commit()
    db.refresh(new_return)
    return OrderReturnResponse(
        id=new_return.public_id,
        return_number=new_return.return_number,
        reason=new_return.reason,
        refund_total=new_return.refund_total,
        status=new_return.status,
        business_id=new_return.business_id,
        order_id=new_return.order_id,
        processed_by=new_return.processed_by,
        created_at=new_return.created_at,
    )


@router.get("/orders/{order_id}/returns/", response_model=List[OrderReturnResponse])
def get_order_returns(order_id: str, db: Session = Depends(get_db)):
    """Get all returns for an order."""
    order = db.query(Order).filter(Order.public_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    returns = db.query(OrderReturn).filter(OrderReturn.order_id == order.id).all()
    return [
        OrderReturnResponse(
            id=order_return.public_id,
            return_number=order_return.return_number,
            reason=order_return.reason,
            refund_total=order_return.refund_total,
            status=order_return.status,
            business_id=order_return.business_id,
            order_id=order_return.order_id,
            processed_by=order_return.processed_by,
            created_at=order_return.created_at,
        )
        for order_return in returns
    ]


@router.get("/orders/{order_id}/returns/{id}", response_model=OrderReturnResponse)
def get_order_return(order_id: str, id: str, db: Session = Depends(get_db)):
    """Get an order return by public_id."""
    order = db.query(Order).filter(Order.public_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    order_return = db.query(OrderReturn).filter(
        OrderReturn.order_id == order.id,
        OrderReturn.public_id == id
    ).first()
    if not order_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order return not found"
        )
    return OrderReturnResponse(
        id=order_return.public_id,
        return_number=order_return.return_number,
        reason=order_return.reason,
        refund_total=order_return.refund_total,
        status=order_return.status,
        business_id=order_return.business_id,
        order_id=order_return.order_id,
        processed_by=order_return.processed_by,
        created_at=order_return.created_at,
    )


@router.put("/orders/{order_id}/returns/{id}", response_model=OrderReturnResponse)
def update_order_return(order_id: str, id: str, order_return_update: OrderReturnUpdate, db: Session = Depends(get_db)):
    """Update an order return."""
    order = db.query(Order).filter(Order.public_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    order_return = db.query(OrderReturn).filter(
        OrderReturn.order_id == order.id,
        OrderReturn.public_id == id
    ).first()
    if not order_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order return not found"
        )

    update_data = order_return_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order_return, field, value)

    db.commit()
    db.refresh(order_return)
    return OrderReturnResponse(
        id=order_return.public_id,
        return_number=order_return.return_number,
        reason=order_return.reason,
        refund_total=order_return.refund_total,
        status=order_return.status,
        business_id=order_return.business_id,
        order_id=order_return.order_id,
        processed_by=order_return.processed_by,
        created_at=order_return.created_at,
    )


@router.delete("/orders/{order_id}/returns/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_return(order_id: str, id: str, db: Session = Depends(get_db)):
    """Delete an order return."""
    order = db.query(Order).filter(Order.public_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    order_return = db.query(OrderReturn).filter(
        OrderReturn.order_id == order.id,
        OrderReturn.public_id == id
    ).first()
    if not order_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order return not found"
        )

    db.delete(order_return)
    db.commit()

    return None


# Order Return Item endpoints
@router.post("/orders/{order_id}/returns/{return_id}/items/", response_model=OrderReturnItemResponse, status_code=status.HTTP_201_CREATED)
def create_order_return_item(order_id: str, return_id: str, item: OrderReturnItemCreate, db: Session = Depends(get_db)):
    """Create an order return item."""
    order = db.query(Order).filter(Order.public_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    order_return = db.query(OrderReturn).filter(
        OrderReturn.order_id == order.id,
        OrderReturn.public_id == return_id
    ).first()
    if not order_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order return not found"
        )

    new_item = OrderReturnItem(
        order_return_id=order_return.id,
        **item.model_dump()
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("/orders/{order_id}/returns/{return_id}/items/", response_model=List[OrderReturnItemResponse])
def get_order_return_items(order_id: str, return_id: str, db: Session = Depends(get_db)):
    """Get all items for an order return."""
    order = db.query(Order).filter(Order.public_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    order_return = db.query(OrderReturn).filter(
        OrderReturn.order_id == order.id,
        OrderReturn.public_id == return_id
    ).first()
    if not order_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order return not found"
        )

    items = db.query(OrderReturnItem).filter(OrderReturnItem.order_return_id == order_return.id).all()
    return items


@router.delete("/orders/{order_id}/returns/{return_id}/items/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_return_item(order_id: str, return_id: str, id: int, db: Session = Depends(get_db)):
    """Delete an order return item."""
    order = db.query(Order).filter(Order.public_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    order_return = db.query(OrderReturn).filter(
        OrderReturn.order_id == order.id,
        OrderReturn.public_id == return_id
    ).first()
    if not order_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order return not found"
        )

    item = db.query(OrderReturnItem).filter(
        OrderReturnItem.order_return_id == order_return.id,
        OrderReturnItem.id == id
    ).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order return item not found"
        )

    db.delete(item)
    db.commit()

    return None
