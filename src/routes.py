from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
from src.models import Customer, CustomerUpdate
from pymongo.errors import PyMongoError

router = APIRouter()


@router.post(
    "/",
    response_description="Create a new Customer",
    status_code=status.HTTP_201_CREATED,
    response_model=Customer,
)
def create_customer(request: Request, customer: Customer = Body(...)):
    try:
        customer = jsonable_encoder(customer)
        new_customer = request.app.state.db["customer"].insert_one(customer)
        created_customer = request.app.state.db["customer"].find_one(
            {"_id": new_customer.inserted_id}
        )
        return created_customer
    except PyMongoError as e:
        # Surface DB connectivity/errors as 503 Service Unavailable
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error: {e}",
        )


@router.get(
    "/",
    response_description="Get all Customers",
    status_code=status.HTTP_200_OK,
    response_model=List[Customer],
)
def get_all_customers(request: Request):
    try:
        customers = list(request.app.state.db["customer"].find(limit=100))
        return customers
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error: {e}",
        )


@router.get(
    "/{customer_number}",
    response_description="Get a Single Customer by CustomerNumber",
    status_code=status.HTTP_200_OK,
    response_model=Customer,
)
def get_customer(request: Request, customer_number: str):
    try:
        customer = request.app.state.db["customer"].find_one(
            {"customerNumber": customer_number}
        )
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Customer with CustomerNumber "
                    f"{customer_number} not found"
                ),
            )
        return jsonable_encoder(customer)
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error: {e}",
        )


@router.put(
    "/{customer_number}",
    response_description="Update a Customer",
    status_code=status.HTTP_200_OK,
    response_model=Customer,
)
def update_customer(
    request: Request,
    customer_number: str,
    customer: CustomerUpdate = Body(...),
):
    update_customer_details = customer.model_dump(exclude_none=True)
    if not update_customer_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Fields to Update",
        )

    try:
        collection = request.app.state.db["customer"]
        updated_customer_result = collection.update_one(
            {"customerNumber": customer_number},
            {"$set": update_customer_details},
        )

        if updated_customer_result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Customer with CustomerNumber "
                    f"{customer_number} was not found"
                ),
            )

        updated_customer = collection.find_one(
            {"customerNumber": customer_number}
        )

        if not updated_customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Customer with CustomerNumber "
                    f"{customer_number} not found"
                ),
            )
        return jsonable_encoder(updated_customer)
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error: {e}",
        )


@router.delete("/{customer_number}", response_description="Delete a Customer")
def delete_customer(
    request: Request,
    customer_number: str,
    response: Response,
):
    try:
        deleted_customer_result = request.app.state.db["customer"].delete_one(
            {"customerNumber": customer_number}
        )
        if deleted_customer_result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Customer with CustomerNumber "
                    f"{customer_number} was not found"
                ),
            )

        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error: {e}",
        )
