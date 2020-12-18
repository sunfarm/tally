import datetime

from sqlalchemy import create_engine
from sqlalchemy import distinct
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql import func

from tally.models import Tally, Base

conn_string = "sqlite:///tally.db"
# conn_string = "sqlite:///:memory:"
engine = create_engine(conn_string)
Base.metadata.create_all(engine) # here we create all tables
Session = sessionmaker(bind=engine)
session = Session()

def add_tally(label):
    new_tally = Tally(label=label)

    session.add(new_tally)
    session.commit()

    return new_tally

def get_count(label=None):
    now = datetime.datetime.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(datetime.timezone.utc)
    end = (start + datetime.timedelta(days=1)).astimezone(datetime.timezone.utc)

    count = session.query(Tally).filter(
        Tally.label == label,
        Tally.time_created >= start,
        Tally.time_created < end,
    ).count()
    return count

def get_counts_today():
    now = datetime.datetime.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(datetime.timezone.utc)
    end = (start + datetime.timedelta(days=1)).astimezone(datetime.timezone.utc)

    # counts = session.query(Tally).filter(
    #     Tally.time_created >= start,
    #     Tally.time_created < end,
    # )
    # .group_by(Tally.label)
    # .count()

    counts = session.query(func.count(distinct(Tally.label))).all()


    return counts

def is_today(date: datetime.datetime):
    now = datetime.datetime.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    end = start + datetime.timedelta(days=1)
    return start <= date and date < end