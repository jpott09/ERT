import requests
import os
import re as regex
import time


# Set your API key
api_key = ""
with open("api_key.txt","r") as file:
    api_key = file.read().strip()
if not api_key:
    print("No API key found")
    exit(1)
    
base_url = 'https://api.themoviedb.org/3'
tv_root_folder = 'D:\\tv shows'
series_start_letter = None   #use if a scan was incomplete

def get_episode_number(series_name, season_number, episode_name):
    # Construct the search URL
    try:
        search_url = f"{base_url}/search/tv?api_key={api_key}&query={series_name}"

        # Make the search request
        response = requests.get(search_url).json()
        series_id = response['results'][0]['id']  # Get the series ID

        # Get season data
        season_url = f"{base_url}/tv/{series_id}/season/{season_number}?api_key={api_key}"
        season_response = requests.get(season_url).json()

        # Find the episode
        for episode in season_response['episodes']:
            #check if the lowercase version of the episode name is in the lowercase version of the episode name
            if episode_name.lower() in episode['name'].lower():
                return episode['episode_number']
    except Exception as e:
        print(f"Error getting episode information: {e}")
    return None

failed_season_folders = []
skipped_episodes = []
failed_episodes = []
aborted_series_seasons = []
skipped_folders = []
rename_errors = []
renamed_items = []

#iterate the folders in the root folder
folders = os.listdir(tv_root_folder)
#sort the folders alphabetically
folders.sort()
start_time = time.time()
for folder in folders:
    if series_start_letter:
        #get the first letter in the folder name
        folder_start = folder[0]
        if folder_start.lower() < series_start_letter.lower():
            skipped_folders.append(folder)
            continue
    print(f"Processing {folder}")
    series_name = folder
    #iterate the season folders in the series folder
    season_folders = os.listdir(os.path.join(tv_root_folder,folder))
    for season in season_folders:
        print(f"Processing {season}")
        #grab just the numbers of the season
        if not season.__contains__(" "):
            print(f"Failed to process {season}")
            failed_season_folders.append(season)
            continue
        season_number = season.split(' ')[1]
        try:
            season_number = int(season_number)
        except Exception as e:
            print(f"Exception for {season} when processing filename. Exception: {e}")
            failed_season_folders.append(season)
            continue
        #iterate the episodes in the season folder
        episodes = os.listdir(os.path.join(tv_root_folder,folder,season))
        print(f"Processing {len(episodes)}...")
        season_fail_count = 0
        for episode in episodes:
            if os.path.exists(os.path.join(tv_root_folder,series_name,season,episode)) and not os.path.isfile(os.path.join(tv_root_folder,series_name,season,episode)):
                print(f"Skipping directory item {episode}")
                continue
            if season_fail_count > 2:
                print(f"Maximum amount of failed attempts reached for episodes in {series_name}")
                aborted_series_seasons.append(f"{series_name} - {season}")
                break
            episode_name = episode
            #get the last index of '.'
            last_index = episode_name.rfind('.')
            extension = episode_name[last_index:]
            #remove the extension
            episode_name = episode_name[:last_index]
            #see if the episode name contains -S#E# where there can be any number of digits using regex
            if regex.search(r'S\d+E\d+',episode_name):
                #skip the episode if it already has the episode number in the name
                skipped_episodes.append(episode_name)
                print(f"Skipping {episode_name}")
                continue
            #get the episode number from the api
            episode_number = get_episode_number(series_name, season_number, episode_name)
            #if the episode number is not none
            if episode_number is not None:
                #create the new name
                name = episode_name
                season_index = str(season_number)
                while len(season_index) < 2:
                    season_index = f"0{season_index}"
                episode_index = str(episode_number)
                while len(episode_index) < 2:
                    episode_index = f"0{episode_index}"
                name = f"{name}-S{season_index}E{episode_index}{extension}"
                #rename the file
                print(f"Renaming {episode_name} to {name}")
                try:
                    os.rename(os.path.join(tv_root_folder,folder,season,episode),os.path.join(tv_root_folder,folder,season,name))
                    renamed_items.append(f"{series_name} {season} {name}")
                except Exception as e:
                    print(f"Could not rename file: {episode}. Exception: {e}")
                    rename_errors.append(f"{series_name} {season} {episode} {episode_name}")
            else:
                season_fail_count += 1
                print(f"Failed to get episode number for {episode_name}")
                failed_episodes.append(episode_name)

print(f"Skipped folder count: {len(skipped_folders)}")
for folder in skipped_folders:
    print(f"\t{folder}")
print(f"Failed to process {len(failed_season_folders)} season folders")
for folder in failed_season_folders:
    print(f"\t{folder}")
print(f"Skipped {len(skipped_episodes)} episodes")
print(f"Failed to process {len(failed_episodes)} episodes")
for episode in failed_episodes:
    print(f"\t{episode}")
print(f"Aborted Series/seasons: {len(aborted_series_seasons)}")
for item in aborted_series_seasons:
    print(f"\t{item}")
print(f"Rename errors: {len(rename_errors)}")
for item in rename_errors:
    print(f'\t{item}')
print(f"Renamed {len(renamed_items)} items")
for item in renamed_items:
    print(f"\t{item}")

elapsed_time = time.time() - start_time
print(f"Completed in {round(elapsed_time/60,2)} minutes")