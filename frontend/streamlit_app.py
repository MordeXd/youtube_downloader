import streamlit as st
import requests

st.set_page_config(page_title="YouTube Downloader", layout="centered")
st.title("📥 YouTube Video Downloader")

# Session state for storing data
if "video_info" not in st.session_state:
    st.session_state.video_info = None
if "url" not in st.session_state:
    st.session_state.url = ""

# Input box
url = st.text_input("🔗 Enter YouTube URL:", value=st.session_state.url)

# Fetch video info
if st.button("🔍 Fetch Info") and url:
    with st.spinner("Fetching video info..."):
        try:
            res = requests.post("http://127.0.0.1:5000/info", json={"url": url})
            data = res.json()

            if "error" in data:
                st.error("❌ " + data["error"])
            else:
                st.session_state.video_info = data
                st.session_state.url = url
        except Exception as e:
            st.error(f"⚠️ Error: {e}")

# Show info if available
if st.session_state.video_info:
    data = st.session_state.video_info
    st.image(data["thumbnail"], width=480)
    st.subheader(data["title"])
    st.caption("⏱️ Duration: " + data["duration"])

    format_options = {
        f"{f['resolution']} • {f['ext']} • {f['filesize']} MB": f['format_id']
        for f in data['formats']
    }

    selected = st.selectbox("🎞️ Choose Quality", list(format_options.keys()))
    download_btn = st.button("📥 Download Video")

    if download_btn:
        format_id = format_options[selected]
        with st.spinner("Downloading... please wait ⏳"):
            try:
                response = requests.post("http://127.0.0.1:5000/download", json={
                    "url": st.session_state.url,
                    "format_id": format_id
                })

                if response.status_code == 200:
                    st.success("✅ Download ready!")
                    st.download_button(
                        label="🎬 Save Video to Your Device",
                        data=response.content,
                        file_name=data["title"] + ".mp4",
                        mime="video/mp4"
                    )
                else:
                    st.error("❌ Failed to download the video.")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
