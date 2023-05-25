from pytube import YouTube
from pytube.cli import on_progress
import pandas as pd
import subprocess
import urllib.request
import re
import pandas as pd
from bs4 import BeautifulSoup
import requests


def downalod_video(link, filepth):
    youtubeObject = YouTube(link)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    try:
        youtubeObject.download(filepth)
    except:
        print("An error has occurred")


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
        "approx_filesize": [],
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
                print(f"Downloading video {i+1}. {link}")
                subprocess.run(
                    [
                        "yt-dlp",
                        "-S",
                        "res,ext:mp4:m4a",
                        "--recode",
                        "mp4",
                        "-o",
                        f"{folder}/%(title)s.%(ext)s",
                        f"{link}",
                    ]
                )
                data_dict["link"].append(link)
                data_dict["title"].append(yt.title)
                data_dict["author"].append(yt.author)
                data_dict["length"].append(yt.length)
                data_dict["views"].append(yt.views)
            except Exception as e:
                print(f"Download is failed {link}: {e}")

    df = pd.DataFrame.from_dict(data_dict)
    return df


def search(search_keyword, videos_quantity=10):

    """
    The method gets a string and an integer as a parameter,
    where string is a pattern and integer is a quantity of the videos that we need to output.
    The method performs a search through the video titles on YouTube by the given pattern.
    And as a result returns list of videos’ full titles with its corresponding links.

    search_keyword: required pattern,
    videos_quantity: a quantity of the videos that we need to output
    """

    search_keyword = search_keyword.replace(" ", "+")
    html = urllib.request.urlopen(
        "https://www.youtube.com/results?search_query=" + search_keyword
    )
    ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    video_ids = list(set(ids))

    csv_elems = {}
    for i in range(videos_quantity):
        url = "https://www.youtube.com/watch?v=" + video_ids[i]

        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")

        title_element = soup.find("title")
        title = title_element.text.strip()
        key = title
        key = key.replace("(Official Video)", "")
        key = key.replace("YouTube", "")
        csv_elems[key] = url

    df = pd.DataFrame(csv_elems.items(), columns=["Title", "Link"])
    df.index = df.index + 1
    df.Title = df.Title.str[:-2]
    return df
