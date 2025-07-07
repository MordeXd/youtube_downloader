# 🎬 YouTube Downloader (1080p Max)

This project is a full-stack **YouTube Video Downloader** built with:

- 🧠 **Backend**: Flask + yt-dlp + ffmpeg  
- 🎨 **Frontend**: Streamlit  
- 🚀 **Deployment**: Render (backend), Streamlit Cloud (frontend)

---

## 📦 Features

✅ Paste any YouTube link  
✅ Shows title, duration, and thumbnail  
✅ Select MP4 quality up to **1080p**  
✅ One-click download  
✅ Video auto-deleted from server after sending  
✅ Clean, responsive UI

---

## 🚀 Deployment

### 🔧 Backend (Render)

1. Place backend files in `/backend`
2. Includes:
   - `app.py`
   - `requirements.txt`
   - `start.sh`
   - `render.yaml`
3. Deploy on [https://render.com](https://render.com)

### 🖼️ Frontend (Streamlit)

1. Place frontend file in `/frontend/streamlit_app.py`
2. Update backend URL inside Streamlit file to:
   ```
   https://your-render-backend.onrender.com
   ```
3. Deploy on [https://streamlit.io/cloud](https://streamlit.io/cloud)

---

## 📁 Project Structure

```
youtube_downloader/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── start.sh
│   └── render.yaml
├── frontend/
│   └── streamlit_app.py
├── .gitignore
└── README.md
```

---

## 🛡 Requirements

- Python 3.10+  
- `yt-dlp`, `ffmpeg`, `Flask`, `requests`, `streamlit`

---

## 💬 Credits

Made with ❤️ by Hardik Lodhari  
Frontend + Backend built for practice & real deployment

---

## 🧹 License

Free to use for educational purposes 🎓