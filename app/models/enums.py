from enum import Enum

class OrgRole(str, Enum):
    admin = "admin"
    member = "member"


class MembershipStatus(str, Enum):
    active = "active"
    suspended = "suspended"
