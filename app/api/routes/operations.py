from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.enums import Role
from app.models.entities import (
    AmenityBooking,
    Asset,
    ComplianceEvent,
    GatePass,
    InventoryItem,
    PurchaseRequest,
    StaffAttendance,
    StaffMember,
    User,
    Vehicle,
)
from app.schemas.dto import (
    AmenityBookingCreate,
    AmenityBookingRead,
    AssetCreate,
    AssetRead,
    ComplianceEventCreate,
    ComplianceEventRead,
    InventoryItemCreate,
    InventoryItemRead,
    InventoryItemUpdate,
    OperationsOverview,
    PurchaseRequestCreate,
    PurchaseRequestDecision,
    PurchaseRequestRead,
    GatePassCreate,
    GatePassRead,
    StaffAttendanceCreate,
    StaffAttendanceRead,
    StaffMemberCreate,
    StaffMemberRead,
    VehicleCreate,
    VehicleRead,
)

router = APIRouter(prefix="/operations", tags=["Society ERP Operations"])


def _is_platform_admin(user: User) -> bool:
    return user.role == Role.ADMIN


def _society_scope(user: User, requested_society_id: int | None = None) -> int | None:
    if _is_platform_admin(user):
        return requested_society_id
    if not user.society_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Society-scoped account required")
    if requested_society_id and requested_society_id != user.society_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requested society is outside your scope")
    return user.society_id


def _required_society_scope(user: User, requested_society_id: int | None = None) -> int:
    society_id = _society_scope(user, requested_society_id)
    if society_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="society_id is required for platform admin actions")
    return society_id


def _require_ops_role(user: User) -> None:
    if user.role not in {Role.ADMIN, Role.SOCIETY_ADMIN, Role.MANAGER}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operations admin access required")


def _inventory_payload(item: InventoryItem) -> dict:
    return {
        "id": item.id,
        "society_id": item.society_id,
        "name": item.name,
        "sku": item.sku,
        "category": item.category,
        "location": item.location,
        "quantity": item.quantity,
        "min_quantity": item.min_quantity,
        "unit_cost": item.unit_cost,
        "vendor_id": item.vendor_id,
        "updated_at": item.updated_at,
        "created_at": item.created_at,
        "needs_reorder": item.quantity <= item.min_quantity,
        "stock_value": item.quantity * item.unit_cost,
    }


@router.get("/overview", response_model=OperationsOverview)
def operations_overview(
    society_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    amc_window = datetime.utcnow() + timedelta(days=30)

    def apply_scope(query, model):
        if scoped_society_id is not None:
            return query.filter(model.society_id == scoped_society_id)
        return query

    assets_query = apply_scope(db.query(Asset), Asset)
    inventory_query = apply_scope(db.query(InventoryItem), InventoryItem)
    staff_query = apply_scope(db.query(StaffMember), StaffMember)
    attendance_query = apply_scope(db.query(StaffAttendance), StaffAttendance)
    vehicle_query = apply_scope(db.query(Vehicle), Vehicle)
    gate_pass_query = apply_scope(db.query(GatePass), GatePass)
    purchase_query = apply_scope(db.query(PurchaseRequest), PurchaseRequest)
    booking_query = apply_scope(db.query(AmenityBooking), AmenityBooking)
    compliance_query = apply_scope(db.query(ComplianceEvent), ComplianceEvent)

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    amc_filter = Asset.amc_expires_at.is_not(None), Asset.amc_expires_at <= amc_window
    low_stock_query = inventory_query.filter(InventoryItem.quantity <= InventoryItem.min_quantity)
    upcoming_amc_query = assets_query.filter(*amc_filter).order_by(Asset.amc_expires_at.asc()).limit(8)

    low_stock_items = [_inventory_payload(item) for item in low_stock_query.order_by(InventoryItem.quantity.asc()).limit(8).all()]

    return {
        "assets_total": assets_query.count(),
        "assets_with_amc_due": assets_query.filter(*amc_filter).count(),
        "inventory_items": inventory_query.count(),
        "inventory_reorder_alerts": low_stock_query.count(),
        "staff_active": staff_query.filter(StaffMember.is_active.is_(True)).count(),
        "staff_checked_in_today": attendance_query.filter(StaffAttendance.check_in_at >= today_start, StaffAttendance.check_out_at.is_(None)).count(),
        "registered_vehicles": vehicle_query.filter(Vehicle.is_active.is_(True)).count(),
        "active_gate_passes": gate_pass_query.filter(GatePass.status == "issued").count(),
        "open_purchase_requests": purchase_query.filter(PurchaseRequest.status == "pending").count(),
        "amenity_bookings_upcoming": booking_query.filter(AmenityBooking.starts_at >= datetime.utcnow(), AmenityBooking.status == "booked").count(),
        "open_compliance_events": compliance_query.filter(ComplianceEvent.status == "open").count(),
        "privacy_events_open": compliance_query.filter(
            ComplianceEvent.status == "open",
            or_(ComplianceEvent.event_type == "privacy", ComplianceEvent.event_type == "data_request"),
        ).count(),
        "low_stock_items": low_stock_items,
        "upcoming_amc_assets": upcoming_amc_query.all(),
    }


@router.post("/assets", response_model=AssetRead)
def create_asset(payload: AssetCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_ops_role(current_user)
    asset = Asset(**payload.model_dump(exclude={"society_id"}), society_id=_required_society_scope(current_user, payload.society_id))
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.get("/assets", response_model=list[AssetRead])
def list_assets(
    society_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(Asset)
    if scoped_society_id is not None:
        query = query.filter(Asset.society_id == scoped_society_id)
    return query.order_by(Asset.created_at.desc()).limit(200).all()


@router.post("/inventory", response_model=InventoryItemRead)
def create_inventory_item(payload: InventoryItemCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_ops_role(current_user)
    item = InventoryItem(**payload.model_dump(exclude={"society_id"}), society_id=_required_society_scope(current_user, payload.society_id))
    db.add(item)
    db.commit()
    db.refresh(item)
    return _inventory_payload(item)


@router.get("/inventory", response_model=list[InventoryItemRead])
def list_inventory(
    society_id: int | None = Query(default=None),
    reorder_only: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(InventoryItem)
    if scoped_society_id is not None:
        query = query.filter(InventoryItem.society_id == scoped_society_id)
    if reorder_only:
        query = query.filter(InventoryItem.quantity <= InventoryItem.min_quantity)
    return [_inventory_payload(item) for item in query.order_by(InventoryItem.updated_at.desc()).limit(200).all()]


@router.patch("/inventory/{item_id}", response_model=InventoryItemRead)
def update_inventory_item(item_id: int, payload: InventoryItemUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_ops_role(current_user)
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    _required_society_scope(current_user, item.society_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return _inventory_payload(item)


@router.post("/staff", response_model=StaffMemberRead)
def create_staff_member(payload: StaffMemberCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_ops_role(current_user)
    member = StaffMember(**payload.model_dump(exclude={"society_id"}), society_id=_required_society_scope(current_user, payload.society_id))
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.get("/staff", response_model=list[StaffMemberRead])
def list_staff(
    society_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(StaffMember)
    if scoped_society_id is not None:
        query = query.filter(StaffMember.society_id == scoped_society_id)
    return query.order_by(StaffMember.created_at.desc()).limit(200).all()


@router.post("/staff/attendance", response_model=StaffAttendanceRead)
def check_in_staff(payload: StaffAttendanceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_ops_role(current_user)
    society_id = _required_society_scope(current_user, payload.society_id)
    member = db.get(StaffMember, payload.staff_member_id)
    if not member or member.society_id != society_id:
        raise HTTPException(status_code=404, detail="Staff member not found in this society")
    attendance = StaffAttendance(staff_member_id=payload.staff_member_id, society_id=society_id, status=payload.status)
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


@router.patch("/staff/attendance/{attendance_id}/checkout", response_model=StaffAttendanceRead)
def check_out_staff(attendance_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_ops_role(current_user)
    attendance = db.get(StaffAttendance, attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Staff attendance record not found")
    _required_society_scope(current_user, attendance.society_id)
    attendance.check_out_at = datetime.utcnow()
    db.commit()
    db.refresh(attendance)
    return attendance


@router.post("/vehicles", response_model=VehicleRead)
def create_vehicle(payload: VehicleCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_ops_role(current_user)
    vehicle = Vehicle(**payload.model_dump(exclude={"society_id"}), society_id=_required_society_scope(current_user, payload.society_id))
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.get("/vehicles", response_model=list[VehicleRead])
def list_vehicles(
    society_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(Vehicle)
    if scoped_society_id is not None:
        query = query.filter(Vehicle.society_id == scoped_society_id)
    return query.order_by(Vehicle.created_at.desc()).limit(200).all()


@router.post("/gate-passes", response_model=GatePassRead)
def create_gate_pass(payload: GatePassCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_ops_role(current_user)
    gate_pass = GatePass(
        **payload.model_dump(exclude={"society_id", "valid_from"}, exclude_none=True),
        society_id=_required_society_scope(current_user, payload.society_id),
        valid_from=payload.valid_from or datetime.utcnow(),
        created_by_user_id=current_user.id,
    )
    db.add(gate_pass)
    db.commit()
    db.refresh(gate_pass)
    return gate_pass


@router.get("/gate-passes", response_model=list[GatePassRead])
def list_gate_passes(
    society_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(GatePass)
    if scoped_society_id is not None:
        query = query.filter(GatePass.society_id == scoped_society_id)
    return query.order_by(GatePass.created_at.desc()).limit(200).all()


@router.post("/purchase-requests", response_model=PurchaseRequestRead)
def create_purchase_request(payload: PurchaseRequestCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society_scope(current_user, payload.society_id)
    request = PurchaseRequest(
        **payload.model_dump(exclude={"society_id"}),
        society_id=society_id,
        requested_by_user_id=current_user.id,
        status="pending",
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@router.get("/purchase-requests", response_model=list[PurchaseRequestRead])
def list_purchase_requests(
    society_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(PurchaseRequest)
    if scoped_society_id is not None:
        query = query.filter(PurchaseRequest.society_id == scoped_society_id)
    return query.order_by(PurchaseRequest.created_at.desc()).limit(200).all()


@router.patch("/purchase-requests/{request_id}/decision", response_model=PurchaseRequestRead)
def decide_purchase_request(
    request_id: int,
    payload: PurchaseRequestDecision,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_ops_role(current_user)
    request = db.get(PurchaseRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Purchase request not found")
    _required_society_scope(current_user, request.society_id)
    request.status = payload.status
    request.approved_by_user_id = current_user.id if payload.status == "approved" else None
    request.approved_at = datetime.utcnow() if payload.status == "approved" else None
    db.commit()
    db.refresh(request)
    return request


@router.post("/amenity-bookings", response_model=AmenityBookingRead)
def create_amenity_booking(payload: AmenityBookingCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.ends_at <= payload.starts_at:
        raise HTTPException(status_code=400, detail="Booking end time must be after start time")
    society_id = _required_society_scope(current_user, payload.society_id)
    resident_user_id = payload.resident_user_id or current_user.id
    if current_user.role == Role.RESIDENT and resident_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Residents can only create their own bookings")
    booking = AmenityBooking(**payload.model_dump(exclude={"society_id", "resident_user_id"}), society_id=society_id, resident_user_id=resident_user_id)
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/amenity-bookings", response_model=list[AmenityBookingRead])
def list_amenity_bookings(
    society_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(AmenityBooking)
    if scoped_society_id is not None:
        query = query.filter(AmenityBooking.society_id == scoped_society_id)
    if current_user.role == Role.RESIDENT:
        query = query.filter(AmenityBooking.resident_user_id == current_user.id)
    return query.order_by(AmenityBooking.starts_at.asc()).limit(200).all()


@router.post("/compliance-events", response_model=ComplianceEventRead)
def create_compliance_event(payload: ComplianceEventCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_ops_role(current_user)
    event = ComplianceEvent(**payload.model_dump(exclude={"society_id"}), society_id=_required_society_scope(current_user, payload.society_id))
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/compliance-events", response_model=list[ComplianceEventRead])
def list_compliance_events(
    society_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(ComplianceEvent)
    if scoped_society_id is not None:
        query = query.filter(ComplianceEvent.society_id == scoped_society_id)
    return query.order_by(func.coalesce(ComplianceEvent.due_at, ComplianceEvent.created_at).asc()).limit(200).all()
