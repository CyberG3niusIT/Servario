# Alle Modelle hier importieren, damit SQLAlchemy die Mapper vollständig konfigurieren kann
from app.models.user import User  # noqa: F401
from app.models.team_member import TeamMember  # noqa: F401
from app.models.availability import AvailabilityRule, AvailabilityException  # noqa: F401
from app.models.service import Service, ServiceTeamMember  # noqa: F401
from app.models.customer import Customer  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.booking import Booking  # noqa: F401
from app.models.settings import InstanceSettings  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
