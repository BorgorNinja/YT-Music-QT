# YT Music Player

YT Music Player is a lightweight YouTube music streaming application written in Python using PyQt5. It allows you to search for music, stream audio directly, and manage playback.

---

## Features
- **Real-time audio streaming**: Streams audio directly from YouTube using `yt-dlp` and `ffplay`.
- **Search functionality**: Easily find YouTube videos by title or keywords.
- **Playback controls**: Pause, stop, and monitor playback progress.
- **Minimal download**: Avoids full audio file downloads by using a streaming buffer.

---

## Requirements
Before running the application, ensure the following are installed:
- Python 3.7+
- `yt-dlp`
- `ffplay` (part of `ffmpeg`)
- Required Python libraries (see `requirements.txt`)

---

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/<your-username>/yt-music-player.git
   cd yt-music-player
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install `ffmpeg`**
   - On Linux:
     ```bash
     sudo apt-get install ffmpeg
     ```
   - On Windows:
     Download and set up `ffmpeg` from [ffmpeg.org](https://ffmpeg.org/).

---

## Usage

1. **Run the Application**
   ```bash
   python main.py
   ```

2. **Search for a Song**
   - Type a keyword in the search bar and hit **Search**.

3. **Stream Audio**
   - Select a song from the search results to begin streaming.
   - Use the playback controls to pause or stop the stream.

---

## Contributions
Feel free to open issues or submit pull requests to improve this application.

---

## License
This project is licensed under the GNU GPL v2.0 License. See `LICENSE` for details.
