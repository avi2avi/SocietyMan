from fastapi import HTTPException, status

from app.core.enums import Role


def enforce_role(current_role: Role, allowed: set[Role]) -> None:
    if current_role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for this action",
        )
