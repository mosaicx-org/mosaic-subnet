from pydantic import BaseModel


class MagicPromptReq(BaseModel):
    prompt: str
