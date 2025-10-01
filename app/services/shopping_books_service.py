import os
import csv
from datetime import datetime
from typing import Optional, List, Tuple

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

    # ---------------- CRUD ----------------
    def create_book(self, cover_file=None, **kwargs) -> Tuple[Optional[ShoppingBooks], Optional[str]]:
        """Create a new book."""
        if not kwargs.get("title"):
            return None, "Title is required."
        if not kwargs.get("price"):
            return None, "Price is required."
        kwargs.pop("id", None)

        kwargs = self._sanitize_numeric_fields(kwargs)
        kwargs["publication_date"] = self._safe_date(kwargs.get("publication_date"))

        # Handle cover upload
        if cover_file and allowed_file(cover_file.filename):
            try:
                filename = secure_filename(cover_file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                cover_file.save(filepath)
                kwargs["cover_image_url"] = f"/{UPLOAD_FOLDER}/{filename}"
            except Exception as e:
                return None, f"Cover upload failed: {e}"

        try:
            book = ShoppingBooks(**kwargs)
            self.db.session.add(book)
            self.db.session.commit()
            self.db.session.refresh(book)
            return book, None
        except SQLAlchemyError as e:
            self.db.session.rollback()
            return None, f"Database error: {str(e)}"

    def get_book_by_id(self, book_id: int) -> Optional[ShoppingBooks]:
        return self.db.session.get(ShoppingBooks, book_id)

    def update_book(self, book_id: int, cover_file=None, **kwargs) -> Tuple[Optional[ShoppingBooks], Optional[str]]:
        """Update an existing book."""
        book = self.get_book_by_id(book_id)
        if not book:
            return None, "Book not found."

        kwargs = self._sanitize_numeric_fields(kwargs)
        kwargs["publication_date"] = self._safe_date(kwargs.get("publication_date"))

        # Handle cover upload
        if cover_file and allowed_file(cover_file.filename):
            try:
                filename = secure_filename(cover_file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                cover_file.save(filepath)
                book.cover_image_url = f"/{UPLOAD_FOLDER}/{filename}"
            except Exception:
                pass

        # Update fields dynamically
        for key, value in kwargs.items():
            if hasattr(book, key):
                setattr(book, key, value)

        book.updated_at = ist_now()

        try:
            self.db.session.commit()
            self.db.session.refresh(book)
            return book, None
        except SQLAlchemyError as e:
            self.db.session.rollback()
            return None, f"Database error: {str(e)}"

    def delete_book(self, book_id: int) -> Tuple[bool, Optional[str]]:
        """Delete a book by ID."""
        book = self.get_book_by_id(book_id)
        if not book:
            return False, "Book not found."

        # Delete cover file
        if book.cover_image_url:
            try:
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

    # ---------------- List / Search ----------------
    def list_books(self, search_word: str = "", limit: int = 10, offset: int = 0) -> Tuple[int, int, list]:
        """List books with search and pagination."""
        query = self.db.session.query(ShoppingBooks)
        total_count = query.count()

        if search_word and search_word.strip():
            like_pattern = f"%{search_word.strip()}%"
            query = query.filter(
                (ShoppingBooks.title.ilike(like_pattern)) |
                (ShoppingBooks.subtitle.ilike(like_pattern)) |
                (ShoppingBooks.author_name.ilike(like_pattern))
            )

        filtered_count = query.count()
        books = query.order_by(ShoppingBooks.created_at.desc()).offset(offset).limit(limit).all()
        return total_count, filtered_count, books

    # ---------------- Bulk Upload ----------------
    def bulk_upload_from_csv(self, csv_file_path: str) -> Tuple[List[ShoppingBooks], List[str]]:
        """Bulk upload books from a CSV file."""
        uploaded_books, errors = [], []

        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader, start=1):
                kwargs = {k: v for k, v in row.items() if v is not None and v.strip() != ""}
                kwargs = self._sanitize_numeric_fields(kwargs)
                kwargs["publication_date"] = self._safe_date(kwargs.get("publication_date"))

                cover_file_name = kwargs.pop("cover_file_name", None)
                if cover_file_name:
                    cover_path = os.path.join(UPLOAD_FOLDER, secure_filename(cover_file_name))
                    if os.path.exists(cover_path):
                        kwargs["cover_image_url"] = f"/{UPLOAD_FOLDER}/{cover_file_name}"

                try:
                    book = ShoppingBooks(**kwargs)
                    self.db.session.add(book)
                    uploaded_books.append(book)
                except Exception as e:
                    errors.append(f"Row {i}: {str(e)}")

        try:
            self.db.session.commit()
            for book in uploaded_books:
                self.db.session.refresh(book)
        except SQLAlchemyError as e:
            self.db.session.rollback()
            errors.append(f"Database commit error: {str(e)}")

        return uploaded_books, errors

    # ---------------- Auto-create from Tatvapada ----------------
    def auto_create_from_tatvapada(self, default_price: float) -> Tuple[int, int]:
        """Auto-create ShoppingBooks from Tatvapada table."""
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

        for sheershike, author_id in rows:
            author = self.db.session.get(TatvapadaAuthorInfo, author_id)
            if not author:
                continue

            existing = (
                self.db.session.query(ShoppingBooks)
                .filter(
                    ShoppingBooks.title == sheershike,
                    ShoppingBooks.author_name == author.tatvapadakarara_hesaru
                )
                .first()
            )
            if existing:
                skipped += 1
                continue

            book = ShoppingBooks(
                title=sheershike,
                author_name=author.tatvapadakarara_hesaru,
                price=default_price,
                discount_price=None,
                stock_quantity=0,
                number_of_pages=None,
                description=None,
                subtitle=None,
                publisher_name=None,
                language=None,
                cover_image_url=None,
                created_at=ist_now(),
                updated_at=ist_now()
            )
            self.db.session.add(book)
            created += 1

        try:
            self.db.session.commit()
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise RuntimeError(f"Failed to auto-create books: {str(e)}")

        return created, skipped

    # ---------------- Helpers ----------------
    def _sanitize_numeric_fields(self, kwargs: dict) -> dict:
        """Ensure numeric fields are proper types, defaulting safely."""
        for field in ["price", "discount_price"]:
            if field in kwargs:
                try:
                    kwargs[field] = float(kwargs[field])
                except (ValueError, TypeError):
                    kwargs[field] = 0.0 if field == "price" else None

        for field in ["stock_quantity", "number_of_pages"]:
            if field in kwargs:
                try:
                    kwargs[field] = int(kwargs[field])
                except (ValueError, TypeError):
                    kwargs[field] = 0

        return kwargs

    def _safe_date(self, value: Optional[str]):
        """Convert string to datetime, safely."""
        if not value or value.strip() == "":
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
