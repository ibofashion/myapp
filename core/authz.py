from functools import wraps

from django.core.exceptions import PermissionDenied

from core.models import Sale, User


def can_edit_sale(user: User, sale: Sale) -> bool:
    return user.role == "admin" or sale.seller_id == user.id


def is_admin(user: User) -> bool:
    return user.role == "admin"


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not is_admin(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapped
