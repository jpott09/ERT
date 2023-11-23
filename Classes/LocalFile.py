from typing import List, Dict

class LocalFile:
    """Local file object"""
    def __init__(self,name_on_disc:str):
        self.name_on_disc:str = name_on_disc
        self.filepath:str = ""

class Series(LocalFile):
    """Series object"""
    def __init__(self,name:str):
        super().__init__(name)
        self.seasons:List[Season] = []

    def getSeasons(self) -> List[object]:
        return self.seasons

class Season(LocalFile):
    """Season object"""
    def __init__(self,name:str):
        super().__init__(name)
        self.episodes:List[Episode] = []
        self.number:int = -1
    
    def getEpisodes(self) -> List[object]:
        return self.episodes

class Episode(LocalFile):
    """Episode object"""
    def __init__(self,name:str):
        super().__init__(name)
        self.extension:str = ""     #extension of the file
        self.original_name:str = "" #name without extension