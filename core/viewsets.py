from rest_framework import viewsets
from core.middleware import get_current_tenant


class TenantSafeViewSet(viewsets.ModelViewSet):
    """
    A base ViewSet that enforces tenant isolation:
    - Filters queryset by current tenant
    - Auto-assigns tenant on create
    - Prevents tenant changes on update
    """

    def get_queryset(self):
        tenant = get_current_tenant()
        if tenant:
            return super().get_queryset().filter(tenant=tenant)
        return self.queryset.none()

    def perform_create(self, serializer):
        tenant = get_current_tenant()
        if not tenant:
            raise PermissionError("Tenant not found in request")
        serializer.save(tenant=tenant)

    def perform_update(self, serializer):
        tenant = get_current_tenant()
        if not tenant:
            raise PermissionError("Tenant not found in request")
        serializer.save(tenant=tenant)
