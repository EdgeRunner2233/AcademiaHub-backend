import os
import sqlalchemy as sql
import sqlalchemy.exc as exc
from src.app import app
from src.util import logger
from flask_sqlalchemy import SQLAlchemy
from typing import Type, TypeVar, Optional, Union, List


app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(app)

T = TypeVar("T", bound="Base")


class Base:
    def save(self) -> bool:
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except exc.IntegrityError:
            logger.error(f"db: save failed: {self}")
            return False

    def delete(self, force: bool = False) -> bool:
        if not force:
            return self.update(is_deleted=True)
        else:
            logger.warning(f"db: deleting record: {self}")
            try:
                db.session.delete(self)
                db.session.commit()
                return True
            except exc.InvalidRequestError:
                logger.error(f"db: delete (force) failed: {self}")
                return False

    def update(self, **values: Union[int, str, bool]) -> bool:
        ins = self.__class__.query_first(id=self.id)
        if ins is None:
            logger.error(f"db: record not found: {self}")
            return False
        for field, value in values.items():
            if hasattr(self, field):
                setattr(self, field, value)
                setattr(ins, field, value)
            else:
                logger.error(f"db: field '{field}' not found in {self}")
        db.session.commit()
        return True

    @classmethod
    def query_first(cls: Type[T], **filter: Union[int, str, bool]) -> Optional[T]:
        if "is_deleted" not in filter:
            filter["is_deleted"] = False
        return cls.query.filter_by(**filter).first()

    @classmethod
    def query_all(cls: Type[T], **filter: Union[int, str, bool]) -> List[T]:
        if "is_deleted" not in filter:
            filter["is_deleted"] = False
        return cls.query.filter_by(**filter).all()


class User(db.Model, Base):
    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String(20))
    is_deleted = sql.Column(sql.Boolean, default=False)

    def __repr__(self):
        return f"<User {self.name}({self.id})>"
