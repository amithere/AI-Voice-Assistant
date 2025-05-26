from PyQt5.QtWidgets import QApplication, QLayout, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit, QStackedWidget, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QLabel, QToolButton
from PyQt5.QtGui import QIcon, QFont, QColor, QPainter, QMovie, QTextCharFormat, QTextCharFormat, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

env_vars = dotenv_values(".env")
AssistantName = env_vars.get("ASSISTANT_NAME")
current_dir = os.getcwd()
old_chat_message = ""
TempDirPath = rf"{current_dir}/Frontend/Files"
GraphicsDirPath = rf"{current_dir}/Frontend/Graphics"

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["what", "who", "where", "when", "why", "how", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
        
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query += new_query[:-1] + "."
        else:
            new_query += "."
    
    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(rf"{TempDirPath}/Mic.data", "w", encoding="utf-8") as file:
        file.write(Command)

def GetMicrophoneStatus():
    with open(rf"{TempDirPath}/Mic.data", "r", encoding="utf-8") as file:
        return file.read()

def SetAssistantStatus(Status):
    with open(rf"{TempDirPath}/Status.data", "w", encoding="utf-8") as file:
        file.write(Status)

def GetAssistantStatus():
    with open(rf"{TempDirPath}/Status.data", "r", encoding="utf-8") as file:
        return file.read()

def MicButtonInitialized():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    Path = rf"{GraphicsDirPath}/{Filename}"
    return Path

def TempDirectoryPath(Filename):
    Path = rf"{TempDirPath}/{Filename}"
    return Path

def ensure_temp_dir():
    if not os.path.exists(TempDirPath):
        os.makedirs(TempDirPath)

def ShowTextToScreen(Text):
    ensure_temp_dir()
    with open(rf"{TempDirPath}/Responses.data", "w", encoding="utf-8") as file:
        file.write(Text)

class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()

        self.toggled = False  # Initialize toggle state

        layout = QVBoxLayout(self)

        # Add mic icon label
        self.icon_label = QLabel()
        layout.addWidget(self.icon_label)

        # Replace self.gif_label with a clickable tool button
        self.icon_button = QToolButton()
        self.icon_button.setStyleSheet("border: none; background-color: black;")
        self.icon_button.setIcon(QIcon(GraphicsDirectoryPath("Mic_off.png")))  # initial icon
        self.icon_button.setIconSize(QSize(60, 60))
        self.icon_button.clicked.connect(self.toggle_icon)
        
        layout.addWidget(self.icon_button, alignment=Qt.AlignCenter)


        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)
        self.setStyleSheet("background-color: black;")
        layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding))
        text_color = QColor(Qt.blue)
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(GraphicsDirectoryPath("Voice_Assistant_By_Amit.gif"))
        max_gif_size_Width = 300
        max_gif_size_Height = 300
        movie.setScaledSize(QSize(max_gif_size_Width, max_gif_size_Height))
        self.gif_label.setMovie(movie)
        self.gif_label.setAlignment(Qt.AlignRight)
        movie.start()
        layout.addWidget(self.gif_label)
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 16px; margin-right: 195px; border: none; margin-top: -30px")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)
        layout.setSpacing(-10)
        layout.addWidget(self.gif_label)
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)
        self.chat_text_edit.viewport().installEventFilter(self)
        self.setStyleSheet("""
                          QScrollBar:vertical {
                              border: none;
                              background: black;
                              width: 10px;
                              margin: 0px 0px 0px 0px;
                           }
                            QScrollBar::handle:vertical {
                                background: white;
                                min-height: 20px;
                            }
                           
                           QScrollBar::add-line:vertical {
                                 background: black;
                                 subcontrol-position: bottom;
                                 subcontrol-origin: margin;
                                 height: 0px;   
                            }
                           
                            QScrollBar::sub-line:vertical {
                                    background: black;
                                    subcontrol-position: top;
                                    subcontrol-origin: margin;
                                    height: 10px;   
                                }
                            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                                background: none;
                                border: none;
                                color: none;
                            }
                           
                           QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                                background: none;
                            }

                        """)

    import os  # Make sure you have this imported

    def loadMessages(self):
        global old_chat_message

        # Ensure the Temp directory exists
        if not os.path.exists(TempDirPath):
            os.makedirs(TempDirPath)

        file_path = rf"{TempDirPath}/Responses.data"

        # Check if the file exists before reading
        if not os.path.isfile(file_path):
            # If file doesn't exist, just skip reading or create an empty file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("")  # create empty file
            return  # No messages to load yet

        with open(file_path, "r", encoding="utf-8") as file:
            messages = file.read()

            if messages is None or len(messages) <= 1:
                return

            if str(old_chat_message) == str(messages):
                return

            self.addMessage(message=messages, color='white')
            old_chat_message = messages


    def SpeechRecogText(self):
        with open(rf"{TempDirPath}/Status.data", "r", encoding="utf-8") as file:
            messages = file.read()
            self.label.setText(messages)

    def load_icon(self, path):
        self.icon_button.setIcon(QIcon(path))

    def toggle_icon(self):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath("Mic_on.png"))
            MicButtonInitialized()
        else:
            self.load_icon(GraphicsDirectoryPath("Mic_off.png"))
            MicButtonClosed()

        self.toggled = not self.toggled

    def addMessage(self, message, color):
        cursor =  self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + '\n')
        self.chat_text_edit.setTextCursor(cursor)

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout(self)
        label = QLabel("")
        layout.addWidget(label)
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.initUI()
        self.current_screen = None
        self.stacked_widget = stacked_widget

    def initUI(self):
        self.setFixedHeight(60)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)
        home_button = QPushButton()
        home_icon = QIcon(GraphicsDirectoryPath("Home.png"))
        home_button.setIcon(home_icon)
        home_button.setText(" Home")
        home_button.setStyleSheet("height: 40px; line-height: 40px; background-color: white; color: black;")
        message_button = QPushButton()
        message_icon = QIcon(GraphicsDirectoryPath("Chats.png"))
        message_button.setIcon(message_icon)
        message_button.setText(" Chats")
        message_button.setStyleSheet("height: 40px; line-height: 40px; background-color: white; color: black;")
        minimize_button = QPushButton()
        minimize_icon = QIcon(GraphicsDirectoryPath("Minimize.png"))
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet("background-color: white;")
        minimize_button.clicked.connect(self.minimizeWindow)
        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath("Maximize.png"))
        self.restore_icon = QIcon(GraphicsDirectoryPath("Minimize.png"))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("background-color: white;")
        self.maximize_button.clicked.connect(self.maximizeWindow)
        close_button = QPushButton()
        close_icon = QIcon(GraphicsDirectoryPath("Close.png"))
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color: white;")
        close_button.clicked.connect(self.closeWindow)
        line_frame = QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape(QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet("border-color: black;")
        title_label = QLabel(f"{str(AssistantName).capitalize()} AI  ")
        title_label.setStyleSheet("color: black; font-size: 18px; background-color: white;")
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        layout.addWidget(line_frame)
        self.draggable = True
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent().close()

    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)
    
    def showMessageScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()

        message_screen = MessageScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(message_screen)

        self.current_screen = message_screen

    def showInitialScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()
        
        initial_screen = InitialScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(initial_screen)

        self.current_screen = initial_screen

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        label = QLabel("Welcome to the Voice Assistant!")
        layout.addWidget(label)

        self.setLayout(layout)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)
        
def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
        GraphicalUserInterface()


    
