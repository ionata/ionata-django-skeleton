"""Routes to be wired into the default router."""
from typing import List, Tuple

from rest_framework.viewsets import ViewSetMixin  # type: ignore

# Add viewsets from apps in the format "routes = [(r'regex', MyViewSet), ...]"
routes: List[Tuple[str, ViewSetMixin]] = []
