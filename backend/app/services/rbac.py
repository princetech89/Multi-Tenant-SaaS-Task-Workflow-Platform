def require_role(user, allowed):
    if user.role not in allowed:
        raise Exception("Forbidden")
