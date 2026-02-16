"""
Delivery zone service
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from decimal import Decimal
from datetime import date, timedelta

from app.models.delivery_zone import DeliveryZone
from app.core.exceptions import NotFoundError, BusinessRuleError
from app.schemas.delivery_zone import DeliveryZoneCreate, DeliveryZoneUpdate
from app.utils.helpers import calculate_delivery_dates
import logging

logger = logging.getLogger(__name__)


def create_delivery_zone(db: Session, zone_data: DeliveryZoneCreate) -> DeliveryZone:
    """Create delivery zone"""
    # Validate ETA
    if zone_data.eta_max_days < zone_data.eta_min_days:
        raise BusinessRuleError("eta_max_days must be >= eta_min_days")
    
    zone = DeliveryZone(
        name=zone_data.name,
        description=zone_data.description,
        fee=zone_data.fee,
        eta_min_days=zone_data.eta_min_days,
        eta_max_days=zone_data.eta_max_days,
        is_active=zone_data.is_active
    )
    
    db.add(zone)
    db.commit()
    db.refresh(zone)
    
    logger.info(f"Created delivery zone: {zone.name} (id: {zone.id})")
    return zone


def get_delivery_zone_by_id(db: Session, zone_id: int) -> Optional[DeliveryZone]:
    """Get delivery zone by ID"""
    return db.query(DeliveryZone).filter(DeliveryZone.id == zone_id).first()


def list_delivery_zones(db: Session, active_only: bool = True) -> List[DeliveryZone]:
    """List delivery zones"""
    query = db.query(DeliveryZone)
    
    if active_only:
        query = query.filter(DeliveryZone.is_active == True)
    
    return query.order_by(DeliveryZone.name.asc()).all()


def update_delivery_zone(db: Session, zone_id: int, zone_data: DeliveryZoneUpdate) -> DeliveryZone:
    """Update delivery zone"""
    zone = get_delivery_zone_by_id(db, zone_id)
    
    if not zone:
        raise NotFoundError(f"Delivery zone with id {zone_id} not found")
    
    # Update fields
    if zone_data.name is not None:
        zone.name = zone_data.name
    
    if zone_data.description is not None:
        zone.description = zone_data.description
    
    if zone_data.fee is not None:
        zone.fee = zone_data.fee
    
    if zone_data.eta_min_days is not None:
        zone.eta_min_days = zone_data.eta_min_days
    
    if zone_data.eta_max_days is not None:
        zone.eta_max_days = zone_data.eta_max_days
    
    if zone_data.is_active is not None:
        zone.is_active = zone_data.is_active
    
    # Validate ETA
    if zone.eta_max_days < zone.eta_min_days:
        raise BusinessRuleError("eta_max_days must be >= eta_min_days")
    
    db.commit()
    db.refresh(zone)
    
    logger.info(f"Updated delivery zone: {zone.name} (id: {zone.id})")
    return zone


def calculate_delivery_fee(db: Session, zone_id: int) -> dict:
    """
    Calculate delivery fee and expected dates for a zone
    
    Args:
        db: Database session
        zone_id: Delivery zone ID
        
    Returns:
        Dictionary with fee, ETA, and expected dates
        
    Raises:
        NotFoundError: If zone not found
    """
    zone = get_delivery_zone_by_id(db, zone_id)
    
    if not zone or not zone.is_active:
        raise NotFoundError(f"Active delivery zone with id {zone_id} not found")
    
    expected_from, expected_to = calculate_delivery_dates(zone.eta_min_days, zone.eta_max_days)
    
    return {
        "zone_id": zone.id,
        "zone_name": zone.name,
        "fee": zone.fee,
        "eta_min_days": zone.eta_min_days,
        "eta_max_days": zone.eta_max_days,
        "expected_delivery_from": expected_from,
        "expected_delivery_to": expected_to
    }

