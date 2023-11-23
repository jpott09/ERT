import re as regex
from Classes.LoggableClass import LoggableClass

class Filter(LoggableClass):
    def __init__(self):
        super().__init__("FLT","FLT ERR","FLT WRN")
        
    def seriesName(self,season_name:str) -> str:
        """Returns a formatted season name"""
        season_name = self.basicFormatting(season_name)
        #remove any instance of (####) or [####] or {####} or '####' or "####"
        season_name = regex.sub(r'\(\d{4}\)|\[\d{4}\]|\{\d{4}\}|\'\d{4}\'|\"\d{4}\"','',season_name)
        return season_name
    
    def seasonName(self,season_name:str) -> str:
        """Returns a formatted season name"""
        pass

    def episodeName(self, episode_name:str) -> str:
        """Returns a formatted episode name"""
        pass

    def basicFormatting(self,string:str) -> str:
        """Returns a formatted string with basic formatting like .strip()"""
        string = string.strip()
        return string
    
