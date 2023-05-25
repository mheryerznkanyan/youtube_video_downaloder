import streamlit as st
import pandas as pd
import base64
import pandas as pd
import os
from utils import search, download_csv, downalod_video


# Streamlit app
def main():
    st.title("CSV Generator")

    filepath = r"./"
    video_filepath = r"./ouput_videos"
    filename = "videos_data.csv"

    if not os.path.exists(video_filepath):
        os.makedirs(video_filepath)

    search_keyword = st.text_input("Enter searching text")
    videos_quantity = st.number_input("Enter number", value=0)

    if st.button("Generate CSV"):
        if search_keyword:
            data = search(search_keyword, videos_quantity)

            df = download_csv(data, filepath)
            df.to_csv(os.path.join(filepath, r"videos_data.csv"))
            map(lambda x: downalod_video(x, video_filepath), df["link"])

            st.success("CSV file generated!")
            st.success("Video files downlaoded!")

            with open(filename, "rb") as file:
                csv = file.read()
            b64 = base64.b64encode(csv).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.warning("Please enter some text.")


if __name__ == "__main__":
    main()
