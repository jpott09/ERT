import requests
from Classes.LoggableClass import LoggableClass
from Classes.Filesystem import Filesystem
from typing import List, Dict
import os
import json
#Database
from Classes.Database import Database, TMDB
#filter
from Classes.Filters import Filter


class TMDBManager(LoggableClass):
    """Class for getting data from the TMDB API and the database"""
    def __init__(self,database:Database,api_key:str):
        #super init
        super().__init__(prefix="TMDB",prefix_error="TMDB ERR",prefix_warning="TMDB WRN")
        #database
        self.database:Database = database
        #api
        self.api_key:str = api_key
        self.api:API = API(api_key=self.api_key)
        #filter
        self.filter:Filter = Filter()
        #error tracking
        self.error_series_list:List[str] = []

    def getSeries(self,series_name:str) -> List[TMDB]:
        """Get the series data for the given series name"""
        #filter the series_name
        series_name:str = self.filter.seriesName(series_name)
        #check if the series is already in the database
        session = self.database.getSession()
        #see if the series_name is a search_string in the database
        series_list:List[TMDB] = session.query(TMDB).filter(TMDB.search_string == series_name).all()
        #if the series_name is not a search_string, see if it is a series_name
        if not series_list:
            series_list:List[TMDB] = session.query(TMDB).filter(TMDB.series_name == series_name).all()
            #update the search_string if this yields results
            if series_list:
                for series in series_list:
                    series.search_string = series_name
                    self.logWarning(f"getSeries(): Updating search_string for '{series_name}' to '{series_name}'")
                session.commit()
        session.close()
        #if the series is not in the database, get the data from the API
        if not series_list:
            series_data:dict = self.api.getSeriesData(series_name)
            if not series_data:
                self.logError(f"getSeries(): No series data for '{series_name}'")
                return []
            #add the series to the database
            if not self.addSeriesToDatabase(series_data,series_name):
                self.logError(f"getSeries(): Could not add API results for series '{series_name}' to database")
                return []
            #get the series from the database
            session = self.database.getSession()
            series_list:List[TMDB] = session.query(TMDB).filter(TMDB.series_name == series_name).all()
            session.close()
        if not series_list:
            self.logError(f"Could not get series data for {series_name} from database, or TMDB API")
            self.error_series_list.append(f"{series_name}: Could not get series data from database, or TMDB API")
            return []
        return series_list
    
    def getErrors(self) -> List[str]:
        errors:List[str] = []
        #add series errors
        for series_name in self.error_series_list:
            errors.append(f"Series: {series_name}")
        #add other errors...
        return errors

    def addSeriesToDatabase(self,series_data:dict,search_string:str) -> bool:
        """Add the json data for the given series to the database"""
        add_count:int = 0
        total_items:int = 0
        for season in series_data['seasons']:
            for episode in season['episodes']:
                total_items += 1
                #generate a unique database ID [db_id]
                #series_id + season_id + episode_id
                db_id:str = f"{series_data['id']}-{season['id']}-{episode['id']}"
                #check if the series is already in the database
                session = self.database.getSession()
                tmdb:TMDB = session.query(TMDB).filter(TMDB.db_id == db_id).first()
                session.close()
                if tmdb:
                    self.logWarning(f"addSeriesToDatabase(): Series '{series_data['name']}' is already in the database")
                    continue
                #add the series to the database
                try:
                    self.database.createTMDB(
                        db_id=db_id,
                        episode_name=episode['name'],
                        episode_id=episode['id'],
                        episode_number=episode['episode_number'],
                        episode_overview=episode['overview'],
                        episode_still_path=episode['still_path'],
                        season_number=season['season_number'],
                        season_id=season['id'],
                        number_of_episodes=series_data['number_of_episodes'],
                        series_name=series_data['name'],
                        series_original_name=series_data['original_name'],
                        series_overview=series_data['overview'],
                        series_poster_path=series_data['poster_path'],
                        series_id=series_data['id'],
                        number_of_seasons=series_data['number_of_seasons'],
                        search_string=search_string
                    )
                    add_count += 1
                except Exception as e:
                    self.logError(f"addSeriesToDatabase(): Error adding series '{series_data['name']}' to database: {e}")
                    continue
        if add_count == 0:
            self.logError(f"addSeriesToDatabase(): No series added to database")
            return False
        self.log(f"addSeriesToDatabase(): Added {add_count}/{total_items} items to database.")
        return True

class API(LoggableClass):
    """Class for interfacing with the TMDB API.  Created by the Manager class"""
    def __init__(self,
                 api_key:str,
                 logging=True,
                 logging_warnings=True,
                 logging_errors=True):
        #super init
        self.prefix:str = "TMDB-API"
        self.prefix_warning:str = "TMDB-API WRN"
        self.prefix_error:str = "TMDB-API ERR"
        super().__init__(prefix=self.prefix,
                         prefix_warning=self.prefix_warning,
                         prefix_error=self.prefix_error,
                         logging=logging,
                         log_warning=logging_warnings,
                         log_errors=logging_errors)
        #api
        self.api_key:str = api_key
        self.api_url:str = "https://api.themoviedb.org/3"
        self.api_image_url:str = "https://image.tmdb.org/t/p/original"

    def sendGet(self,url:str,params:str=None,headers:str=None)->dict or None:
        """Sends a GET request to the given URL.  Returns the response as a dictionary, or None if unsuccessful."""
        try:
            response = requests.get(url,params=params,headers=headers).json()
            return response
        except Exception as e:
            self.logError(f"Error sending GET request to {url}: {e}")
            self.logError(f"Params: {params}")
            self.logError(f"Headers: {headers}")
            return None
        
    def sendPost(self,url:str,params:str=None,headers:str=None)->dict or None:
        """Sends a POST request to the given URL.  Returns the response as a dictionary, or None if unsuccessful."""
        try:
            response = requests.post(url,params=params,headers=headers).json()
            return response
        except Exception as e:
            self.logError(f"Error sending POST request to {url}: {e}")
            self.logError(f"Params: {params}")
            self.logError(f"Headers: {headers}")
            return None

    def __stepOne(self,series_name:str) -> dict:
        """Get the series ID, Series Name, Overview, original name, and poster path for the series"""
        # Construct the search URL
        url:str = f"{self.api_url}/search/tv?api_key={self.api_key}&query={series_name}"
        # Make the search request
        response_data:dict = self.sendGet(url)
        if not response_data:
            self.logError(f"__stepOne(): No response data for '{series_name}'")
            return None
        try:
            results:List[dict] = response_data.get('results',None)
            if not results:
                self.logError(f"__stepOne(): No results found for '{series_name}'")
                return None
            result:dict = results[0]
            #get the series ID
            id:int = result.get('id',None)
            name:str = result.get('name',None)
            original_name:str = result.get('original_name',"None")
            overview:str = result.get('overview',"None")
            poster_path:str = result.get('poster_path',"None")
            if not id:
                self.logError(f"__stepOne(): No ID found for '{series_name}'")
                return None
            if not name:
                self.logError(f"__stepOne(): No name found for '{series_name}'")
                return None
            data:dict = {
                'id':id,
                'name':name,
                'original_name':original_name,
                'overview':overview,
                'poster_path':poster_path
            }
            return data
        except Exception as e:
            self.logError(f"Error getting series ID for '{series_name}': {e}")
            return None

    def __stepTwo(self,step_one_data:dict) -> dict:
        """Take the data from step one, and get the Season count and episode count, and add it to the data"""
        # Construct the search URL
        series_id:int = step_one_data.get('id',None)
        url:str = f"{self.api_url}/tv/{series_id}?api_key={self.api_key}"
        # Make the search request
        response_data:dict = self.sendGet(url)
        if not response_data:
            self.logError(f"__stepTwo(): No response data for '{series_id}'")
            return None
        try:
            number_of_seasons:int = response_data.get('number_of_seasons',None)
            number_of_episodes:int = response_data.get('number_of_episodes',None)
            step_two_data = step_one_data
            step_two_data['number_of_seasons'] = number_of_seasons
            step_two_data['number_of_episodes'] = number_of_episodes
            return step_two_data
        except Exception as e:
            self.logError(f"Error getting step two data for '{series_id}': {e}")
            return None
        
    def __stepThree(self,step_two_data:dict) -> dict:
        """Take the data from step two, and get the episode data for each season, and add it to the data"""
        # Construct the search URL
        series_id:int = step_two_data.get('id',None)
        number_of_seasons:int = step_two_data.get('number_of_seasons',None)
        step_three_data:dict = step_two_data
        step_three_data['seasons'] = []
        for i in range(1,number_of_seasons+1):
            url:str = f"{self.api_url}/tv/{series_id}/season/{i}?api_key={self.api_key}"
            # Make the search request
            response_data:dict = self.sendGet(url)
            if not response_data:
                self.logError(f"__stepThree(): No response data for '{series_id}'")
                continue
            #create a season data object
            episodes:List[dict] = response_data.get('episodes',None)
            if not episodes:
                self.logError(f"__stepThree(): No episodes found for '{series_id}'")
                continue
            #create a season data object
            season_data:dict = {}
            season_data['season_number']:int = i
            season_data['id']:str = response_data.get('_id','None')
            season_data['episodes']:List[dict] = []

            for episode in episodes:
                episode_data:dict = {}
                episode_data['name']:str = episode.get('name','None')
                episode_data['id']:str = episode.get('_id','None')
                episode_data['episode_number']:int = episode.get('episode_number','None')
                episode_data['overview']:str = episode.get('overview','None')
                episode_data['still_path']:str = episode.get('still_path','None')
                #add the episode data to the season data
                season_data['episodes'].append(episode_data)
            step_three_data['seasons'].append(season_data)
        #verify that the number of seasons is correct
        if len(step_three_data['seasons']) != number_of_seasons:
            self.logError(f"__stepThree(): The number of seasons for '{series_id}' is incorrect")
        #verify that the number of episodes is correct
        number_of_episodes:int = 0
        for season in step_three_data['seasons']:
            number_of_episodes += len(season['episodes'])
        if number_of_episodes != step_three_data['number_of_episodes']:
            self.logError(f"__stepThree(): The number of episodes for '{series_id}' is incorrect")
        return step_three_data
            
    def getSeriesData(self,series_name:str) -> dict:
        """Build a dictionary object of information about the given series and return it."""
        step_one_data:dict = self.__stepOne(series_name)
        if not step_one_data:
            self.logError(f"buildSeriesData(): No step one data for '{series_name}'")
            return None
        step_two_data:dict = self.__stepTwo(step_one_data)
        if not step_two_data:
            self.logError(f"buildSeriesData(): No step two data for '{series_name}'")
            return None
        step_three_data:dict = self.__stepThree(step_two_data)
        if not step_three_data:
            self.logError(f"buildSeriesData(): No step three data for '{series_name}'")
            return None
        return step_three_data
    


