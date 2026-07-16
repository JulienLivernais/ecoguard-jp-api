from pydantic import BaseModel, Field, ConfigDict


class WebhookBase(BaseModel):
    url: str = Field(...)


class WebhookCreate(WebhookBase):
    pass


class WebhookResponse(WebhookBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

