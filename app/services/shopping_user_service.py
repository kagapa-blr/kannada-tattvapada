from sqlalchemy import func

from app.config.database import db_instance
from app.models.tatvapada import Tatvapada, ShoppingTatvapada
from app.models.tatvapada_author_info import TatvapadaAuthorInfo
from app.models.user_management import ShoppingUser, ShoppingUserAddress, ShoppingOrder, User
import pytz
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import traceback

# Define IST timezone
IST = pytz.timezone("Asia/Kolkata")


class MessageTemplate:
    @staticmethod
    def database_error(error):
        return {"success": False, "message": f"Database error: {error}", "data": None}

    @staticmethod
    def not_found(entity):
        return {"success": False, "message": f"{entity} not found.", "data": None}


# -------------------------
# ShoppingUser Service
# -------------------------
# -------------------------
# ShoppingUser Service
# -------------------------

class ShoppingUserService:
    @staticmethod
    def serialize_user(user: ShoppingUser):
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "gender": user.gender,
            "date_of_birth": user.date_of_birth.astimezone(IST).strftime("%d-%m-%Y") if user.date_of_birth else None,
            "preferred_language": user.preferred_language,
            "last_login_at": user.last_login_at.astimezone(IST).strftime(
                "%d-%m-%Y %I:%M %p") if user.last_login_at else None,
            "created_at": user.created_at.astimezone(IST).strftime("%d-%m-%Y %I:%M %p") if user.created_at else None,
            "updated_at": user.updated_at.astimezone(IST).strftime("%d-%m-%Y %I:%M %p") if user.updated_at else None,
        }

    @staticmethod
    def get_user_by_email(email, auto_create=True):
        try:
            email_normalized = email.strip().lower()
            user = User.query.filter(func.lower(User.email) == email_normalized).first()
            if not user:
                return MessageTemplate.not_found("User")

            shopping_user = ShoppingUser.query.filter_by(user_id=user.id).first()
            if not shopping_user and auto_create:
                shopping_user = ShoppingUser(
                    user_id=user.id,
                    name_override=user.name.strip() if user.name else None,
                    phone_override=user.phone.strip() if user.phone else None,
                    last_login_at=datetime.now(IST)  # Set last login in IST
                )
                db_instance.session.add(shopping_user)
                db_instance.session.commit()
                db_instance.session.refresh(shopping_user)
            elif not shopping_user:
                return MessageTemplate.not_found("ShoppingUser")

            # Update last login automatically in IST
            shopping_user.last_login_at = datetime.now(IST)
            db_instance.session.commit()
            db_instance.session.refresh(shopping_user)

            return {"success": True, "message": "", "data": ShoppingUserService.serialize_user(shopping_user)}
        except SQLAlchemyError as e:
            db_instance.session.rollback()
            traceback.print_exc()
            return MessageTemplate.database_error(str(e))

    @staticmethod
    def create_user(email, **kwargs):
        try:
            email_normalized = email.strip().lower()
            user = User.query.filter(func.lower(User.email) == email_normalized).first()
            if not user:
                return MessageTemplate.not_found("User")
            if ShoppingUser.query.filter_by(user_id=user.id).first():
                return {"success": False, "message": "Shopping profile already exists.", "data": None}

            shopping_user = ShoppingUser(
                user_id=user.id,
                name_override=kwargs.get("name"),
                phone_override=kwargs.get("phone"),
                gender=kwargs.get("gender"),
                date_of_birth=kwargs.get("date_of_birth"),
                preferred_language=kwargs.get("preferred_language"),
                last_login_at=datetime.now(IST)  # IST for new profile
            )
            db_instance.session.add(shopping_user)
            db_instance.session.commit()
            db_instance.session.refresh(shopping_user)
            return {"success": True, "message": "Shopping profile created.",
                    "data": ShoppingUserService.serialize_user(shopping_user)}
        except SQLAlchemyError as e:
            db_instance.session.rollback()
            traceback.print_exc()
            return MessageTemplate.database_error(str(e))

    @staticmethod
    def update_user(email, **kwargs):
        try:
            email_normalized = email.strip().lower()
            user = User.query.filter(func.lower(User.email) == email_normalized).first()
            if not user:
                return MessageTemplate.not_found("User")

            shopping_user = ShoppingUser.query.filter_by(user_id=user.id).first()
            if not shopping_user:
                return MessageTemplate.not_found("ShoppingUser")

            allowed_keys = {"name", "phone", "gender", "date_of_birth", "preferred_language"}
            clean_kwargs = {k: v for k, v in kwargs.items() if k in allowed_keys}

            dob_str = clean_kwargs.get("date_of_birth")
            if dob_str:
                try:
                    clean_kwargs["date_of_birth"] = datetime.strptime(dob_str, "%Y-%m-%d").date()
                except ValueError:
                    return {"success": False, "message": "Invalid date format for date_of_birth. Use YYYY-MM-DD.",
                            "data": None}

            field_map = {
                "name": "name_override",
                "phone": "phone_override",
                "gender": "gender",
                "date_of_birth": "date_of_birth",
                "preferred_language": "preferred_language"
            }

            for key, value in clean_kwargs.items():
                db_field = field_map[key]
                setattr(shopping_user, db_field, value.strip() if isinstance(value, str) else value)

            # Update last login in IST
            shopping_user.last_login_at = datetime.now(IST)

            db_instance.session.commit()
            db_instance.session.refresh(shopping_user)

            return {"success": True, "message": "Shopping profile updated.",
                    "data": ShoppingUserService.serialize_user(shopping_user)}
        except SQLAlchemyError as e:
            db_instance.session.rollback()
            traceback.print_exc()
            return MessageTemplate.database_error(str(e))


# -------------------------
# ShoppingUserAddress Service
# -------------------------
class ShoppingUserAddressService:

    @staticmethod
    def serialize_address(address: ShoppingUserAddress):
        return {
            "id": address.id,
            "shopping_user_id": address.shopping_user_id,
            "address_line": address.address_line,
            "city": address.city,
            "taluk_division": address.taluk_division,
            "state": address.state,
            "country": address.country,
            "postal_code": address.postal_code,
            "address_type": address.address_type,
            "is_default": address.is_default,
            "recipient_name": address.recipient_name,
            "phone_number": address.phone_number,
            "latitude": address.latitude,
            "longitude": address.longitude,
            "delivery_instructions": address.delivery_instructions,
            "created_at": address.created_at.isoformat() if address.created_at else None,
            "updated_at": address.updated_at.isoformat() if address.updated_at else None,
        }

    @staticmethod
    def _unset_default_for_user(shopping_user_id: int):
        """Set all addresses for this user to is_default=False"""
        db_instance.session.query(ShoppingUserAddress) \
            .filter(
            ShoppingUserAddress.shopping_user_id == shopping_user_id,
            ShoppingUserAddress.is_default == True
        ) \
            .update({"is_default": False}, synchronize_session="fetch")
        db_instance.session.commit()

    @staticmethod
    def create_address(email, **kwargs):
        try:
            user = User.query.filter(func.lower(User.email) == email.strip().lower()).first()
            if not user:
                return MessageTemplate.not_found("User")

            shopping_user = ShoppingUser.query.filter_by(user_id=user.id).first()
            if not shopping_user:
                result = ShoppingUserService.get_user_by_email(email=email)
                if not result.get("success"):
                    return result
                shopping_user_id = result["data"]["id"]
                shopping_user = ShoppingUser.query.get(shopping_user_id)

            # If this new address is marked as default, unset other defaults
            if kwargs.get("is_default"):
                ShoppingUserAddressService._unset_default_for_user(shopping_user.id)

            address = ShoppingUserAddress(shopping_user_id=shopping_user.id, **kwargs)
            db_instance.session.add(address)
            db_instance.session.commit()
            db_instance.session.refresh(address)
            return {"success": True, "message": "Address created.",
                    "data": ShoppingUserAddressService.serialize_address(address)}
        except SQLAlchemyError as e:
            db_instance.session.rollback()
            return MessageTemplate.database_error(str(e))

    @staticmethod
    def update_address(address_id, **kwargs):
        try:
            address = ShoppingUserAddress.query.get(address_id)
            if not address:
                return MessageTemplate.not_found("Address")

            # If updating is_default=True, unset all other defaults for this user
            if kwargs.get("is_default"):
                ShoppingUserAddressService._unset_default_for_user(address.shopping_user_id)

            for key, value in kwargs.items():
                if hasattr(address, key) and value is not None:
                    setattr(address, key, value)

            db_instance.session.commit()
            db_instance.session.refresh(address)
            return {"success": True, "message": "Address updated.",
                    "data": ShoppingUserAddressService.serialize_address(address)}
        except SQLAlchemyError as e:
            db_instance.session.rollback()
            return MessageTemplate.database_error(str(e))

    @staticmethod
    def delete_address(address_id):
        try:
            address = ShoppingUserAddress.query.get(address_id)
            if not address:
                return MessageTemplate.not_found("Address")
            db_instance.session.delete(address)
            db_instance.session.commit()
            return {"success": True, "message": "Address deleted.", "data": None}
        except SQLAlchemyError as e:
            db_instance.session.rollback()
            return MessageTemplate.database_error(str(e))

    @staticmethod
    def list_addresses(email):
        try:
            user = User.query.filter(func.lower(User.email) == email.strip().lower()).first()
            if not user:
                return MessageTemplate.not_found("User")

            shopping_user = ShoppingUser.query.filter_by(user_id=user.id).first()
            if not shopping_user:
                return {"success": True, "message": "", "data": []}

            addresses = ShoppingUserAddress.query.filter_by(shopping_user_id=shopping_user.id).all()
            return {"success": True, "message": "",
                    "data": [ShoppingUserAddressService.serialize_address(a) for a in addresses]}
        except SQLAlchemyError as e:
            return MessageTemplate.database_error(str(e))


# -------------------------
# ShoppingOrder Service
# -------------------------
class ShoppingOrderService:

    @staticmethod
    def serialize_order(order: ShoppingOrder):
        return {
            "id": order.id,
            "shopping_user_id": order.shopping_user_id,
            "order_number": order.order_number,
            "status": order.status,
            "total_amount": order.total_amount,
            "payment_method": order.payment_method,
            "shipping_address_id": order.shipping_address_id,
            "notes": order.notes,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None,
        }

    @staticmethod
    def create_order(email, order_number, total_amount, **kwargs):
        try:
            user = User.query.filter(func.lower(User.email) == email.strip().lower()).first()
            if not user:
                return MessageTemplate.not_found("User")
            shopping_user = ShoppingUser.query.filter_by(user_id=user.id).first()
            if not shopping_user:
                result = ShoppingUserService.get_user_by_email(email=email)
                if not result.get("success"):
                    return result
                shopping_user_id = result["data"]["id"]
                shopping_user = ShoppingUser.query.get(shopping_user_id)
            order = ShoppingOrder(
                shopping_user_id=shopping_user.id,
                order_number=order_number,
                total_amount=total_amount,
                status=kwargs.get("status", "Pending"),
                payment_method=kwargs.get("payment_method"),
                shipping_address_id=kwargs.get("shipping_address_id"),
                notes=kwargs.get("notes")
            )
            db_instance.session.add(order)
            db_instance.session.commit()
            db_instance.session.refresh(order)
            return {"success": True, "message": "Order created.", "data": ShoppingOrderService.serialize_order(order)}
        except SQLAlchemyError as e:
            db_instance.session.rollback()
            return MessageTemplate.database_error(str(e))

    @staticmethod
    def update_order(order_id, **kwargs):
        try:
            order = ShoppingOrder.query.get(order_id)
            if not order:
                return MessageTemplate.not_found("Order")
            for key, value in kwargs.items():
                if hasattr(order, key) and value is not None:
                    setattr(order, key, value)
            db_instance.session.commit()
            db_instance.session.refresh(order)
            return {"success": True, "message": "Order updated.", "data": ShoppingOrderService.serialize_order(order)}
        except SQLAlchemyError as e:
            db_instance.session.rollback()
            return MessageTemplate.database_error(str(e))

    @staticmethod
    def delete_order(order_id):
        try:
            order = ShoppingOrder.query.get(order_id)
            if not order:
                return MessageTemplate.not_found("Order")
            db_instance.session.delete(order)
            db_instance.session.commit()
            return {"success": True, "message": "Order deleted.", "data": None}
        except SQLAlchemyError as e:
            db_instance.session.rollback()
            return MessageTemplate.database_error(str(e))

    @staticmethod
    def list_orders(email=None, limit=100, offset=0):
        try:
            query = ShoppingOrder.query
            if email:
                user = User.query.filter(func.lower(User.email) == email.strip().lower()).first()
                if not user:
                    return MessageTemplate.not_found("User")
                shopping_user = ShoppingUser.query.filter_by(user_id=user.id).first()
                if not shopping_user:
                    return {"success": True, "message": "", "data": []}
                query = query.filter_by(shopping_user_id=shopping_user.id)
            orders = query.offset(offset).limit(limit).all()
            return {"success": True, "message": "", "data": [ShoppingOrderService.serialize_order(o) for o in orders]}
        except SQLAlchemyError as e:
            return MessageTemplate.database_error(str(e))




class ShoppingTatvapadaService:

    @staticmethod
    def add_or_update_book(author_id: int, samputa_sankhye: str, price: float,
                           tatvapadakosha_sheershike: str = None):
        """
        Add a new book to shopping catalog or update price if it already exists.
        """
        session = db_instance.session

        # Check if book already exists for this author and samputa
        existing = session.query(ShoppingTatvapada).filter_by(
            tatvapada_author_id=author_id,
            samputa_sankhye=samputa_sankhye
        ).first()

        if existing:
            existing.price = price
            session.commit()
            return {"message": "Price updated successfully", "id": existing.id}

        # Add new entry
        new_item = ShoppingTatvapada(
            tatvapada_author_id=author_id,
            samputa_sankhye=samputa_sankhye,
            price=price,
            tatvapadakosha_sheershike=tatvapadakosha_sheershike
        )
        session.add(new_item)
        session.commit()
        return {"message": "Item added successfully", "id": new_item.id}

    @staticmethod
    def get_catalog(offset: int = 0, limit: int = 10):
        """
        Fetch shopping catalog with offset/limit pagination.
        Includes author name from TatvapadaAuthorInfo.
        """
        session = db_instance.session

        query = (
            session.query(
                ShoppingTatvapada.id,
                ShoppingTatvapada.samputa_sankhye,
                ShoppingTatvapada.price,
                ShoppingTatvapada.tatvapadakosha_sheershike,
                ShoppingTatvapada.tatvapada_author_id,
                TatvapadaAuthorInfo.tatvapadakarara_hesaru.label("author_name")
            )
            .join(TatvapadaAuthorInfo, ShoppingTatvapada.tatvapada_author_id == TatvapadaAuthorInfo.id)
        )

        total = query.count()
        results = query.offset(offset).limit(limit).all()

        items = [
            {
                "id": r.id,
                "samputa_sankhye": r.samputa_sankhye,
                "price": float(r.price),
                "tatvapadakosha_sheershike": r.tatvapadakosha_sheershike,
                "tatvapada_author_id": r.tatvapada_author_id,
                "tatvapadakarara_hesaru": r.author_name
            }
            for r in results
        ]

        return {
            "items": items,
            "total": total,
            "offset": offset,
            "limit": limit
        }

    @staticmethod
    def populate_from_tatvapada(price: float = 100.0):
        """
        Populate shopping catalog from Tatvapada table (unique by author + samputa).
        """
        session = db_instance.session

        # Unique books by author + samputa, pick min tatvapadakosha_sheershike
        unique_books = (
            session.query(
                Tatvapada.tatvapada_author_id,
                Tatvapada.samputa_sankhye,
                func.min(Tatvapada.tatvapadakosha_sheershike).label("tatvapadakosha_sheershike")
            )
            .group_by(Tatvapada.tatvapada_author_id, Tatvapada.samputa_sankhye)
            .all()
        )

        added = 0
        for book in unique_books:
            exists = session.query(ShoppingTatvapada).filter_by(
                tatvapada_author_id=book.tatvapada_author_id,
                samputa_sankhye=book.samputa_sankhye
            ).first()
            if not exists:
                new_item = ShoppingTatvapada(
                    tatvapada_author_id=book.tatvapada_author_id,
                    samputa_sankhye=book.samputa_sankhye,
                    price=price,
                    tatvapadakosha_sheershike=book.tatvapadakosha_sheershike
                )
                session.add(new_item)
                added += 1

        session.commit()
        return {"message": f"{added} books added to shopping catalog"}
