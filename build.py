def load_role(role) -> type:
    assert role in ["Master", "Agent"]
    if role == "Master":
        from Master.app import Master as Role
        return Role
    elif role == "Agent":
        from Agent.app import Agent as Role
        return Role


def build(role: str, **kwargs):
    return build_role(load_role(role), **kwargs)


def build_role(role:type, **kwargs):
    return role(**kwargs)
