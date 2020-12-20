import datetime
from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy import distinct
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql import func

from tally.models import Tally, Base


class StorageStaticMethods():
    @staticmethod
    def is_today(self, date: datetime.datetime):
        now = datetime.datetime.now()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + datetime.timedelta(days=1)
        is_today = start <= date and date < end
        return is_today

@dataclass
class Storage(StorageStaticMethods):
    """Tally storage class"""
    connection_string: str = "sqlite:///:memory:"
    engine = None
    session = None

    def needs_session(func):
        def wrapper(self, *args, **kwargs):
            if self.engine is None:
                self.engine = create_engine(self.connection_string)
                Base.metadata.create_all(self.engine) # here we create all tables
            if self.session is None:
                Session = sessionmaker(bind=self.engine)
                self.session = Session()

            return func(self, *args, **kwargs)
        return wrapper

    @needs_session
    def add_tally(self, label):
        new_tally = Tally(label=label)

        self.session.add(new_tally)
        self.session.commit()

        return new_tally

    @needs_session
    def get_count(self, label=None):
        now = datetime.datetime.now()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(datetime.timezone.utc)
        end = (start + datetime.timedelta(days=1)).astimezone(datetime.timezone.utc)

        count = self.session.query(Tally).filter(
            Tally.label == label,
            Tally.time_created >= start,
            Tally.time_created < end,
        ).count()
        return count

    @needs_session
    def get_counts_today(self):
        now = datetime.datetime.now()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(datetime.timezone.utc)
        end = (start + datetime.timedelta(days=1)).astimezone(datetime.timezone.utc)

        counts = self.session.query(Tally.label, func.count(Tally.label)).group_by(Tally.label).filter(
            Tally.time_created >= start,
            Tally.time_created < end,
        ).all()

        return counts

    @needs_session
    def get_counts_all(self):
        counts = self.session.query(Tally.label, func.count(Tally.label)).group_by(Tally.label).all()
        return counts
