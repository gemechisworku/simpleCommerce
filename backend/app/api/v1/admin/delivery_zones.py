"""
Admin delivery zone management endpoints
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import require_admin
from app.models.user import User
from app.schemas.delivery_zone import (
    DeliveryZoneCreate,
    DeliveryZoneUpdate,
    DeliveryZoneResponse,
    DeliveryFeeCalculationResponse
)
from app.schemas.common import ResponseModel
from app.services.delivery_zone import (
    create_delivery_zone,
    get_delivery_zone_by_id,
    list_delivery_zones,
    update_delivery_zone,
    calculate_delivery_fee
)
from app.core.exceptions import NotFoundError

router = APIRouter()


@router.post("", response_model=ResponseModel[DeliveryZoneResponse], status_code=status.HTTP_201_CREATED)
async def create_delivery_zone_endpoint(
    zone_data: DeliveryZoneCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create delivery zone
    
    Requires admin role.
    """
    zone = create_delivery_zone(db, zone_data)
    return ResponseModel(data=DeliveryZoneResponse.model_validate(zone))


@router.get("", response_model=ResponseModel[list[DeliveryZoneResponse]], status_code=status.HTTP_200_OK)
async def list_delivery_zones_endpoint(
    active_only: bool = True,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List delivery zones
    
    Requires admin role.
    """
    zones = list_delivery_zones(db, active_only=active_only)
    return ResponseModel(data=[DeliveryZoneResponse.model_validate(z) for z in zones])


@router.get("/{zone_id}", response_model=ResponseModel[DeliveryZoneResponse], status_code=status.HTTP_200_OK)
async def get_delivery_zone_endpoint(
    zone_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get delivery zone by ID
    
    Requires admin role.
    """
    zone = get_delivery_zone_by_id(db, zone_id)
    if not zone:
        raise NotFoundError(f"Delivery zone with id {zone_id} not found")
    
    return ResponseModel(data=DeliveryZoneResponse.model_validate(zone))


@router.patch("/{zone_id}", response_model=ResponseModel[DeliveryZoneResponse], status_code=status.HTTP_200_OK)
async def update_delivery_zone_endpoint(
    zone_id: int,
    zone_data: DeliveryZoneUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update delivery zone
    
    Requires admin role.
    """
    zone = update_delivery_zone(db, zone_id, zone_data)
    return ResponseModel(data=DeliveryZoneResponse.model_validate(zone))


@router.get("/{zone_id}/calculate-fee", response_model=ResponseModel[DeliveryFeeCalculationResponse], status_code=status.HTTP_200_OK)
async def calculate_delivery_fee_endpoint(
    zone_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Calculate delivery fee and expected dates for a zone
    
    Requires admin role.
    """
    result = calculate_delivery_fee(db, zone_id)
    return ResponseModel(data=DeliveryFeeCalculationResponse(**result))


@router.get("/public/list", response_model=ResponseModel[list[DeliveryZoneResponse]], status_code=status.HTTP_200_OK)
async def list_delivery_zones_public(
    db: Session = Depends(get_db)
):
    """
    List active delivery zones (public endpoint)
    
    No authentication required.
    """
    zones = list_delivery_zones(db, active_only=True)
    return ResponseModel(data=[DeliveryZoneResponse.model_validate(z) for z in zones])


@router.get("/public/{zone_id}/calculate-fee", response_model=ResponseModel[DeliveryFeeCalculationResponse], status_code=status.HTTP_200_OK)
async def calculate_delivery_fee_public(
    zone_id: int,
    db: Session = Depends(get_db)
):
    """
    Calculate delivery fee and expected dates (public endpoint)
    
    No authentication required.
    """
    result = calculate_delivery_fee(db, zone_id)
    return ResponseModel(data=DeliveryFeeCalculationResponse(**result))

