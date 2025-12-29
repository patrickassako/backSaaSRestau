"""
Business logic for Order management module.

Handles order creation, listing, and status updates with proper validation.
"""
from typing import List
from uuid import UUID
from decimal import Decimal
from fastapi import HTTPException, status
from app.core.supabase import get_supabase_client
from app.modules.orders.schemas import OrderCreate, OrderStatusUpdate


# Valid order statuses
# Valid order statuses
VALID_STATUSES = {"pending", "confirmed", "preparing", "ready", "delivering", "completed", "canceled"}


def verify_restaurant_ownership(user_id: UUID, restaurant_id: UUID) -> bool:
    """Verify that the user owns the restaurant."""
    supabase = get_supabase_client()

    try:
        response = (
            supabase.table("restaurants")
            .select("id")
            .eq("id", str(restaurant_id))
            .eq("owner_id", str(user_id))
            .single()
            .execute()
        )
        return response.data is not None
    except Exception:
        return False


def verify_order_ownership(user_id: UUID, order_id: UUID) -> dict:
    """
    Verify that the user owns the restaurant associated with the order.
    Returns the order data if valid, raises HTTPException otherwise.
    """
    supabase = get_supabase_client()

    try:
        response = (
            supabase.table("orders")
            .select("*, restaurants!inner(owner_id)")
            .eq("id", str(order_id))
            .single()
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        if response.data["restaurants"]["owner_id"] != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this order"
            )

        return response.data

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )


def create_order(data: OrderCreate) -> dict:
    """
    Create a new order from public website.
    
    Steps:
    1. Verify restaurant exists
    2. Validate all menu items belong to the restaurant
    3. Validate all sides belong to their menu items
    4. Insert order, items, and sides
    5. Calculate and update total amount
    """
    supabase = get_supabase_client()

    # Step 1: Verify restaurant exists
    try:
        restaurant = (
            supabase.table("restaurants")
            .select("id")
            .eq("id", str(data.restaurant_id))
            .single()
            .execute()
        )
        if not restaurant.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )

    # Step 2: Validate all menu items belong to the restaurant
    menu_item_ids = [str(item.menu_item_id) for item in data.items]
    try:
        menu_items = (
            supabase.table("menu_items")
            .select("id, restaurant_id, name")
            .in_("id", menu_item_ids)
            .execute()
        )
        
        if not menu_items.data or len(menu_items.data) != len(menu_item_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more menu items not found"
            )

        # Check all items belong to the restaurant
        for item in menu_items.data:
            if item["restaurant_id"] != str(data.restaurant_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Menu item {item['id']} does not belong to this restaurant"
                )

        # Create lookup for item names
        item_names = {item["id"]: item["name"] for item in menu_items.data}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating menu items: {str(e)}"
        )

    # Step 3: Validate all sides belong to their menu items
    all_sides = []
    for item in data.items:
        for side in item.sides:
            all_sides.append({
                "side_id": str(side.menu_item_side_id),
                "menu_item_id": str(item.menu_item_id)
            })

    if all_sides:
        side_ids = [s["side_id"] for s in all_sides]
        try:
            sides_response = (
                supabase.table("menu_item_sides")
                .select("id, menu_item_id, name")
                .in_("id", side_ids)
                .execute()
            )

            if not sides_response.data or len(sides_response.data) != len(side_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more sides not found"
                )

            # Verify each side belongs to its menu item
            side_to_item = {s["id"]: s["menu_item_id"] for s in sides_response.data}
            for side_info in all_sides:
                if side_to_item.get(side_info["side_id"]) != side_info["menu_item_id"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Side {side_info['side_id']} does not belong to menu item {side_info['menu_item_id']}"
                    )

            # Create lookup for side names
            side_names = {s["id"]: s["name"] for s in sides_response.data}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error validating sides: {str(e)}"
            )
    else:
        side_names = {}

    # Step 4: Create the order
    try:
        order_data = {
            "restaurant_id": str(data.restaurant_id),
            "customer_name": data.customer_name,
            "customer_phone": data.customer_phone,
            "delivery_address": data.delivery_address,
            "delivery_note": data.delivery_note,
            "total_amount": 0,  # Will be updated after calculating
            "status": "pending"
        }

        order_response = supabase.table("orders").insert(order_data).execute()
        
        if not order_response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create order"
            )

        order_id = order_response.data[0]["id"]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating order: {str(e)}"
        )

    # Step 5: Insert order items and calculate total
    total_amount = Decimal("0")
    order_items_response = []

    try:
        for item in data.items:
            # Calculate item total: (base_price + sum of sides) * quantity
            item_sides_total = sum(Decimal(str(side.extra_price)) for side in item.sides)
            item_total = (Decimal(str(item.price)) + item_sides_total) * item.quantity
            total_amount += item_total

            # Insert order item
            order_item_data = {
                "order_id": order_id,
                "menu_item_id": str(item.menu_item_id),
                "quantity": item.quantity,
                "price": float(item.price),
                "total_price": float(item_total)
            }

            order_item_resp = supabase.table("order_items").insert(order_item_data).execute()
            
            if not order_item_resp.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create order item"
                )

            order_item_id = order_item_resp.data[0]["id"]
            
            # Insert sides for this item
            item_sides_response = []
            for side in item.sides:
                side_data = {
                    "order_item_id": order_item_id,
                    "menu_item_side_id": str(side.menu_item_side_id),
                    "extra_price": float(side.extra_price)
                }

                side_resp = supabase.table("order_item_sides").insert(side_data).execute()
                
                if side_resp.data:
                    side_record = side_resp.data[0]
                    side_record["side_name"] = side_names.get(str(side.menu_item_side_id))
                    item_sides_response.append(side_record)

            # Build item response
            item_record = order_item_resp.data[0]
            item_record["item_name"] = item_names.get(str(item.menu_item_id))
            item_record["sides"] = item_sides_response
            order_items_response.append(item_record)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating order items: {str(e)}"
        )

    # Step 6: Update order with total amount
    try:
        updated_order = (
            supabase.table("orders")
            .update({"total_amount": float(total_amount)})
            .eq("id", order_id)
            .execute()
        )

        if not updated_order.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update order total"
            )

        # Build final response
        final_order = updated_order.data[0]
        final_order["items"] = order_items_response
        
        return final_order

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finalizing order: {str(e)}"
        )


def get_restaurant_orders(user_id: UUID, restaurant_id: UUID) -> List[dict]:
    """
    Get all orders for a restaurant.
    
    Requires the user to be the restaurant owner.
    Returns orders with items and sides, sorted by created_at DESC.
    """
    # Verify ownership
    if not verify_restaurant_ownership(user_id, restaurant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this restaurant"
        )

    supabase = get_supabase_client()

    try:
        # Get orders with items and sides
        orders_response = (
            supabase.table("orders")
            .select("*")
            .eq("restaurant_id", str(restaurant_id))
            .order("created_at", desc=True)
            .execute()
        )

        orders = orders_response.data or []

        # For each order, get items and sides
        for order in orders:
            # Get order items
            items_response = (
                supabase.table("order_items")
                .select("*, menu_items(name)")
                .eq("order_id", order["id"])
                .execute()
            )

            items = items_response.data or []

            # For each item, get sides
            for item in items:
                sides_response = (
                    supabase.table("order_item_sides")
                    .select("*, menu_item_sides(name)")
                    .eq("order_item_id", item["id"])
                    .execute()
                )

                sides = sides_response.data or []
                
                # Flatten side data
                for side in sides:
                    if side.get("menu_item_sides"):
                        side["side_name"] = side["menu_item_sides"]["name"]
                    if "menu_item_sides" in side:
                        del side["menu_item_sides"]

                item["sides"] = sides
                
                # Flatten item data
                if item.get("menu_items"):
                    item["item_name"] = item["menu_items"]["name"]
                if "menu_items" in item:
                    del item["menu_items"]

            order["items"] = items

        return orders

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching orders: {str(e)}"
        )


def update_order_status(user_id: UUID, order_id: UUID, data: OrderStatusUpdate) -> dict:
    """
    Update the status of an order.
    
    Requires the user to be the owner of the restaurant associated with the order.
    """
    # Validate status
    if data.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
        )

    # Verify ownership (will raise if invalid)
    verify_order_ownership(user_id, order_id)

    supabase = get_supabase_client()

    try:
        response = (
            supabase.table("orders")
            .update({"status": data.status})
            .eq("id", str(order_id))
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update order status"
            )

        # Get updated order with items
        updated_order = response.data[0]
        
        # Fetch items for response
        items_response = (
            supabase.table("order_items")
            .select("*, menu_items(name)")
            .eq("order_id", str(order_id))
            .execute()
        )

        items = items_response.data or []
        
        for item in items:
            # Get sides
            sides_response = (
                supabase.table("order_item_sides")
                .select("*, menu_item_sides(name)")
                .eq("order_item_id", item["id"])
                .execute()
            )

            sides = sides_response.data or []
            for side in sides:
                if side.get("menu_item_sides"):
                    side["side_name"] = side["menu_item_sides"]["name"]
                if "menu_item_sides" in side:
                    del side["menu_item_sides"]

            item["sides"] = sides
            
            if item.get("menu_items"):
                item["item_name"] = item["menu_items"]["name"]
            if "menu_items" in item:
                del item["menu_items"]

        updated_order["items"] = items
        
        return updated_order

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating order: {str(e)}"
        )


def get_order_by_code(code: str) -> dict:
    """
    Get order details by short code (first 8 chars of UUID).
    
    This is a public method for order tracking.
    """
    if not code or len(code) != 8:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order code format"
        )

    supabase = get_supabase_client()

    try:
        # Find order by ID prefix match
        # Since 'id' is a UUID column, valid LIKE operations require casting to text.
        # However, a cleaner and more performant way for UUID prefix is using range queries.
        
        # Construct the UUID range for the given 8-char prefix
        start_uuid = f"{code}-0000-0000-0000-000000000000"
        end_uuid = f"{code}-ffff-ffff-ffff-ffffffffffff"

        response = (
            supabase.table("orders")
            .select("*")
            .gte("id", start_uuid)
            .lte("id", end_uuid)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
            
        # Take the first match
        order = response.data[0]
        # Check that the found order actually matches the code (redundant if LIKE works, but safe)
        if not str(order["id"]).startswith(code):
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        order_id = order["id"]
        
        # Determine status (using the same format as valid statuses)
        # Assuming the DB status is one of the valid ones
        
        # Fetch items
        items_response = (
            supabase.table("order_items")
            .select("*, menu_items(name)")
            .eq("order_id", order_id)
            .execute()
        )
        
        items = items_response.data or []
        
        # Prepare items with sides
        final_items = []
        for item in items:
            sides_response = (
                supabase.table("order_item_sides")
                .select("*, menu_item_sides(name)")
                .eq("order_item_id", item["id"])
                .execute()
            )
            
            sides = sides_response.data or []
            
            cleaned_sides = []
            for side in sides:
                if side.get("menu_item_sides"):
                    side["side_name"] = side["menu_item_sides"]["name"]
                if "menu_item_sides" in side:
                    del side["menu_item_sides"]
                cleaned_sides.append(side)

            item["sides"] = cleaned_sides
            
            if item.get("menu_items"):
                item["item_name"] = item["menu_items"]["name"]
            if "menu_items" in item:
                del item["menu_items"]
            
            final_items.append(item)
            
        return {
            "order_code": code,
            "status": order["status"],
            "total_price": order["total_amount"],
            "delivery_address": order["delivery_address"],
            "created_at": order["created_at"],
            "items": final_items
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching order: {str(e)}"
        )
