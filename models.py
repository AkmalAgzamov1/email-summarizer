from enum import Enum   
from dataclasses import dataclass
from datetime import datetime

class Category(str, Enum):
    IMPORTANT = "Important"
    NORMAL = "Normal"
    NOT_IMPORTANT = "Not Important"

    
class Provider(str, Enum):
    GMAIL = "Gmail"
    # outlook to be added later

#raw gmail
@dataclass
class Email:
    id: str

    provider: Provider
    sender: str
    subject: str
    body_text: str
    received_at: datetime


#after processing and classification
@dataclass 
class ClassifiedEmail:
    email: Email
    category: Category 
    summary: str
    # reasoning: Optional[str] = None
    # don't need it now, can be added later if needed