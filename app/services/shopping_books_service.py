import csv
import os
from datetime import datetime
from typing import Optional, Tuple, List
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from app.config.database import db_instance
from app.models.tatvapada import ShoppingBooks, ist_now, Tatvapada, TatvapadaAuthorInfo

UPLOAD_FOLDER = "uploads/covers"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class ShoppingBooksService:
    def __init__(self):
        self.db = db_instance

    def _sanitize_numeric_fields(self, kwargs: dict) -> dict:
        """Ensure numeric fields are proper types + enforce discount rules."""
        for field in ["price", "discount_price", "rating"]:
            if field in kwargs and kwargs[field] not in [None, ""]:
                try:
                    kwargs[field] = float(kwargs[field])
                except (ValueError, TypeError):
                    kwargs[field] = None

        if "stock_quantity" in kwargs:
            try:
                kwargs["stock_quantity"] = int(kwargs["stock_quantity"])
            except:
                kwargs["stock_quantity"] = 0

        if "number_of_pages" in kwargs:
            try:
                kwargs["number_of_pages"] = int(kwargs["number_of_pages"])
            except:
                kwargs["number_of_pages"] = None

        return kwargs

    def _safe_date(self, value: Optional[str]):
        """Convert string to datetime safely, returns None if invalid."""
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return None

    def _apply_price_rules(self, kwargs):
        """E-commerce pricing logic."""
        price = kwargs.get("price")
        discount = kwargs.get("discount_price")

        if price is None:
            return False, "Price is required."

        if discount in [None, "", 0]:
            kwargs["discount_price"] = None
            return True, None

        if discount >= price:
            return False, "Discount price must be less than actual price."

        return True, None

    def _save_cover(self, cover_file, book_id: int) -> Optional[str]:
        """Save cover image file for the book and return URL path."""
        if cover_file and allowed_file(cover_file.filename):
            ext = cover_file.filename.rsplit(".", 1)[1].lower()
            filename = secure_filename(f"{book_id}.{ext}")
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            # Delete old file if exists to avoid stale files
            if os.path.exists(filepath):
                os.remove(filepath)

            cover_file.save(filepath)

            # Return relative URL path for web usage
            return f"/{UPLOAD_FOLDER}/{filename}"
        return None

    def create_book(self, cover_file=None, **kwargs):
        if not kwargs.get("title"):
            return None, "Title is required."
        if not kwargs.get("price"):
            return None, "Price is required."

        kwargs.pop("id", None)
        kwargs = self._sanitize_numeric_fields(kwargs)
        kwargs["publication_date"] = self._safe_date(kwargs.get("publication_date"))

        # Step 1 — Create book record first (without cover)
        book = ShoppingBooks(**kwargs)

        try:
            self.db.session.add(book)
            self.db.session.commit()
            self.db.session.refresh(book)
        except SQLAlchemyError as e:
            self.db.session.rollback()
            return None, f"Database error: {str(e)}"

        # Step 2 — Handle cover file using book ID
        if cover_file and allowed_file(cover_file.filename):
            try:
                cover_url = self._save_cover(cover_file, book.id)
                if cover_url:
                    book.cover_image_url = cover_url
                    self.db.session.commit()
            except Exception as e:
                self.db.session.rollback()
                return None, f"Cover upload failed: {e}"

        return book, None

    def get_book_by_id(self, book_id: int) -> Optional["ShoppingBooks"]:
        return self.db.session.get(ShoppingBooks, book_id)

    def update_book(self, book_id, cover_file=None, **kwargs):
        book = self.get_book_by_id(book_id)
        if not book:
            return None, "Book not found."

        kwargs = self._sanitize_numeric_fields(kwargs)
        kwargs["publication_date"] = self._safe_date(kwargs.get("publication_date"))

        # Update normal fields
        for key, value in kwargs.items():
            if hasattr(book, key):
                setattr(book, key, value)

        book.updated_at = ist_now()

        # Update cover image
        if cover_file and allowed_file(cover_file.filename):
            try:
                # Delete old cover image file if exists
                if book.cover_image_url:
                    old_path = book.cover_image_url.lstrip("/")
                    if os.path.exists(old_path):
                        os.remove(old_path)

                cover_url = self._save_cover(cover_file, book.id)
                if cover_url:
                    book.cover_image_url = cover_url
            except Exception as e:
                return None, f"Cover upload failed: {e}"

        try:
            self.db.session.commit()
            self.db.session.refresh(book)
            return book, None
        except SQLAlchemyError as e:
            self.db.session.rollback()
            return None, f"Database error: {str(e)}"

    def delete_book(self, book_id: int) -> Tuple[bool, Optional[str]]:
        book = self.get_book_by_id(book_id)
        if not book:
            return False, "Book not found."

        try:
            if book.cover_image_url:
                file_path = book.cover_image_url.lstrip("/")
                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception:
            pass

        try:
            self.db.session.delete(book)
            self.db.session.commit()
            return True, None
        except SQLAlchemyError as e:
            self.db.session.rollback()
            return False, f"Database error: {str(e)}"

    def list_books(self, search_word: str = "", limit: int = 10, offset: int = 0) -> Tuple[
        int, int, List["ShoppingBooks"]]:
        query = self.db.session.query(ShoppingBooks)
        total_count = query.count()

        if search_word:
            like = f"%{search_word.strip()}%"
            query = query.filter(
                (ShoppingBooks.title.ilike(like)) |
                (ShoppingBooks.subtitle.ilike(like)) |
                (ShoppingBooks.author_name.ilike(like))
            )

        filtered_count = query.count()
        books = query.order_by(ShoppingBooks.created_at.desc()).offset(offset).limit(limit).all()
        return total_count, filtered_count, books

    def bulk_upload_from_csv(self, csv_file_path: str) -> Tuple[List["ShoppingBooks"], List[str]]:
        uploaded, errors = [], []

        with open(csv_file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                kwargs = {k: v.strip() for k, v in row.items() if v}
                kwargs = self._sanitize_numeric_fields(kwargs)
                kwargs["publication_date"] = self._safe_date(kwargs.get("publication_date"))

                ok, err = self._apply_price_rules(kwargs)
                if not ok:
                    errors.append(f"Row {i}: {err}")
                    continue

                try:
                    book = ShoppingBooks(**kwargs)
                    self.db.session.add(book)
                    uploaded.append(book)
                except Exception as e:
                    errors.append(f"Row {i}: {str(e)}")

        try:
            self.db.session.commit()
            for b in uploaded:
                self.db.session.refresh(b)
        except SQLAlchemyError as e:
            self.db.session.rollback()
            errors.append(f"Commit error: {str(e)}")

        return uploaded, errors

    def auto_create_from_tatvapada(self, default_price: float) -> Tuple[int, int]:
        created, skipped = 0, 0

        rows = (
            self.db.session.query(
                Tatvapada.tatvapadakosha_sheershike,
                Tatvapada.tatvapada_author_id
            )
            .distinct()
            .filter(Tatvapada.tatvapadakosha_sheershike.isnot(None))
            .all()
        )

        for title, author_id in rows:
            author = self.db.session.get(TatvapadaAuthorInfo, author_id)
            if not author:
                continue

            exists = self.db.session.query(ShoppingBooks).filter(
                ShoppingBooks.title == title,
                ShoppingBooks.author_name == author.tatvapadakarara_hesaru
            ).first()

            if exists:
                skipped += 1
                continue

            book = ShoppingBooks(
                title=title,
                author_name=author.tatvapadakarara_hesaru,
                price=default_price,
                discount_price=0,
                stock_quantity=0,
                number_of_pages=None,
                created_at=ist_now(),
                updated_at=ist_now()
            )
            self.db.session.add(book)
            created += 1

        self.db.session.commit()
        return created, skipped
