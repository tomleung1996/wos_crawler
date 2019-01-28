from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time

Base = declarative_base()

def get_engine(db_path=None):
    if not db_path:
        timestamp = str(time.strftime('%Y-%m-%d-%H.%M.%S',time.localtime(time.time())))
        engine = create_engine('sqlite:///wos_crawler_result_{}.db'.format(timestamp))
    else:
        engine = create_engine('sqlite:///{}'.format(db_path))
    return engine


def get_session(engine, auto_flush = True):
    Session = sessionmaker(bind=engine, autoflush=auto_flush)
    session = Session()
    return session
