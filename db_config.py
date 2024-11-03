from sqlalchemy import create_engine, Column, Integer, Date, Boolean, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = 'sqlite:///shift.db'  # путь к вашей базе данных SQLite

engine = create_engine(DATABASE_URL)
Base = declarative_base()

class User(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer)
    name = Column(String)


class Shift(Base):
    __tablename__ = 'n_shift'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Users.id'))
    date = Column(Date, nullable=False)
    shift = Column(String, nullable=False)


class D_shift(Base):
    __tablename__ = 'd_shift'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Users.id'))
    date = Column(Date, nullable=False)
    shift = Column(String, nullable=False)


#Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

#session.commit()
