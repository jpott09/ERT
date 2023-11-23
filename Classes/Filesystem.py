import os
import pickle
import json
from Classes.LoggableClass import LoggableClass
from typing import List, Dict

class Filesystem(LoggableClass):
    def __init__(self,logging=True,logging_warnings=True,logging_errors=True):
        super().__init__(prefix="FileSys",
                         prefix_error="FileSys ERR",
                         prefix_warning="FileSys WRN",
                         logging=logging,
                         log_warning=logging_warnings,
                         log_errors=logging_errors)

    def loadFileToList(self, filepath:str) -> List:
        """Load a file to a list of strings.  Returns the list, or an empty list"""
        if not os.path.exists(filepath):
            return []
        try:
            lines:List[str] = []
            with open(filepath, 'r') as f:
                for line in f.readlines():
                    lines.append(line.strip())
            return lines
        except Exception as e:
            self.logError(f"Error loading file to list: {e}")
            return []
        
    def loadFileToString(self,filepath:str) -> str:
        """Load a file to a string.  Returns the string, or an empty string"""
        if not os.path.exists(filepath):
            return ""
        try:
            with open(filepath, 'r') as f:
                return f.read()
        except Exception as e:
            self.logError(f"Error loading file to string: {e}")
            return ""
        
    def loadJson(self,filepath:str) -> dict:
        """Load a json file to a dictionary.  Returns the dictionary, or an empty dictionary"""
        if not os.path.exists(filepath):
            return {}
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logError(f"Error loading json: {e}")
            return {}
        
    def loadPickle(self,filepath:str) -> object or List[object]:
        """Load a pickle file to an object.  Returns the object, or None"""
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            self.logError(f"Error loading pickle: {e}")
            return None
        
    def getFolders(self,filepath:str) -> List[str]:
        """Returns a list of folders in the given directory. Returns an empty list if none found."""
        if not os.path.exists(filepath):
            return []
        try:
            return [f for f in os.listdir(filepath) if os.path.isdir(os.path.join(filepath, f))]
        except Exception as e:
            self.logError(f"Error getting folders: {e}")
            return []
        
    def getFiles(self,filepath:str) -> List[str]:
        """Returns a list of files in the given directory. Returns an empty list if none found."""
        if not os.path.exists(filepath):
            return []
        try:
            return [f for f in os.listdir(filepath) if os.path.isfile(os.path.join(filepath, f))]
        except Exception as e:
            self.logError(f"Error getting files: {e}")
            return []