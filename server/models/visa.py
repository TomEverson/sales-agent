from sqlmodel import SQLModel, Field


class VisaRequirement(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    origin_country: str
    destination_country: str
    visa_required: bool
    visa_on_arrival: bool = False
    visa_eta: str | None = None
    max_stay_days: int | None = None
    notes: str | None = None


class VisaRequirementCreate(SQLModel):
    origin_country: str
    destination_country: str
    visa_required: bool
    visa_on_arrival: bool = False
    visa_eta: str | None = None
    max_stay_days: int | None = None
    notes: str | None = None
