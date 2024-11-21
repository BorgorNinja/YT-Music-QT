import sys
import subprocess
import threading
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QListWidget, QLabel, QHBoxLayout, QSlider, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from youtubesearchpython import VideosSearch


class BackendWorker(QThread):
    update_progress_signal = pyqtSignal(int, str, str)
    playback_finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.url = None
        self.ffplay_proc = None
        self.is_running = False

    def run(self):
        if self.url:
            try:
                # yt-dlp command to stream audio
                yt_dl_cmd = [
                    "yt-dlp",
                    "--quiet",
                    "--no-warnings",
                    "--default-search=ytsearch",
                    "-f", "bestaudio",
                    "-o", "-",  # Output to stdout
                    self.url
                ]

                # ffplay to play from yt-dlp's stdout
                self.ffplay_proc = subprocess.Popen(
                    ["ffplay", "-autoexit", "-nodisp", "-i", "pipe:0"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                yt_dl_proc = subprocess.Popen(
                    yt_dl_cmd,
                    stdout=self.ffplay_proc.stdin,
                    stderr=subprocess.PIPE
                )

                self.is_running = True

                while self.is_running:
                    time.sleep(0.1)
                    output = self.ffplay_proc.stderr.readline().decode("utf-8")
                    if "time=" in output:
                        current_time = self.extract_time(output)
                        self.update_progress_signal.emit(0, time.strftime("%M:%S", time.gmtime(current_time)), "Streaming")

                    if self.ffplay_proc.poll() is not None:
                        break

                self.is_running = False
                self.playback_finished_signal.emit()

            except Exception as e:
                self.error_signal.emit(str(e))

    def stop(self):
        self.is_running = False
        if self.ffplay_proc:
            self.ffplay_proc.terminate()
            self.ffplay_proc = None

    def extract_time(self, output):
        # Extract current playback time from ffplay output (format: time=00:00:11.49)
        try:
            parts = output.split("time=")[1].split(" ")[0].split(":")
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        except (IndexError, ValueError):
            return 0


class YTMusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("YT Music Player")
        self.setGeometry(100, 100, 600, 400)

        self.backend_worker = BackendWorker()
        self.backend_worker.update_progress_signal.connect(self.update_progress)
        self.backend_worker.playback_finished_signal.connect(self.playback_finished)
        self.backend_worker.error_signal.connect(self.display_error)

        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Enter your search here...")
        layout.addWidget(self.search_input)

        search_button = QPushButton("Search", self)
        search_button.clicked.connect(self.search)
        layout.addWidget(search_button)

        self.result_list = QListWidget(self)
        layout.addWidget(self.result_list)

        self.result_list.itemClicked.connect(self.play_video)

        self.media_controls_layout = QVBoxLayout()

        self.title_label = QLabel("No music playing", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.media_controls_layout.addWidget(self.title_label)

        self.progress_slider = QSlider(Qt.Horizontal, self)
        self.progress_slider.setRange(0, 100)
        self.media_controls_layout.addWidget(self.progress_slider)

        controls_layout = QHBoxLayout()

        self.pause_button = QPushButton("Pause", self)
        self.pause_button.setEnabled(False)
        self.pause_button.clicked.connect(self.pause_resume)
        controls_layout.addWidget(self.pause_button)

        stop_button = QPushButton("Stop", self)
        stop_button.clicked.connect(self.stop_playback)
        controls_layout.addWidget(stop_button)

        self.media_controls_layout.addLayout(controls_layout)

        layout.addLayout(self.media_controls_layout)

        central_widget.setLayout(layout)

    def search(self):
        query = self.search_input.text()
        if query:
            threading.Thread(target=self.perform_search, args=(query,)).start()

    def perform_search(self, query):
        results = search_music(query)
        self.result_list.clear()
        for result in results:
            self.result_list.addItem(f"{result['title']} | {result['url']}")

    def play_video(self, item):
        if self.backend_worker.is_running:
            self.backend_worker.stop()
            self.backend_worker.wait()

        self.backend_worker.url = item.text().split('|')[-1].strip()
        self.title_label.setText(item.text().split('|')[0].strip())
        self.backend_worker.start()

        self.pause_button.setEnabled(True)

    @pyqtSlot(int, str, str)
    def update_progress(self, progress, elapsed_time, remaining_time):
        self.progress_slider.setValue(progress)
        self.title_label.setText(f"{self.title_label.text()} - {elapsed_time} / {remaining_time}")

    @pyqtSlot()
    def playback_finished(self):
        self.progress_slider.setValue(100)
        self.title_label.setText("Playback Finished")
        self.pause_button.setEnabled(False)

    @pyqtSlot(str)
    def display_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)

    def stop_playback(self):
        self.backend_worker.stop()
        self.pause_button.setEnabled(False)

    def pause_resume(self):
        if self.backend_worker.ffplay_proc:
            if self.backend_worker.is_running:
                self.backend_worker.ffplay_proc.terminate()
                self.backend_worker.is_running = False

    def closeEvent(self, event):
        self.backend_worker.stop()
        self.backend_worker.wait()
        event.accept()


def search_music(query):
    search = VideosSearch(query, limit=10)
    results = search.result()['result']
    return [{"title": entry["title"], "url": entry["link"]} for entry in results]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = YTMusicPlayer()
    player.show()
    sys.exit(app.exec_())
