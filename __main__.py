#import
import os
import pickle
import json
from Menu import MainMenu, ERTMenu, MissingMenu, AboutMenu
from Classes.Filesystem import Filesystem
from typing import List, Dict
from Classes.Config import Config

#get the current file directory
current_file_directory:str = os.path.dirname(os.path.abspath(__file__))
## ---------------------------- CONFIG ------------------------------##
#filepath for config
config_filepath:str = os.path.join(current_file_directory, 'config.json')
#initialize config class
config = Config(config_filepath)
## ---------------------------- FILESYSTEM ------------------------------##
#initialize filesystem class
filesystem = Filesystem()
## ---------------------------- PATHS ------------------------------##
#path to info .txt files
info_files_path:str = os.path.join(current_file_directory, 'info files')
#paths to ERT data
ert_local_series_data:str = os.path.join(current_file_directory, 'ERT data','local_series_data.pkl')
ert_API_series_data:str = os.path.join(current_file_directory, 'ERT data', 'api_series_data.pkl')


## ---------------------------- MENUS ------------------------------##
main_menu = MainMenu("Main Menu")
ert_menu = ERTMenu("Episode Repair Tool")
missing_menu = MissingMenu("Missing Media Tool")
about_menu = AboutMenu("About")
#load menu info
main_menu.setInfo(filesystem.loadFileToString(os.path.join(info_files_path, 'main menu.txt')))
ert_menu.setInfo(filesystem.loadFileToString(os.path.join(info_files_path, 'ert menu.txt')))
#append the config filepath to the ert info
ert_menu.appendInfo(f"Current filepath: {config.FILEPATH_ROOT_SERIES_DATA()}")
missing_menu.setInfo(filesystem.loadFileToString(os.path.join(info_files_path, 'mmt menu.txt')))
about_menu.setInfo(filesystem.loadFileToString(os.path.join(info_files_path, 'about menu.txt')))
#load menu options
    #main menu
main_menu.addOption("Episode Repair Tool", ert_menu.draw)
main_menu.addOption("Missing Media Tool", missing_menu.draw)
main_menu.addOption("About", about_menu.draw)
main_menu.addOption("Exit", exit)
    #ert menu
ert_menu.addOption("Set Root Filepath", None)
ert_menu.addOption("Full Scan", None)
ert_menu.addOption("Single Series Scan", None)
ert_menu.addOption("Single Season Scan", None)
ert_menu.addOption("Toggle Safety Mode (Currently: On)", None)
ert_menu.addOption("Back", main_menu.draw)
    #missing menu
missing_menu.addOption("Full Scan", None)
missing_menu.addOption("Single Series Scan", None)
missing_menu.addOption("Single Season Scan", None)
missing_menu.addOption("Back", main_menu.draw)
    #about menu
about_menu.addOption("Back", main_menu.draw)


## ---------------------------- MAIN ------------------------------##
if __name__ == "__main__":
    main_menu.draw()


