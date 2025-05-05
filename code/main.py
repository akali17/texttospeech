### main.py
import sys
import tempfile
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QTextEdit, QLabel, QMessageBox, QSlider, QProgressBar
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

from pdf_utils import extract_text_from_pdf
from translation import translate_text
from tts import text_to_speech
from file_utils import save_text_file, save_audio_file

class PDFTranslatorApp(QWidget):
    def __init__(self):
        super().__init__()
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
        
        self.selected_lang = 'en'
        self.player = QMediaPlayer()
        self.audio_path = None
        self.temp_audio_path = None
        self.current_file = None
        self.is_processing = False
        self.original_text = ""
        self.init_ui()
        self.setAcceptDrops(True)

    def init_ui(self):
        self.setWindowTitle("PDF Audio Translator")
        self.setGeometry(100, 100, 800, 600)
        
        # Main stylesheet
        self.setStyleSheet("""
            QWidget {
                font-size: 14px;
            }
            QPushButton {
                padding: 8px;
                min-width: 100px;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
            }
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
            #DropArea {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 20px;
                text-align: center;
                background-color: #f9f9f9;
                font-size: 16px;
                color: #666;
            }
            #FileInfo {
                font-weight: bold;
                color: #333;
                padding: 8px;
                background-color: #f0f0f0;
                border-radius: 3px;
                border: 1px solid #ddd;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #ddd;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                width: 16px;
                height: 16px;
                background: #4CAF50;
                border-radius: 8px;
                margin: -4px 0;
            }
            #TimeLabel {
                font-family: monospace;
                min-width: 60px;
                text-align: center;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Drag and drop area
        self.drop_area = QLabel("Kéo và thả file PDF vào đây hoặc nhấn nút 'Mở PDF'", self)
        self.drop_area.setObjectName("DropArea")
        self.drop_area.setAlignment(Qt.AlignCenter)
        self.drop_area.setFixedHeight(80)
        self.drop_area.setAcceptDrops(True)

        # Current file info
        self.file_info = QLabel("", self)
        self.file_info.setObjectName("FileInfo")
        self.file_info.setAlignment(Qt.AlignCenter)
        self.file_info.setVisible(False)

        # Text display
        self.text_display = QTextEdit(self)
        self.text_display.setPlaceholderText("Văn bản sẽ hiển thị ở đây...")

        # Progress bar for operations
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        open_button = QPushButton("Mở PDF", self)
        open_button.clicked.connect(self.open_pdf)

        translate_button = QPushButton("Dịch văn bản", self)
        translate_button.clicked.connect(self.translate_text)

        save_text_button = QPushButton("Lưu văn bản", self)
        save_text_button.clicked.connect(self.save_text)

        buttons_layout.addWidget(open_button)
        buttons_layout.addWidget(translate_button)
        buttons_layout.addWidget(save_text_button)

        # Media control buttons layout
        media_layout = QHBoxLayout()
        media_layout.setSpacing(10)

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

        # Timeline control
        time_layout = QHBoxLayout()
        
        # Progress slider
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.sliderMoved.connect(self.set_position)

        time_layout.addWidget(self.progress_slider)

        # Connect signal from player
        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)

        # Language buttons
        lang_layout = QHBoxLayout()
        lang_layout.setSpacing(10)
        self.en_button = QPushButton("English", self)
        self.vi_button = QPushButton("Tiếng Việt", self)
        self.en_button.clicked.connect(lambda: self.set_language('en'))
        self.vi_button.clicked.connect(lambda: self.set_language('vi'))
        lang_layout.addWidget(QLabel("Chọn ngôn ngữ dịch/đọc:"))
        lang_layout.addWidget(self.en_button)
        lang_layout.addWidget(self.vi_button)
        self.set_language('en')

        # Add widgets to main layout
        layout.addWidget(self.drop_area)
        layout.addWidget(self.file_info)
        layout.addWidget(self.text_display)
        layout.addWidget(self.progress_bar)
        layout.addLayout(buttons_layout)
        layout.addLayout(lang_layout)
        layout.addLayout(media_layout)
        layout.addLayout(time_layout)

        self.setLayout(layout)

    def format_time(self, ms):
        """Chuyển milliseconds sang định dạng mm:ss"""
        seconds = int(ms / 1000)
        return f"{seconds//60:02d}:{seconds%60:02d}"

    def update_position(self, position):
        """Cập nhật thời gian hiện tại và thanh trượt"""
        if self.player.duration() > 0:
            self.progress_slider.setValue(int(position * 100 / self.player.duration()))
            self.current_time_label.setText(self.format_time(position))

    def update_duration(self, duration):
        """Cập nhật tổng thời lượng audio"""
        self.total_time_label.setText(self.format_time(duration))

    def set_position(self, value):
        """Xử lý khi người dùng kéo thanh trượt"""
        if self.player.duration() > 0:
            position = int(value * self.player.duration() / 100)
            self.player.setPosition(position)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].toLocalFile().lower().endswith('.pdf'):
                event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        file_path = event.mimeData().urls()[0].toLocalFile()
        self.load_pdf(file_path)

    def load_pdf(self, file_path):
        self.current_file = file_path
        self.file_info.setText(f"File đang mở: {os.path.basename(file_path)}")
        self.file_info.setVisible(True)
        
        self.show_loading(True, "Đang đọc file PDF...")
        QTimer.singleShot(100, lambda: self.process_pdf(file_path))

    def process_pdf(self, file_path):
        try:
            text = extract_text_from_pdf(file_path)
            self.text_display.setPlainText(text)
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể đọc file PDF: {str(e)}")
        finally:
            self.show_loading(False)

    def show_loading(self, show, message=None):
        self.is_processing = show
        self.progress_bar.setVisible(show)
        if show:
            self.progress_bar.setFormat(message)
            self.progress_bar.setValue(0)
        else:
            self.progress_bar.setValue(100)
            QTimer.singleShot(500, lambda: self.progress_bar.setVisible(False))

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
            self.load_pdf(file_path)

    def translate_text(self):
        text = self.text_display.toPlainText()
        if text:
            self.show_loading(True, "Đang dịch văn bản...")
            QTimer.singleShot(100, lambda: self.process_translation(text))

    def process_translation(self, text):
        try:
            translated = translate_text(text, self.selected_lang)
            self.text_display.setPlainText(translated)
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể dịch văn bản: {str(e)}")
        finally:
            self.show_loading(False)

    def save_text(self):
        text = self.text_display.toPlainText()
        if text:
            save_text_file(text)

    def convert_to_audio(self):
        text = self.text_display.toPlainText()
        if text:
            self.show_loading(True, "Đang tạo file audio...")
            QTimer.singleShot(100, lambda: self.process_audio_conversion(text))

    def process_audio_conversion(self, text):
        try:
            audio = text_to_speech(text, self.selected_lang)
            path = save_audio_file(audio)
            if path:
                self.audio_path = path
                QMessageBox.information(self, "Thành công", f"Đã lưu file audio tại: {path}")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tạo file audio: {str(e)}")
        finally:
            self.show_loading(False)

    def play_audio(self):
        text = self.text_display.toPlainText()
        if text:
            self.show_loading(True, "Đang chuẩn bị phát audio...")
            QTimer.singleShot(100, lambda: self.process_audio_playback(text))

    def process_audio_playback(self, text):
        try:
            tts = text_to_speech(text, self.selected_lang)
            temp_fd, temp_path = tempfile.mkstemp(suffix='.mp3')
            os.close(temp_fd)
            tts.save(temp_path)
            self.temp_audio_path = temp_path
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(temp_path)))
            self.player.play()
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể phát audio: {str(e)}")
        finally:
            self.show_loading(False)

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
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QApplication(sys.argv)
    window = PDFTranslatorApp()
    window.show()
    sys.exit(app.exec_())