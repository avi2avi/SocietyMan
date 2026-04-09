from fastapi import Header

from app.core.enums import Role


# Placeholder role extraction for demo purposes.
def get_current_role(x_role: str = Header(default="resident")) -> Role:
    return Role(x_role)
