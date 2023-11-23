from typing import Dict
import json
import os
from Classes.Filesystem import Filesystem
from Classes.LoggableClass import LoggableClass

class Config(LoggableClass):
    def __init__(self,config_path:str,logging=True,logging_warnings=True,logging_errors=True):
        #super init
        self.prefix:str = "CFG"
        self.prefix_warning:str = "CFG WRN"
        self.prefix_error:str = "CFG ERR"
        super().__init__(prefix=self.prefix,
                         prefix_warning=self.prefix_warning,
                         prefix_error=self.prefix_error,
                         logging=logging,
                         log_warning=logging_warnings,
                         log_errors=logging_errors)
        #config
        self.config_path:str = config_path
        self.filesystem:Filesystem = Filesystem()
        #HARD CODED PATHS
        self.CWD = os.path.dirname(self.config_path)    #current working directory
        self.FILEPATH_TMDB_API_KEY_BACKUP = os.path.join(self.CWD, 'api_key.txt')   #backup file for tmdb api key
        self.FILEPATH_TMDB_DATA = os.path.join(self.CWD, 'data','TMDB data','tmdb_data.pkl')  #file to store tmdb data
        self.FILEPATH_LST_DATA = os.path.join(self.CWD, 'data','LST data', 'local_series_data.pkl')   #file to store ert data
        #LOAD CONFIG
        self.loadConfig()

    def loadConfig(self) -> bool:
        """Loads the config file into a dictionary.  Returns True if successful, False if not."""
        config = self.filesystem.loadJson(self.config_path) # TODO here
        if config == {}:
            self.logError(f"Error loading config file at {self.config_path}")
            return False
        else:
            # ------------------------------- Load and set variable values -------------------------------
            self.TMDB_API_KEY = config.get('tmdb_api_key',"")
            self.FILEPATH_ROOT_SERIES_DATA = config.get('root_series_folder',"")

            # END
        #api key backup file
        if self.TMDB_API_KEY == "":
            self.TMDB_API_KEY = self.filesystem.loadFileToString(self.FILEPATH_TMDB_API_KEY_BACKUP)
        if self.TMDB_API_KEY == "":
            self.logError(f"No TMDB API key found in config or backup file.")
            return False
        return True
            