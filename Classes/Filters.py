import re as regex
from Classes.LoggableClass import LoggableClass
from typing import List

class Filter(LoggableClass):
    def __init__(self):
        super().__init__("FLT","FLT ERR","FLT WRN")
        
    def seriesName(self,series_name:str) -> str:
        """Returns a formatted season name"""
        original_name:str = series_name
        series_name = self.__basicFormatting(series_name)
        series_name = self.__removeYear(series_name)
        #log any changes
        if original_name != series_name:
            self.log(f"Series name changed from '{original_name}' to '{series_name}'")
        return series_name
    
    def seasonName(self,season_name:str) -> str:
        """Returns a formatted season name"""
        original_name:str = season_name
        season_name = self.__basicFormatting(season_name)
        season_name = self.__removeYear(season_name)
        digits:List[str] = [char for char in season_name if char.isdigit()]
        if len(digits) > 0:
            season_number = int("".join(digits))
            season_number_str = str(season_number)
            while(len(season_number_str) < 2):
                season_number_str = "0" + season_number_str
            season_name = f"Season {season_number_str}"
        #log any changes
        if original_name != season_name:
            self.log(f"Season name changed from '{original_name}' to '{season_name}'")
        return season_name
            
    def determineSeasonNumber(self,formatted_season_name:str) -> int:
        """Returns the index of the season number.  Returns -1 of none found"""
        digits:List[str] = [char for char in formatted_season_name[6:] if char.isdigit()]
        if len(digits) > 0:
            number = int("".join(digits))
        else:
            number = -1
        #log determination
        self.log(f"Season number for '{formatted_season_name}' determined to be '{number}'")
        return number

    def episodeName(self, episode_name:str) -> str:
        """Returns a formatted episode name"""
        episode_name = self.__basicFormatting(episode_name)
        episode_name = self.__removeYear(episode_name)
        # TODO determine if this is necessary.  Likely will be pulling details from the TMDB API
        # and then trying to determine which episode matches that data, rather than the other way around
        return episode_name

    def __basicFormatting(self,string:str) -> str:
        """Returns a formatted string with basic formatting like .strip()"""
        string = string.strip()
        return string
    
    def __removeYear(self,string:str) -> str:
        """Returns a string with any year removed"""
        #remove any instance of (####) or [####] or {####} or '####' or "####"
        string = regex.sub(r'\(\d{4}\)|\[\d{4}\]|\{\d{4}\}|\'\d{4}\'|\"\d{4}\"','',string)
        return string
    
