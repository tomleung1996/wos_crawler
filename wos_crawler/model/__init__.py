from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time

Base = declarative_base()

timestamp = str(time.strftime('%Y-%m-%d-%H.%M.%S',time.localtime(time.time())))
engine = create_engine('sqlite:///wos_crawler_result_{}.db'.format(timestamp))


def loadSession():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
