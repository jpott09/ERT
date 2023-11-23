from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, String, Integer, inspect
import datetime
from Classes.LoggableClass import LoggableClass as Class
import uuid

Base = declarative_base()

class Database(Class):
    def __init__(self):
        super().__init__("DB","DB ERR","DB WRN")
        global Base
        self.db_path:str = 'database.db'
        self.engine = create_engine(f'sqlite:///{self.db_path}?timeout=45', echo=False, pool_size=20, max_overflow=30)
        self.Session:scoped_session = scoped_session(sessionmaker(bind=self.engine))
        self.Base = Base
        #create the tables
        self.createTables()

    def getSession(self) -> scoped_session:
        """Returns a scoped session"""
        return self.Session()
    
    def createTables(self) -> None:
        """Called on init.  Creates tables if they do not exist"""
        self.log("Creating tables")
        self.Base.metadata.create_all(self.engine,checkfirst=True)

    def generateUniqueID(self) -> str:
        """Generate a random unique ID with uuid4"""
        unique_id:str = str(uuid.uuid4())

    def createTMDB(self,
                   db_id:str,
                   episode_name:str,
                   episode_id:str,
                   episode_number:int,
                   episode_overview:str,
                   episode_still_path:str,
                   season_number:int,
                   season_id:str,
                   number_of_episodes:int,
                   series_name:str,
                   series_original_name:str,
                   series_overview:str,
                   series_poster_path:str,
                   series_id:int,
                   number_of_seasons:int,
                   search_string:str) -> None:
        """Create a TMDB object"""
        session = self.getSession()
        tmdb = TMDB(db_id=db_id,
                    episode_name=episode_name,
                    episode_id=episode_id,
                    episode_number=episode_number,
                    episode_overview=episode_overview,
                    episode_still_path=episode_still_path,
                    season_number=season_number,
                    season_id=season_id,
                    number_of_episodes=number_of_episodes,
                    series_name=series_name,
                    series_original_name=series_original_name,
                    series_overview=series_overview,
                    series_poster_path=series_poster_path,
                    series_id=series_id,
                    number_of_seasons=number_of_seasons,
                    search_string=search_string
                    )
        session.add(tmdb)
        session.commit()
        session.close()



class BaseModel(Base):
    __abstract__ = True
    db_id:str = Column(String, primary_key=True, unique=True)
    created_at:DateTime = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at:DateTime = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class TMDB(BaseModel):
    __tablename__ = "tmbd"
    #episode data
    episode_name:str = Column(String, nullable=False)
    episode_id:str = Column(String, nullable=False) #use this for db_id ?
    episode_number:int = Column(Integer, nullable=False)
    episode_overview:str = Column(String, nullable=True)
    episode_still_path:str = Column(String, nullable=True)
    #season data
    season_number:int = Column(Integer, nullable=False)
    season_id:str = Column(String, nullable=False)
    number_of_episodes:int = Column(Integer, nullable=False)
    #series data
    series_name:str = Column(String, nullable=False)
    series_original_name:str = Column(String, nullable=False)
    series_overview:str = Column(String, nullable=True)
    series_poster_path:str = Column(String, nullable=True)
    series_id:int = Column(Integer, nullable=False)
    number_of_seasons:int = Column(Integer, nullable=False)
    #search data
    search_string:str = Column(String, nullable=False)

    def __repr__(self):
        return f"<TMDB(series_name = {self.series_name}, series_id = {self.series_id}, season_number = {self.season_number}, episode_number = {self.episode_number})>"

