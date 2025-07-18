# app/routes/assets.py
from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database.database import get_db
from app.database.models import User
from app.database.dependencies import get_current_active_user
from app.utils.sheets import get_all_assets, get_asset_by_id, get_dropdown_options
from app.utils.flash import get_flash

router = APIRouter(tags=["assets"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/assets", response_class=HTMLResponse)
async def list_assets(
    request: Request,
    status: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List assets with optional filtering."""
    # Get all assets from Google Sheets
    all_assets = get_all_assets()
    
    # Apply filters
    filtered_assets = all_assets
    
    if status:
        filtered_assets = [a for a in filtered_assets if a.get('Status') == status]
    if category:
        filtered_assets = [a for a in filtered_assets if a.get('Category') == category]
    if location:
        filtered_assets = [a for a in filtered_assets if a.get('Location') == location]
    if search:
        search = search.lower()
        filtered_assets = [a for a in filtered_assets if 
            search in str(a.get('Item Name', '')).lower() or
            search in str(a.get('Asset Tag', '')).lower() or
            search in str(a.get('Notes', '')).lower() or
            search in str(a.get('Serial Number', '')).lower()
        ]
    
    # Get dropdown options for filters
    dropdown_options = get_dropdown_options()
    
    # Get flash messages
    flash = get_flash(request)
    
    return templates.TemplateResponse(
        "assets/list.html",
        {
            "request": request,
            "user": current_user,
            "assets": filtered_assets,
            "categories": dropdown_options['categories'],
            "locations": list(dropdown_options['locations'].keys()),
            "statuses": ['Active', 'Damaged', 'Repaired', 'Disposed'],
            "selected_status": status,
            "selected_category": category,
            "selected_location": location,
            "search": search,
            "flash": flash
        }
    )

@router.get("/assets/{asset_id}", response_class=HTMLResponse)
async def asset_detail(
    request: Request,
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Asset detail page."""
    asset = get_asset_by_id(asset_id)
    if not asset:
        return RedirectResponse(url="/assets", status_code=status.HTTP_303_SEE_OTHER)
    
    # Get flash messages
    flash = get_flash(request)
    
    return templates.TemplateResponse(
        "assets/detail.html",
        {
            "request": request,
            "user": current_user,
            "asset": asset,
            "flash": flash
        }
    )