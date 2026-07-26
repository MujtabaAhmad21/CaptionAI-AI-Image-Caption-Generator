from app.db.base_class import Base



# Import all models here for Alembic to discover them
from app.db.models.user import User  # noqa
from app.db.models.image import Image  # noqa
from app.db.models.caption import Caption  # noqa
from app.db.models.feedback import CaptionFeedback  # noqa
from app.db.models.job import Job  # noqa
from app.db.models.api_key import ApiKey  # noqa
