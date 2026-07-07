from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict, Field


# --- Authentication ---------------------------------------------------------

class LoginRequest(BaseModel):
    username: str = Field(..., description="Your Middleware account username")
    password: str = Field(..., description="Your Middleware account password")


class UserInfo(BaseModel):
    id: str
    username: str
    email: str


class LoginResponse(BaseModel):
    accessToken: str
    user: UserInfo


# --- Data Offerings ----------------------------------------------------------

class DataOfferingCreate(BaseModel):
    title: str = Field(..., description="Title of the new Data Offering")
    data_catalog_business_object_id: str = Field(
        ..., description="Business Object ID, from GET /offerings/catalog"
    )
    status: str = "active"
    profile_selector: str = "json"
    type: str = "data"
    updating_frequency: str = "60"
    active_from: Optional[str] = None
    active_from_enable: str = "0"
    active_to: Optional[str] = None
    active_to_enable: str = "0"
    input_profile: Optional[str] = None
    input_data_source: Optional[str] = None
    comments: Optional[str] = None
    file_schema: Optional[str] = None
    file_schema_sample: Optional[str] = None
    profile_description: Optional[str] = None
    file_schema_filename: Optional[str] = None
    file_schema_sample_filename: Optional[str] = None
    use_custom_semantics: Optional[str] = None
    push_uri: Optional[str] = None
    topic: Optional[str] = None


class IdResponse(BaseModel):
    response: str


# --- Subscriptions -------------------------------------------------------------

class SubscriptionCreate(BaseModel):
    data_catalog_data_offering_id: str = Field(
        ..., description="ID of the Data Offering to subscribe to, from GET /offerings/available"
    )
    comments: Optional[str] = None
    status: str = "pending"


class RespondToRequest(BaseModel):
    """Body for accepting/rejecting a pending subscription request.

    Extra fields are allowed and passed through untouched: the upstream API accepts
    either the minimal identifying fields or the full request row (as returned by
    GET /subscriptions/requests) with only `status` changed.
    """

    model_config = ConfigDict(extra="allow")

    status: Literal["accept", "reject"]


# --- Data provide / consume ------------------------------------------------------

class ProvideDataRequest(BaseModel):
    title: str
    description: Optional[str] = None
    filename: str
    file: str = Field(..., description="File content, as documented by the connector (e.g. base64 or raw text)")
    fileSize: Optional[str] = None
    data_offering_id: str = Field(..., description="ID of the Data Offering this file is provided for")
    code: Optional[str] = None


class ProvideDataResponse(BaseModel):
    id: str
    responseCode: Optional[str] = None
