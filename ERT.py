import requests
import os
import re as regex
import time
from typing import List, Dict

# ------------------------- Classes ------------------------- //FILE OBJECTS
class FileObject:
    def __init__(self,name:str):
        self.name:str = name
        self.children:List[FileObject] = []

    def getName(self) -> str:
        return self.name
    
    def addChild(self,child:object):    
        self.children.append(child)
    
    def getChildren(self) -> List[object]:
        return self.children
    
class Episode(FileObject):
    def __init__(self,name:str):
        super().__init__(name)

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
    def __init__(self,api_key:str, logging:bool = True):
        # main variables
        self.api_key:str = api_key
        self.base_url:str = 'https://api.themoviedb.org/3'
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
        self.logging:bool = True
        self.log_list:List[str] = []
        self.warning_list:List[str] = []
        self.error_list:List[str] = []
        self.full_logs:List[str] = []
        #questionable_matches
        self.possibly_formatted_episodes:List[str] = []

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
        if self.logging:
            print(line)

    def logWarning(self, message:str, prefix:str = "ERT Warning"):
        """Logs a warning message to the console if logging is enabled.  Message is logged to warning_list and full_logs regardless of logging status"""
        current_time:str = self.getTimestamp()
        line:str = f"[{self.warning_color}{prefix}{self.reset}]:[{self.timestamp_color}{current_time}{self.reset}] {self.messsage_color}{message}{self.reset}"
        self.warning_list.append(line)
        self.full_logs.append(line)
        if self.logging:
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
    
    #--------- STRING TOOLS ---------------------------------------------------------------- STRING TOOLS --------       
    def formatSeriesName(self,series_name:str) -> str:
        """Check series name for formatting issues.  Returns a formatted series name"""
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
    
    def generateSeriesData(self,root_folder:str) -> True or False:
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
            #get the season folders
            season_folders:List[str] = os.listdir(os.path.join(root_folder,series_folder))
            #iterate the season folders
            for season_folder in season_folders:
                #create a season object
                season:Season = Season(season_folder)
                #get the episode files
                episode_files:List[str] = os.listdir(os.path.join(root_folder,series_folder,season_folder))
                #iterate the episode files
                for episode_file in episode_files:
                    #create an episode object
                    episode:Episode = Episode(episode_file)
                    #add the episode to the season
                    season.addChild(episode)
                #add the season to the series
                series.addChild(season)
            #add the series to the series list
            series_list.append(series)
        self.series_list.clear()
        self.series_list = series_list
        return True
    
    def TESTING(self,root_folder:str):
        print(f"TESTING: against {root_folder}")
        self.generateSeriesData(root_folder)
        for series in self.series_list:
            series_name:str = series.getName()
            formatted_series_name:str = self.formatSeriesName(series_name)
            print(f"{series_name} -> {formatted_series_name}")
            # TODO add functions to get the series season count from API
            # check that series names all are valid for the API



    
#if name = main for testing
if __name__ == "__main__":
    import os
    api_key:str = "6549463d223be920a83a50572d0e3db0"
    folder_path = os.path.join(os.getcwd(),"tv shows")

    ert:ERT = ERT(api_key)
    ert.TESTING(folder_path)



