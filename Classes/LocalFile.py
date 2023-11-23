from typing import List, Dict
from Classes.Filters import Filter

class LocalFile:
    """Local file object"""
    def __init__(self,name_on_disc:str):
        self.name_on_disc:str = name_on_disc    #the name of the file on disc
        self.formatted_name:str = ""            #the name after running through the filters
        self.proposed_name:str = ""             #the name after querying database/API
        self.filepath:str = ""                  #the full path to the file
        self.filter:Filter = Filter()           #filter object

    def getProposedName(self) -> str:
        """Returns the proposed name"""
        return self.formatted_name

#----------------------------------------------------------------------------#
#Series
class Series(LocalFile):
    """Series object"""
    def __init__(self,name:str):
        super().__init__(name)
        self.seasons:List[Season] = []
        self.__formatName()

    def getSeasons(self) -> List[object]:
        return self.seasons
    
    def __formatName(self) -> None:
        """Format the series name"""
        self.formatted_name = self.filter.seriesName(self.name_on_disc)
#Season
class Season(LocalFile):
    """Season object"""
    def __init__(self,name:str):
        super().__init__(name)
        self.episodes:List[Episode] = []
        self.number:int = -1
        self.__formatName()
    
    def getEpisodes(self) -> List[object]:
        return self.episodes
    
    def __formatName(self) -> None:
        """Format the season name"""
        self.formatted_name = self.filter.seasonName(self.name_on_disc)

#Episode
class Episode(LocalFile):
    """Episode object"""
    def __init__(self,name:str):
        super().__init__(name)
        self.extension:str = ""     #extension of the file
        self.original_name:str = "" #name without extension -> This will be used for formatting and queries
        self.__formatName()

    def __formatName(self) -> None:
        """Format the episode name"""
        self.formatted_name = self.filter.episodeName(self.original_name)

    def getProposedName(self) -> str:
        return self.formatted_name + "." + self.extension