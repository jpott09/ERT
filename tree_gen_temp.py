import requests
from typing import List, Dict
import pickle
import os

# ------------------------- Classes -------------------------
class Data:
    def __init__(self,name:str):
        self.name:str = name
        self.links:List[str] = []
        self.children:List[Data] = []

    def addChild(self,child:object):
        self.children.append(child)

    def getChildren(self) -> List[object]:
        return self.children
    
    def getChild(self,child_name:str) -> object or None:
        for child in self.children:
            if child == child_name:
                return child
        return None
    
    def addLink(self,link:str):
        self.links.append(link)

    def getLinks(self) -> List[str]:
        return self.links
    
class Episode(Data):
    def __init__(self,name:str):
        super().__init__(name)

class Season(Data):
    def __init__(self,name:str):
        super().__init__(name)

    def getChildren(self) -> List[Episode]:
        return super().getChildren()

class Series(Data):
    def __init__(self,name:str):
        super().__init__(name)

    def getChildren(self) -> List[Season]:
        return super().getChildren()

# ------------------------- Functions -------------------------

def getResponseLines( url:str) -> List[str]:
    """Gets the lines of the response from the given url"""
    response = requests.get(url)
    raw_response:str = response.text
    lines:List[str] = raw_response.split('\n')
    return lines

def scrapeResponseData(url:str,lines:List[str]) -> Dict[str,str]:
    """Parses the response lines into a dictionary
    Returns {'name':name, 'url':url}, 'raw':raw_line"""
    li_count:int = 0
    data:List[Dict] = []
    for line in lines:
        if line.startswith('<li>'):
            li_count += 1
            directory:str = line.split('<a href="')[1].split('">')[0]
            if line.__contains__("/</a>"):
                name:str = line.split("a href=")[1].split(">")[1].split("/</a")[0]
            else:
                name:str = line.split("a href=")[1].split(">")[1].split("</a")[0]
            d:Dict[str,str] = {}
            d['name'] = name
            d['url'] = f'{url}/{directory}'
            d['raw'] = line
            data.append(d)
    return data

def scrapeUnlinkedResponseData(lines:List[str]) -> Dict[str,str]:
    """Parses the response lines into a dictionary
    Returns {'name':name, 'raw':raw_line}"""
    li_count:int = 0
    data:List[Dict] = []
    for line in lines:
        if line.startswith('<li>'):
            li_count += 1
            name:str = line.split("<li>")[1].split("</li>")[0]
            d:Dict[str,str] = {}
            d['name'] = name
            d['raw'] = line
            data.append(d)
    return data

def generateData(url:str) -> List[Series]:
    """Generates a list of Series objects from the given url"""
    series_list:List[Series] = []
    series_data:List[Dict] = scrapeResponseData(url,getResponseLines(url))
    for data in series_data:
        series:Series = Series(data['name'])
        series.addLink(data['url'])
        series_list.append(series)
    #test
    print(f"Found {len(series_list)} series")
    #get the season names and urls
    for series in series_list:
        links:List[str] = series.getLinks()
        for link in links:
            season_data:List[Dict] = scrapeResponseData(link,getResponseLines(link))
            for data in season_data:
                season:Season = Season(data['name'])
                season.addLink(data['url'])
                series.addChild(season)
    #get the episode names and urls
    for series in series_list:
        for season in series.getChildren():
            links:List[str] = season.getLinks()
            for link in links:
                episode_data:List[Dict] = scrapeResponseData(link,getResponseLines(link))
                for data in episode_data:
                    episode:Episode = Episode(data['name'])
                    season.addChild(episode)
    return series_list

def verifyFolder(folder_path:str,exit_on_fail:bool = True) -> bool:
    if not os.path.exists(folder_path):
        print(f"Creating folder: {folder_path}")
        os.mkdir(folder_path)
        if not os.path.exists(folder_path):
            print(f"Failed to create folder: {folder_path}")
            if exit_on_fail:
                exit(1)
            else:
                return False
    return True

def verifyFile(file_path:str,exit_on_fail:bool = True) -> bool:
    if not os.path.exists(file_path):
        print(f"Creating file: {file_path}")
        open(file_path,'w').close()
        if not os.path.exists(file_path):
            print(f"Failed to create file: {file_path}")
            if exit_on_fail:
                exit(1)
            else:
                return False
    return True

# ------------------------- Run -------------------------
url:str = "http://192.168.1.14:5000"
root_directory:str = os.path.join(os.getcwd(),'tv shows')
#create root directory if it doesn't exist
verifyFolder(root_directory)


series_list:List[Series] = generateData(url)

for series in series_list:
    #create the series folder
    folder_path:str = os.path.join(root_directory,series.name)
    verifyFolder(folder_path)
    print(f"{series.name}")
    for season in series.getChildren():
        season_path:str = os.path.join(folder_path,season.name)
        verifyFolder(season_path)
        print(f"\tSeason: {season.name}")
        for episode in season.getChildren():
            episode_path:str = os.path.join(season_path,episode.name)
            verifyFile(episode_path)
            print(f"\t\tEpisode: {episode.name}")