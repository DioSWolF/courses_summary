from app.core.exceptions import UserForbiddenError


def check_owner(resource_user_id: int, current_user_id: int):
    if resource_user_id != current_user_id:
        raise UserForbiddenError(current_user_id)
