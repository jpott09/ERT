import requests
import os
import re as regex
import time
from typing import List, Dict
import pickle

# ------------------------- Classes ------------------------- //FILE OBJECTS
class FileObject:
    def __init__(self,name:str):
        self.name:str = name
        self.tmdb_id:str = ""
        self.formatted_name:str = name
        self.children:List[FileObject] = []

    def getName(self) -> str:
        return self.name
    
    def setFormattedName(self,formatted_name:str) -> None:
        self.formatted_name = formatted_name

    def getFormattedName(self) -> str:
        return self.formatted_name
    
    def addChild(self,child:object) -> None:    
        self.children.append(child)
    
    def getChildren(self) -> List[object]:
        return self.children

    def getID(self) -> str:
        if self.tmdb_id != "":
            return self.tmdb_id
        else:
            return None
        
    def setID(self,id:str) -> None:
        self.tmdb_id = id
    
class Episode(FileObject):
    def __init__(self,name:str):
        super().__init__(name)
        self.extension = ""
        self.identifier_string = ""

    def setExtension(self,extension:str) -> None:
        self.extension = extension

    def getExtension(self) -> str:
        return self.extension
    
    def setIdentifierString(self,identifier_string:str) -> None:
        self.identifier_string = identifier_string

    def getIdentifierString(self) -> str:
        return self.identifier_string

class Season(FileObject):
    def __init__(self,name:str):
        super().__init__(name)
    
    def getChildren(self) -> List[Episode]:
        return super().getChildren()
    
class Series(FileObject):
    def __init__(self,name:str):
        super().__init__(name)
        
    def getChildren(self) -> List[Season]:
        return super().getChildren()
# ------------------------- Classes ------------------------- //ERT
class ERT:
    def __init__(
            self,api_key:str, 
            local_series_data_path:str = "",
            local_root_folder:str = "",
            logging:bool = True, 
            log_warning:bool = True, 
            log_errors:bool = True
            ):
        # main variables
        self.api_key:str = api_key
        self.base_url:str = 'https://api.themoviedb.org/3'
        #filepaths
        self.local_series_data_path:str = local_series_data_path
        self.local_root_folder:str = local_root_folder
        #colors
        self.red:str = "\033[31m"
        self.green:str = "\033[32m"
        self.yellow:str = "\033[33m"
        self.blue:str = "\033[34m"
        self.magenta:str = "\033[35m"
        self.cyan:str = "\033[36m"
        self.white:str = "\033[37m"
        self.black:str = "\033[30m"
        self.grey:str = "\033[90m"
        self.reset:str = "\033[0m"
        #logging
        self.prefix_color:str = self.cyan
        self.messsage_color:str = self.white
        self.timestamp_color:str = self.grey
        self.warning_color:str = self.yellow
        self.error_color:str = self.red

        self.logging:bool = logging
        self.log_warning:bool = log_warning
        self.log_errors:bool = log_errors
        self.log_list:List[str] = []
        self.warning_list:List[str] = []
        self.error_list:List[str] = []
        self.full_logs:List[str] = []
        #questionable_matches
        self.possibly_formatted_episodes:List[str] = []
        self.failed_episode_formats:List[str] = []

        #class lists
        self.series_list:List[Series] = []


    def getTimestamp(self) -> str:
        """Returns the current time in HH:MM:SS format"""
        return time.strftime("%H:%M:%S", time.localtime())
    
    def log(self, message:str, prefix:str = "ERT"):
        """Logs a message to the console if logging is enabled.  Message is logged to log_list and full_logs regardless of logging status"""
        current_time:str = self.getTimestamp()
        line:str = f"[{self.prefix_color}{prefix}{self.reset}]:[{self.timestamp_color}{current_time}{self.reset}] {self.messsage_color}{message}{self.reset}"
        self.log_list.append(line)
        self.full_logs.append(line)
        if self.logging:
            print(line)

    def logError(self, message:str, prefix:str = "ERT Error"):
        """Logs an error message to the console if logging is enabled.  Message is logged to error_list and full_logs regardless of logging status"""
        current_time:str = self.getTimestamp()
        line:str = f"[{self.error_color}{prefix}{self.reset}]:[{self.timestamp_color}{current_time}{self.reset}] {self.messsage_color}{message}{self.reset}"
        self.error_list.append(line)
        self.full_logs.append(line)
        if self.log_errors:
            print(line)

    def logWarning(self, message:str, prefix:str = "ERT Warning"):
        """Logs a warning message to the console if logging is enabled.  Message is logged to warning_list and full_logs regardless of logging status"""
        current_time:str = self.getTimestamp()
        line:str = f"[{self.warning_color}{prefix}{self.reset}]:[{self.timestamp_color}{current_time}{self.reset}] {self.messsage_color}{message}{self.reset}"
        self.warning_list.append(line)
        self.full_logs.append(line)
        if self.log_warning:
            print(line)
    #--------- API CALLS --------------------------------------------------------------------------- API CALLS --------
    def getEpisodeNumber(self,series_name:str, season_number:str, episode_name:str)->int or None:
        """Returns the episode number of the episode with the given name in the given season of the given series"""
        # Construct the search URL
        search_url:str = f"{self.base_url}/search/tv?api_key={self.api_key}&query={series_name}"

        # Make the search request
        try:
            response = requests.get(search_url).json()
            series_id = response['results'][0]['id']  # Get the series ID
        except Exception as e:
            self.logError(f"Error getting series ID for '{series_name}': {e}")
            return None

        # Get season data
        season_url = f"{self.base_url}/tv/{series_id}/season/{season_number}?api_key={self.api_key}"
        try:
            season_response = requests.get(season_url).json()
            # Find the episode
            for episode in season_response['episodes']:
                #check if the lowercase version of the episode name is in the lowercase version of the episode name
                # TODO: see if this needs to be refined, or if there is more information from API to compare name variations against
                if episode_name.lower() in episode['name'].lower() or episode['name'].lower() in episode_name.lower():
                    return int(episode['episode_number'])
        except Exception as e:
            self.logError(f"Error getting episode information for '{series_name}' in {season_number}: {e}")
            return None
    
    def getSeriesID(self,item_name:str) -> int or None:
        """Returns the ID of the Series with the given name"""
        # Construct the search URL
        search_url:str = f"{self.base_url}/search/tv?api_key={self.api_key}&query={item_name}"

        # Make the search request
        try:
            response = requests.get(search_url).json()
            item_id = response['results'][0]['id']  # Get the series ID
            return item_id
        except Exception as e:
            self.logError(f"Error getting item ID for '{item_name}': {e}")
            return None
        
    #--------- STRING TOOLS ---------------------------------------------------------------- STRING TOOLS --------       
    def formatSeriesName(self,series_name:str) -> str:
        """Check series name for formatting issues.  Returns a formatted series name"""
        #check if formatted string contains (year)
        year_regex:str = r'\(\d{4}\)'
        if regex.search(year_regex,series_name):
            #remove (year)
            series_name = regex.sub(year_regex,'',series_name)
        return self.cleanString(series_name)
    
    def formatSeasonName(self,season_name:str) -> str:
        """Check season name for formatting issues.  Returns a formatted season name"""
        return self.cleanString(season_name)
    
    def formatEpisodeName(self,episode_name:str) -> Dict[str,str] or None:
        """Attempt to split, and then format episode name.  Returns a dictionary containing {'name':formatted_episode_name,'extension':extension} or None"""
        data:Dict[str,str] = self.splitEpisodeName(episode_name)
        if not data:
            return None
        episode_name:str = data["name"]
        extension:str = data["extension"]
        episode_name = self.cleanString(episode_name)
        data["name"] = episode_name
        data["extension"] = extension
        return data
    
    def episodeIsIndexed(self,season_number:int,formatted_episode_name:str) -> bool:
        """Check if the episode name is indexed.  Returns True or False"""
        #check if the episode name contains 'S##E##' (upper or lowercase) 
        # with any number of digits 
        # and the possibility of a dash between the season and episode numbers
        indexed_regex:str = r'[sS]\d+-?[eE]\d+'
        if regex.search(indexed_regex,formatted_episode_name):
            return True
        #check if the episode name contains season number
        season_number_index:int = formatted_episode_name.find(str(season_number))
        if season_number_index == -1:
            return False
        #check if the episode name contains episode number after the season number
        substring:str = formatted_episode_name[season_number_index:]
        #get the first character of the substring
        first_char:str = substring[0]
        valid_matches:List[str] = [" ","-","_","E","e"]
        if first_char.isdigit() or first_char in valid_matches:
            self.logWarning(f"Episode '{formatted_episode_name}' is {self.yellow}possibly{self.reset} indexed, but not formatted correctly. Will be reported as formatted.")
            self.possibly_formatted_episodes.append(formatted_episode_name)
            return True
        return False

    def determineSeasonNumber(self,season_name:str) -> int or None:
        """Take the season name [Season 02/Season 1/Season15] and try to determine the season number.  Returns an int or None"""
        #iterate all numbers in the season_name and add them to an array
        numbers:List[str] = [letter for letter in season_name if letter.isdigit()]
        if len(numbers) == 0:
            self.logError(f"No numbers found in the string '{season_name}'")
            return None
        #join the numbers array into a string
        season_number_string:str = ''.join(numbers)
        #convert the string to an int
        season_number:int = int(season_number_string)
        #return the season number
        if not season_number or len(str(season_number)) == 0:
            self.logError(f"Failed to determine season number for '{season_name}'")
            return None
        return season_number
    
    def splitEpisodeName(self,episode_name:str) -> Dict[str,str] or None:
        """Split the episode name into name and extension. Returns {'name':episode_name,'extension':extension} or None"""
        #initialize dict object
        default_value:str = "None"
        data:Dict[str,str] = {
            "name":default_value,
            "extension":default_value
        }
        #split the episode name by the last period
        split_name:List[str] = episode_name.rsplit('.',1)
        #if there is no period, return the name and default extension
        failed:bool = False
        if len(split_name) != 2:
            failed = True
        else:
            data["name"] = split_name[0]
            data["extension"] = split_name[1]
        for key in data:
            if data[key] == default_value:
                failed = True
        if failed:
            self.logError(f"Failed to split episode name '{episode_name}'")
            self.failed_episode_formats.append(episode_name)
            return None
        else:
            return data

    def cleanString(self,string:str) -> str:
        """Cleans a string by removing trailing spaces, special characters, and double spaces"""
        string = self.stripTrailingSpaces(string)
        string = self.removeSpecialCharacters(string)
        string = self.removeDoubleSpaces(string)
        return string
    
    def stripTrailingSpaces(self,string:str) -> str:
        """Removes trailing spaces from a string"""
        return string.strip()
    
    def removeSpecialCharacters(self,string:str) -> str:
        """Removes special characters from a string"""
        special_chars:str = r'[!@#$%^&*()_+={}\[\]:;"\'<>?,./\\]'
        return regex.sub(special_chars,'',string)
    
    def removeDoubleSpaces(self,string:str) -> str:
        """Removes double spaces from a string"""
        return string.replace("  "," ")
    
    def generateLocalSeriesData(self) -> True or False:
        """Generates a list of series objects from the local series data path.
        Writes the results to the local series data path.
        Returns True or False"""
        root_folder:str = self.local_root_folder
        if not os.path.exists(root_folder):
            self.logError(f"Root folder '{root_folder}' does not exist")
            return False
        #get the series folders
        series_folders:List[str] = os.listdir(root_folder)
        #create a list of series objects
        series_list:List[Series] = []
        #iterate the series folders
        for series_folder in series_folders:
            #create a series object
            series:Series = Series(series_folder)
            formatted_name:str = self.formatSeriesName(series_folder)
            series.setFormattedName(formatted_name)
            #get the season folders
            season_folders:List[str] = os.listdir(os.path.join(root_folder,series_folder))
            #iterate the season folders
            for season_folder in season_folders:
                #create a season object
                season:Season = Season(season_folder)
                formatted_name:str = self.formatSeasonName(season_folder)
                season.setFormattedName(formatted_name)
                #get the episode files
                episode_files:List[str] = os.listdir(os.path.join(root_folder,series_folder,season_folder))
                #iterate the episode files
                for episode_file in episode_files:
                    #create an episode object
                    episode:Episode = Episode(episode_file)
                    #split the episode name
                    data:Dict[str,str] = self.formatEpisodeName(episode_file)
                    if not data:
                        self.logError(f"Failed to format episode name '{episode_file}'")
                        continue
                    formatted_name:str = data["name"]
                    extension:str = data["extension"]
                    episode.setFormattedName(formatted_name)
                    episode.setExtension(extension)
                    #add the episode to the season
                    season.addChild(episode)
                #add the season to the series
                series.addChild(season)
            #add the series to the series list
            series_list.append(series)
        #set the series list
        self.series_list.clear()
        self.series_list = series_list
        #write the series list to the local series data path
        self.writeLocalSeriesData()
        return True
    
    def loadLocalSeriesData(self) -> bool:
        if not os.path.exists(self.local_series_data_path):
            self.logError(f"Local series data file '{self.local_series_data_path}' does not exist")
            return False
        with open(self.local_series_data_path,"rb") as file:
            self.series_list = pickle.load(file)
        if len(self.series_list) == 0:
            self.logError(f"Failed to load local series data from '{self.local_series_data_path}'")
            return False
        return True

    def writeLocalSeriesData(self) -> bool:
        if len(self.series_list) == 0:
            self.logError("No series data to write")
            return False
        if os.path.exists(self.local_series_data_path):
            self.logWarning(f"Overwriting existing local series data at '{self.local_series_data_path}'")
            os.remove(self.local_series_data_path)
        with open(self.local_series_data_path,"wb") as file:
            pickle.dump(self.series_list,file)
        if os.path.exists(self.local_series_data_path):
            return True
        else:
            self.logError(f"Failed to write local series data to '{self.local_series_data_path}'")
            return False
        
    def updateLocalSeriesData(self,force_scan:bool = False) -> bool:
        if not force_scan:
            if self.loadLocalSeriesData():
                return True
            else:
                self.generateLocalSeriesData()
                return True
        else:
            return self.generateLocalSeriesData()
        
    def run(self,force_scan:bool = False) -> bool:
        #generate local series data
        if not self.updateLocalSeriesData(force_scan):
            self.logError("Failed to generate local series data")
            return False
        #iterate the series
        for series in self.series_list:
            series_name:str = series.getName()
            #format the series name
            formatted_series_name:str = self.formatSeriesName(series_name)
            if formatted_series_name != series_name:
                self.logWarning(f"Series '{series_name}' formatted to '{formatted_series_name}'")
            #get the series ID
            series_id:int = series.getID()
            if not series_id:
                series_id:int = self.getSeriesID(formatted_series_name)
                if series_id:
                    self.log(f"API call for '{formatted_series_name}' has returned ID {series_id}")
                    series.setID(series_id)
                else:
                    self.logError(f"Failed to get series ID for '{formatted_series_name}'")
            else:
                self.log(f"Loaded ID for Series '{formatted_series_name}': {series_id}")
        #write the updated series objects
        self.writeLocalSeriesData()
        #log the failed episode formats
        if len(self.failed_episode_formats) == 0:
            self.log(f"All episode names were formatted/split successfully")
        else:
            self.log(f"The following {len(self.failed_episode_formats)} episode names failed to be format/split:")
            for episode_name in self.failed_episode_formats:
                self.log(f"\t{episode_name}")
        return True


def loadAPI():
    with open("api_key.txt","r") as file:
        api_key = file.read().strip()
    return api_key
    
# ------------------------- Main ------------------------- //MAIN
local_series_data_path:str = os.path.join(os.getcwd(),"ERT data","local_series_data.pkl")
local_tv_root_folder_path:str = os.path.join(os.getcwd(),"tv shows")
logging:bool = True
log_warning:bool = True
log_errors:bool = True
if __name__ == "__main__":
    import os
    api_key:str = loadAPI()
    folder_path = os.path.join(os.getcwd(),"tv shows")

    ert:ERT = ERT(api_key,local_series_data_path,local_tv_root_folder_path,logging,log_warning,log_errors)
    ert.run(True)



