from pytube import YouTube
from pytube.cli import on_progress
import pandas as pd
import subprocess
import urllib.request
import re
import pandas as pd
from bs4 import BeautifulSoup
import requests


SCROLL_PAUSE_TIME = 2
MULIPLIER = 2

def downalod_video(link, filepth):
    # TODO write a comment
    subprocess.run(
                    [
                        "yt-dlp",
                        "-S",
                        "res,ext:mp4:m4a",
                        "--recode",
                        "mp4",
                        "-o",
                        f"{filepth}/%(title)s.%(ext)s",
                        f"{link}",
                    ]
                )


def download_csv(data: pd.DataFrame, folder: str):
    """
    The function gets a pandas DataFrame and string objects as a parameter,
    where DataFrame contains video title and link of scraped videos and string is the folder path
    where the downloaded videos should be saved.
    The function downloads youtube videos and returns scraped videos'
    link, title, author, length with seconds, approx_filesize with MBs and views as a DataFrame object

    data: data of the videos which should be scrapped,
    folder: folder path to save videos in,
    return value: returns detailed information of downloaded videos as pandas Dataframe
    """
    data_dict = {
        "link": [],
        "author": [],
        "title": [],
        "length": [],
        # "approx_filesize": [],
        "views": [],
    }

    for i, link in enumerate(data["Link"]):
        try:
            yt = YouTube(
                link, on_progress_callback=on_progress
            )  # use_oauth=True,allow_oauth_cache=True)
        except:
            print(f"Video {link} is unavaialable, skipping.\n")
        else:
            try:
                data_dict["link"].append(link)
                data_dict["title"].append(yt.title)
                data_dict["author"].append(yt.author)
                data_dict["length"].append(yt.length)
                data_dict["views"].append(yt.views)
            except Exception as e:
                print(f"Download is failed {link}: {e}")

    df = pd.DataFrame.from_dict(data_dict)
    return df


# def search(search_keyword, videos_quantity=10):

#     """
#     The method gets a string and an integer as a parameter,
#     where string is a pattern and integer is a quantity of the videos that we need to output.
#     The method performs a search through the video titles on YouTube by the given pattern.
#     And as a result returns list of videos’ full titles with its corresponding links.

#     search_keyword: required pattern,
#     videos_quantity: a quantity of the videos that we need to output
#     """

#     search_keyword = search_keyword.replace(" ", "+")
#     html = urllib.request.urlopen(
#         "https://www.youtube.com/results?search_query=" + search_keyword
#     )
#     ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
#     video_ids = list(set(ids))

#     csv_elems = {}
#     for i in range(videos_quantity):
#         url = "https://www.youtube.com/watch?v=" + video_ids[i]

#         response = requests.get(url)
#         html_content = response.text
#         soup = BeautifulSoup(html_content, "html.parser")

#         title_element = soup.find("title")
#         title = title_element.text.strip()
#         key = title
#         key = key.replace("(Official Video)", "")
#         key = key.replace("YouTube", "")
#         csv_elems[key] = url

#     df = pd.DataFrame(csv_elems.items(), columns=["Title", "Link"])
#     df.index = df.index + 1
#     df.Title = df.Title.str[:-2]
#     return df

from selenium import webdriver
from selenium.webdriver.common.by import By
import time 
from webdriver_manager.chrome import ChromeDriverManager 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService




def search(search_keyword, videos_quantity=10):
    
    
    video_links = []
    scroll_pause_time = 2  # Time to pause between scrolls
    df = pd.DataFrame()
    
    search_keyword = search_keyword.replace(" ", "+")
    url = "https://www.youtube.com/results?search_query=" + search_keyword
    
    # Configure Selenium to use a headless browser (e.g., Chrome)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(ChromeDriverManager().install())

    driver.get(url)
    time.sleep(2)  

    # Scroll the page to load more videos
    
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    # decision="again"
    while df.shape[0] < videos_quantity:  
        video_q=int(videos_quantity*MULIPLIER)
        # print(driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer"))
        num_ready_videos = len(driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer"))
        print('num_ready_videos',num_ready_videos)
        print('video_q',video_q)
        print(num_ready_videos < video_q)
        while num_ready_videos < video_q:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            num_ready_videos = len(driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer"))

        # Extract video links
        video_elements = driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer")

        for i in range(video_q):
            video_link_element = video_elements[i].find_element(By.CSS_SELECTOR, "a#thumbnail").get_attribute("href")
            video_links.append(video_link_element)

        driver.quit()  # Close the browser

        # Create dataframe from video links
        csv_elems = {}
        for video_link in video_links:
            response = requests.get(video_link)
            html_content = response.text
            soup = BeautifulSoup(html_content, "html.parser")

            title_element = soup.find("title")
            title = title_element.text.strip()
            key = title
            key = key.replace("(Official Video)", "")
            key = key.replace("YouTube", "")
            csv_elems[key] = video_link

        df = pd.DataFrame(csv_elems.items(), columns=["Title", "Link"])
        df.index = df.index + 1
        df.Title = df.Title.str[:-2]
        #Filtering from not related videos

        filtered_df = df[df["Title"].str.contains(search_keyword, na=False)]
        
        # TODO
        m+=1
    
    return filtered_df.iloc[0:videos_quantity,]

if __name__ == '__main__' :
    search(search_keyword='aram',videos_quantity = 30)
