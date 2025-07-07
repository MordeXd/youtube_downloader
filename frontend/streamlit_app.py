import streamlit as st
import requests
import os

# ✅ Your deployed backend URL
BACKEND_URL = "https://youtube-downloader-79m2.onrender.com"

st.set_page_config(page_title="🎥 YouTube Downloader", layout="centered")
st.title("📥 YouTube Video Downloader")

url = st.text_input("🔗 Paste a YouTube video link")

if url:
    if st.button("🔍 Get Video Info"):
        with st.spinner("Fetching video info..."):
            try:
                response = requests.post(f"{BACKEND_URL}/info", json={"url": url})

                st.write("📡 Status:", response.status_code)

                if response.ok:
                    try:
                        data = response.json()

                        st.success("✅ Video info fetched successfully!")
                        st.image(data.get("thumbnail", ""))
                        st.markdown(f"**🎬 Title:** {data.get('title')}")
                        st.markdown(f"**⏱️ Duration:** {data.get('duration')}")

                        formats = data.get("formats", [])
                        qualities = [
                            f"{f['resolution']} • {f['ext']} • {round(f['filesize'] / 1_000_000, 2)} MB"
                            for f in formats if f.get("filesize")
                        ]

                        selected = st.selectbox("📺 Choose Quality", qualities)

                        if st.button("⬇️ Download"):
                            selected_format = formats[qualities.index(selected)]

                            with st.spinner("Downloading video..."):
                                download_res = requests.post(
                                    f"{BACKEND_URL}/download",
                                    json={"url": url, "format_id": selected_format["format_id"]}
                                )

                                if download_res.ok:
                                    st.success("✅ Download complete!")

                                    filename = download_res.headers.get("X-Filename", "video.mp4")
                                    with open("temp_video.mp4", "wb") as f:
                                        f.write(download_res.content)

                                    with open("temp_video.mp4", "rb") as f:
                                        st.download_button(
                                            label="📥 Save to your device",
                                            data=f,
                                            file_name=filename,
                                            mime="video/mp4"
                                        )

                                    os.remove("temp_video.mp4")

                                else:
                                    st.error("❌ Download failed")
                                    st.code(download_res.text)

                    except Exception as e:
                        st.error("❌ Could not parse backend response")
                        st.exception(e)
                        st.code(response.text)
                else:
                    st.error("❌ Failed to get video info")
                    st.code(response.text)

            except requests.exceptions.RequestException as e:
                st.error("❌ Could not connect to backend")
                st.exception(e)
