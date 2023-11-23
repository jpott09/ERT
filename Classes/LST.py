
#Local Scraper Tool
from Classes.LoggableClass import LoggableClass
from Classes.Filesystem import Filesystem
from Classes.LocalFile import Series, Season, Episode
from typing import List, Dict
import os

class LST(LoggableClass):
    """Local Series Tool"""
    def __init__(self,root_directory:str,logging=True,logging_warnings=True,logging_errors=True):
        #super init
        self.prefix:str = "LST"
        self.prefix_warning:str = "LST WRN"
        self.prefix_error:str = "LST ERR"
        super().__init__(prefix=self.prefix,
                         prefix_warning=self.prefix_warning,
                         prefix_error=self.prefix_error,
                         logging=logging,
                         log_warning=logging_warnings,
                         log_errors=logging_errors)
        #root directory
        self.root_directory:str = root_directory
        #filesystem
        self.filesystem:Filesystem = Filesystem()
        #filenames to skip
        self.skip_filenames:List[str] = [
            'metadata',
            'folder.jpg',
            'folder.png',
            'commentaries',
            'cover.jpg',
            'logo.png',
            'extras',
            'sample'
        ]
        self.skip_extensions = [
            'png',
            'jpg',
            'jpeg',
            'txt',
            'gif',
            'nfo'
        ]
        #local series data
        self.local_series_data:List[Series] = []
        #scan 
        self.scanLocalSeries()

    def getData(self) -> List[Series]:
        """Returns a list of 'Series' objects, containing 'Season' objects, which contain 'Episode' objects."""
        return self.local_series_data
    
    def scanLocalSeries(self) -> List[Series]:
        """Returns a list of 'Series' objects, containing 'Season' objects, which contain 'Episode' objects."""
        series_list:List[Series] = []
        #get all series directories
        series_directories:List[str] = self.filesystem.getFolders(self.root_directory)
        if len(series_directories) == 0:
            self.logError(f"No series directories found in {self.root_directory}")
            return []
        #------------------------------------------------- SERIES -------------------------------------------------
        for series_folder in series_directories:
            if self.__determineSkip(series_folder):
                self.log(f"Skipping {series_folder}")
                continue
            series_data:Series = Series(series_folder)
            series_data.filepath:str = os.path.join(self.root_directory,series_folder)
            #get all season directories
            season_directories:List[str] = self.filesystem.getFolders(os.path.join(self.root_directory,series_folder))
            if len(season_directories) == 0:
                self.logError(f"No season directories found in {series_folder}")
                continue
            #------------------------------------------------- SEASONS -------------------------------------------------
            for season_folder in season_directories:
                if self.__determineSkip(season_folder):
                    self.log(f"Skipping {season_folder} in {series_folder}")
                    continue
                season_data:Season = Season(season_folder)
                season_data.filepath = os.path.join(self.root_directory,series_folder,season_folder)
                season_data.number = self.__getSeasonNumber(season_folder)
                #get all episode files
                episode_files:List[str] = self.filesystem.getFiles(os.path.join(self.root_directory,series_folder,season_folder))
                if len(episode_files) == 0:
                    self.logError(f"No episode files found in {season_folder}")
                    continue
                #------------------------------------------------- EPISODES -------------------------------------------------
                for episode_file in episode_files:
                    if self.__determineSkip(episode_file):
                        self.log(f"Skipping {episode_file} in {season_folder}")
                        continue
                    split_data:List[str] = self.__splitNameExtension(episode_file)
                    if len(split_data) != 2:
                        self.logError(f"Error splitting name and extension from {episode_file}")
                        continue
                    episode_data:Episode = Episode(episode_file)
                    episode_data.filepath:str = os.path.join(self.root_directory,series_folder,season_folder,episode_file)
                    episode_data.original_name:str = split_data[0]
                    episode_data.extension:str = split_data[1]
                    #add the episode data to the season data
                    season_data.episodes.append(episode_data)
                #add the season data to the series data
                series_data.seasons.append(season_data)
            #add the series data to the series list
            series_list.append(series_data)
        self.local_series_data = series_list
        if len(self.local_series_data) == 0:
            self.logError(f"No series found in {self.root_directory}")
            return False
        return True
    
    def __determineSkip(self,filename:str) -> bool:
        """Determines if the given filename should be skipped.  Returns True if it should be skipped, False if not."""
        for name in self.skip_filenames:
            if filename.lower() == name.lower():
                return True
        for extension in self.skip_extensions:
            if filename.lower().endswith(extension.lower()):
                return True
        return False
    
    def __getSeasonNumber(self,season_string:str) -> int:
        """Returns the season number from the given string.  Returns -1 if not found."""
        #check if a number follows a space
        if season_string.__contains__(" "):
            possible_number:str = season_string.rsplit(" ")[1]
            if possible_number.isdigit():
                return int(possible_number)
        #check if a number follows the word 'season'
        if season_string.lower().__contains__("season"):
            try:
                possible_number:str = season_string.lower().split("season")[1]
                if possible_number.isdigit():
                    return int(possible_number)
            except Exception as e:
                self.log(f"{season_string} contains 'season' but could not be split: {e}")
        #check if a number is written out
        number_text:List[str] = ["one","two","three","four","five","six","seven","eight","nine","ten","eleven","twelve","thirteen","fourteen", "fifteen","sixteen","seventeen","eighteen","nineteen","twenty"]
        for i in range(0,len(number_text)):
            if season_string.lower().__contains__(number_text[i]):
                return i+1
        #check digits in the string, starting from the end
        digits:List[str] = []
        for i in range(len(season_string)-1,-1,-1):
            if season_string[i].isdigit():
                digits.append(season_string[i])
            else:
                break
        #reverse the digits
        digits.reverse()
        #join the digits into a string
        digits_string:str = "".join(digits)
        #return the digits as an int
        if digits_string.isdigit():
            return int(digits_string)
        #check digits in the string, starting from the beginning
        digits:List[str] = []
        for i in range(0,len(season_string)):
            if season_string[i].isdigit():
                digits.append(season_string[i])
            else:
                break
        #join the digits into a string
        digits_string:str = "".join(digits)
        #return the digits as an int
        if digits_string.isdigit():
            return int(digits_string)
        #just grab all digits and put them in a string
        digits:List[str] = []
        for i in range(0,len(season_string)):
            if season_string[i].isdigit():
                digits.append(season_string[i])
        #join the digits into a string
        digits_string:str = "".join(digits)
        #return the digits as an int
        if digits_string.isdigit():
            return int(digits_string)
        #if no number was found, return -1
        return -1

    def __splitNameExtension(self,episode_string:str) -> List[str]:
        """Splits the episode name and extension from the given string.  Returns a list of two strings, or an empty list if not found."""
        #check if a period exists
        if episode_string.__contains__("."):
            #split the string by the period
            data:List[str] = episode_string.rsplit(".",1)
            return data
        return []