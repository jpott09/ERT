"""
TMDB manager: used to query database, and then API for series data
LST manager: used to scrape local series data.
ERT (this class) iterate through LST results, and query TMDB manager for series data
    Formatting report:
    -identify episodes missing any formatting
    -identify episodes missing 'correct' formatting
    -generate revised formatted names for episodes
    -iterate through report and check if user wants to rename episodes
    -other stuff probably
"""
from Classes.LoggableClass import LoggableClass
from Classes.TMDB import TMDBManager
from Classes.Filters import Filter
from Classes.LST import LST
from typing import List, Dict
from Classes.LocalFile import Series, Season, Episode
#database
from Classes.Database import Database, TMDB

class ERT(LoggableClass):
    def __init__(self,database:Database, tmdb_api_key:str):
        #super init
        super().__init__("ERT","ERT ERR","ERT WRN")
        #database stuff
        self.database:Database = database
        #tmdb stuff
        self.tmdb_api_key:str = tmdb_api_key
        #load TMDB 
        tmdb = TMDBManager(self.database, tmdb_api_key)
        #init Local Scraper Tool
        self.lst = LST()
        self.local_series_data:List[Series] = self.lst.getData()
