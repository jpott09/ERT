from typing import List, Dict
from Classes.Filters import Filter

class LocalFile:
    """Local file object"""
    def __init__(self,name_on_disc:str):
        self.name_on_disc:str = name_on_disc
        """Full name of file on disc (without path)"""
        self.formatted_name:str = ""
        """Filename after running through filters"""
        self.proposed_name:str = ""
        """Proposed name after querying and comparing to API/database"""
        self.filepath:str = ""
        """Full filepath"""
        self.filter:Filter = Filter()
        """Filter object for formatting names"""

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
        self.formatted_name = self.filter.seriesName(self.name_on_disc)

    def getSeasons(self) -> List[object]:
        return self.seasons
    
#Season
class Season(LocalFile):
    """Season object"""
    def __init__(self,name:str):
        super().__init__(name)
        self.episodes:List[Episode] = []
        self.formatted_name = self.filter.seasonName(self.name_on_disc)
        # unchanged if 'season' is not in the folder name
        self.season_number:int = self.filter.determineSeasonNumber(self.formatted_name)
        # -1 if no season number found
    
    def getEpisodes(self) -> List[object]:
        return self.episodes
    
    def __formatName(self) -> None:
        """Format the season name"""
        self.formatted_name = self.filter.seasonName(self.name_on_disc)

    def __determineSeasonNumber(self) -> None:
        """Determine the season number"""
        #get the numbers after season (from formatted name)
        digits:List[str] = [char for char in self.formatted_name[6:] if char.isdigit()]
        if len(digits) > 0:
            self.number = int("".join(digits))
        else:
            self.number = -1

#Episode
class Episode(LocalFile):
    """Episode object"""
    def __init__(self,name:str):
        super().__init__(name)
        self.extension:str = ""
        """Extension of the file"""
        self.original_name:str = ""
        """Name without Extensions"""
        self.formatted_name:str = self.filter.episodeName(self.original_name)
        """Name after running through the filters"""

ep = Episode("test")
ep.original_name