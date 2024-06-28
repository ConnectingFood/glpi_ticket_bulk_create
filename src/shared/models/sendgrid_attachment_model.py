from pydantic import BaseModel

class AttachmentModel(BaseModel):

    file_path: str
    file_name: str
    file_type: str