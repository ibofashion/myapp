from core.models import Sale, User


def can_edit_sale(user: User, sale: Sale) -> bool:
    return user.role == "admin" or sale.seller_id == user.id
