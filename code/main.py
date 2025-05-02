### main.py
import sys
import tempfile
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QTextEdit, QLabel, QMessageBox, QSlider
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, Qt

from pdf_utils import extract_text_from_pdf
from translation import translate_text
from tts import text_to_speech
from file_utils import save_text_file, save_audio_file

class PDFTranslatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_lang = 'en'
        self.player = QMediaPlayer()
        self.audio_path = None
        self.temp_audio_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PDF Audio Translator")
        self.setGeometry(100, 100, 600, 450)

        layout = QVBoxLayout()

        self.text_display = QTextEdit(self)
        self.text_display.setPlaceholderText("Văn bản sẽ hiển thị ở đây...")

        open_button = QPushButton("Mở PDF", self)
        open_button.clicked.connect(self.open_pdf)

        translate_button = QPushButton("Dịch văn bản", self)
        translate_button.clicked.connect(self.translate_text)

        save_text_button = QPushButton("Lưu văn bản", self)
        save_text_button.clicked.connect(self.save_text)

        # Media control buttons layout
        media_layout = QHBoxLayout()

        play_button = QPushButton("Nghe thử giọng nói", self)
        play_button.clicked.connect(self.play_audio)

        pause_button = QPushButton("Tạm dừng phát", self)
        pause_button.clicked.connect(self.pause_audio)

        save_audio_button = QPushButton("Lưu Audio", self)
        save_audio_button.clicked.connect(self.convert_to_audio)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.valueChanged.connect(lambda val: self.player.setVolume(val))

        media_layout.addWidget(play_button)
        media_layout.addWidget(pause_button)
        media_layout.addWidget(save_audio_button)
        media_layout.addWidget(QLabel("Âm lượng:"))
        media_layout.addWidget(self.volume_slider)

        # Progress slider
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.sliderMoved.connect(self.set_position)
        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)

        # Language buttons
        lang_layout = QHBoxLayout()
        self.en_button = QPushButton("English", self)
        self.vi_button = QPushButton("Tiếng Việt", self)
        self.en_button.clicked.connect(lambda: self.set_language('en'))
        self.vi_button.clicked.connect(lambda: self.set_language('vi'))
        lang_layout.addWidget(QLabel("Chọn ngôn ngữ dịch/đọc:"))
        lang_layout.addWidget(self.en_button)
        lang_layout.addWidget(self.vi_button)
        self.set_language('en')

        layout.addWidget(open_button)
        layout.addWidget(self.text_display)
        layout.addLayout(lang_layout)
        layout.addWidget(translate_button)
        layout.addWidget(save_text_button)
        layout.addLayout(media_layout)
        layout.addWidget(self.progress_slider)

        self.setLayout(layout)

    def set_language(self, lang):
        self.selected_lang = lang
        if lang == 'en':
            self.en_button.setStyleSheet("background-color: lightblue")
            self.vi_button.setStyleSheet("")
        else:
            self.vi_button.setStyleSheet("background-color: lightblue")
            self.en_button.setStyleSheet("")

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file PDF", "", "PDF files (*.pdf)")
        if file_path:
            text = extract_text_from_pdf(file_path)
            self.text_display.setPlainText(text)

    def translate_text(self):
        text = self.text_display.toPlainText()
        if text:
            translated = translate_text(text, self.selected_lang)
            self.text_display.setPlainText(translated)

    def save_text(self):
        text = self.text_display.toPlainText()
        if text:
            save_text_file(text)

    def convert_to_audio(self):
        text = self.text_display.toPlainText()
        if text:
            audio = text_to_speech(text, self.selected_lang)
            path = save_audio_file(audio)
            if path:
                self.audio_path = path

    def play_audio(self):
        text = self.text_display.toPlainText()
        if text:
            tts = text_to_speech(text, self.selected_lang)
            temp_fd, temp_path = tempfile.mkstemp(suffix='.mp3')
            os.close(temp_fd)
            tts.save(temp_path)
            self.temp_audio_path = temp_path
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(temp_path)))
            self.player.play()
        else:
            QMessageBox.warning(self, "Lỗi", "Không có nội dung để chuyển thành giọng nói.")

    def pause_audio(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        elif self.player.state() == QMediaPlayer.PausedState:
            self.player.play()

    def update_position(self, position):
        if self.player.duration() > 0:
            self.progress_slider.setValue(int(position * 100 / self.player.duration()))

    def update_duration(self, duration):
        self.progress_slider.setRange(0, 100)

    def set_position(self, value):
        if self.player.duration() > 0:
            position = int(value * self.player.duration() / 100)
            self.player.setPosition(position)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFTranslatorApp()
    window.show()
    sys.exit(app.exec_())