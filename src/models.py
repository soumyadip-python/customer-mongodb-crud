import uuid
from typing import Optional, Literal
from pydantic import BaseModel, Field

class Address(BaseModel):
    addressType: Literal['shipping', 'billing']
    addressLine:str = Field(...)
    city:str = Field(...)
    state:str = Field(...)
    zipCode:str = Field(...)
    country:str = Field(...)

class Phone(BaseModel):
    phoneType:str = Field(...)
    phoneNumber:str = Field(...)

class Customer(BaseModel):
    id:str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    customerNumber:str = Field(...)
    name:str = Field(...)
    email:str = Field(...)
    phone:Phone = Field(...)
    address:list[Address] = Field(...)
    customerType: Literal['active','inactive','draft'] | None = None
    planName: Literal['Gold','Silver','Bronze'] | None = None

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "customerNumber": "C000001",
                "name": "John Wick",
                "email": "john.wick@abc.com",
                "phone": {
                    "phoneType": "Mobile",
                    "phoneNumber":"+911234567890"
                },
                "address":[
                    {
                        "addressType": "shipping",
                        "addressLine":"1 MG Road",
                        "city":"Bangalore",
                        "state":"Karnataka",
                        "zipCode":"560001",
                        "country":"India",
                    },
                    {
                        "addressType": "billing",
                        "addressLine": "1 MG Road",
                        "city": "Bangalore",
                        "state": "Karnataka",
                        "zipCode": "560001",
                        "country": "India",
                    }
                ],
                "customerType": "active",
                "planName": "Gold",
            }
        }

class CustomerUpdate(BaseModel):
    email:Optional[str]
    phone:Optional[Phone]
    address:Optional[list[Address]]
    customerType: Optional[Literal['active','inactive','draft'] | None]
    planName: Optional[Literal['Gold','Silver','Bronze'] | None]

    class Config:
        schema_extra = {
            "example": {
                "email": "john.wick@abc.com",
                "phone": {
                    "phoneType": "Mobile",
                    "phoneNumber":"+911234567890"
                },
                "address":[
                    {
                        "addressType": "shipping",
                        "addressLine":"1 MG Road",
                        "city":"Bangalore",
                        "state":"Karnataka",
                        "zipCode":"560001",
                        "country":"India",
                    },
                    {
                        "addressType": "billing",
                        "addressLine": "1 MG Road",
                        "city": "Bangalore",
                        "state": "Karnataka",
                        "zipCode": "560001",
                        "country": "India",
                    }
                ],
                "customerType": "active",
                "planName": "Gold",
            }
        }