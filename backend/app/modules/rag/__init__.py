"""Public API of the rag module (P4).

Other modules import only from `app.modules.rag`, never from its internal files.
"""
from .guard import contains_profanity
from .service import ensure_index, search_department_knowledge

__all__ = ["contains_profanity", "ensure_index", "search_department_knowledge"]
