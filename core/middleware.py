import threading
from django.utils.deprecation import MiddlewareMixin
from core.models import Tenant

# Thread-local storage for current tenant
_thread_locals = threading.local()

def get_current_tenant():
    return getattr(_thread_locals, "tenant", None)

class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tenant = None
        if request.user and request.user.is_authenticated:
            tenant = getattr(request.user, "tenant", None)
        _thread_locals.tenant = tenant
        request.tenant = tenant
