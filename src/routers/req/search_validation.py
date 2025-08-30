from typing import List, Dict, Any
from fastapi import Header
from ...domains.user.value_objects.auth_vo import BaseAuthDTO

def search_list_check_visitor(
    role: str = Header(None),
    role_id: int = Header(None),
) -> BaseAuthDTO:
    if role is not None and role_id is not None:
        return BaseAuthDTO(role=role, role_id=role_id)
    
    return None