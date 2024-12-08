"""
WordGPT - AI-Powered Vocabulary Card Generator for Anki
Copyright (c) 2024 jeongminc_
MIT License - See LICENSE file for details
"""

from aqt import mw, gui_hooks
from aqt.utils import showInfo, qconnect
from aqt.qt import *
from aqt.editor import Editor
import json
import requests
import time
from .config import config

BACKEND_URL = "https://wordgpt.onrender.com/generate"

class WordGPTSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("WordGPT Settings")
        self.current_config = config.get_config()
        self.setup_ui()
        self.setStyleSheet("""
            QDialog {
                background-color: #2f2f2f;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QCheckBox {
                color: white;
                font-size: 13px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton#restoreButton {
                background-color: #7f8c8d;
            }
            QPushButton#restoreButton:hover {
                background-color: #6c7a7d;
            }
        """)
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title section
        title_label = QLabel(" WordGPT Settings")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Content generation options group
        options_group = QGroupBox("Content Generation Options")
        options_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 1px solid #3f3f3f;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)
        options_layout = QVBoxLayout()
        
        self.synonyms_cb = QCheckBox("Include synonyms")
        self.examples_cb = QCheckBox("Include example sentences")
        
        self.synonyms_cb.setChecked(self.current_config.get('include_synonyms', True))
        self.examples_cb.setChecked(self.current_config.get('include_examples', True))
        
        options_layout.addWidget(self.synonyms_cb)
        options_layout.addWidget(self.examples_cb)
        options_group.setLayout(options_layout)
        
        layout.addWidget(options_group)
        
        button_box = QHBoxLayout()
        restore_button = QPushButton("Restore Defaults")
        restore_button.setObjectName("restoreButton")
        cancel_button = QPushButton("Cancel")
        ok_button = QPushButton("OK")
        
        button_box.addWidget(restore_button)
        button_box.addStretch()
        button_box.addWidget(cancel_button)
        button_box.addWidget(ok_button)
        
        cancel_button.clicked.connect(self.reject)
        ok_button.clicked.connect(self.save_and_close)
        restore_button.clicked.connect(self.restore_defaults)
        
        layout.addStretch()
        layout.addLayout(button_box)
        
        self.setLayout(layout)
        self.resize(400, 300)
        
    def save_and_close(self):
        new_config = {
            'include_synonyms': self.synonyms_cb.isChecked(),
            'include_examples': self.examples_cb.isChecked()
        }
        config.save_config(new_config)
        self.accept()
        
    def restore_defaults(self):
        self.synonyms_cb.setChecked(config.default_config['include_synonyms'])
        self.examples_cb.setChecked(config.default_config['include_examples'])

def show_settings():
    dialog = WordGPTSettingsDialog(mw)
    dialog.exec()

# Create settings action
settings_action = QAction("WordGPT Settings", mw)
qconnect(settings_action.triggered, show_settings)
mw.form.menuTools.addAction(settings_action)

def generate_card_content(word):
    """Generate card content using backend service"""
    try:
        current_config = config.get_config()
        response = requests.post(
            BACKEND_URL,
            json={
                "word": word,
                "include_synonyms": current_config.get('include_synonyms', True),
                "include_examples": current_config.get('include_examples', True)
            },
            timeout=30
        )
        
        if response.status_code != 200:
            showInfo(f"Service Error (Status {response.status_code}): {response.text}")
            return None
            
        content = response.json()
        if "error" in content:
            showInfo(f"Service Error: {content['error']}")
            return None
            
        return content
        
    except requests.exceptions.Timeout:
        showInfo("Service is taking too long to respond. Please try again later.")
        return None
        
    except requests.exceptions.ConnectionError:
        showInfo("Could not connect to the service. It might be down or starting up. Please try again in a minute.")
        return None
        
    except Exception as e:
        showInfo(f"Error generating content: {str(e)}")
        return None

def on_gpt_button_clicked(editor):
    """Handle WordGPT button click"""
    word = editor.note.fields[0]
    
    if not word:
        showInfo("Please enter a word in the front field first.")
        return
    
    content = generate_card_content(word)
    if not content:
        return
    
    current_config = config.get_config()
    back_content = f"Definition: {content['definition']}"
    
    if current_config.get('include_synonyms', True) and 'synonyms' in content:
        back_content += f"<br><br>Synonyms: {', '.join(content['synonyms'])}"
    
    if current_config.get('include_examples', True) and 'example' in content:
        back_content += f"<br><br>Example: {content['example']}"
    
    editor.note.fields[1] = back_content
    
    editor.loadNote()

def add_gpt_button(buttons, editor):
    """Add WordGPT button to the editor"""
    button = editor.addButton(
        icon=None,
        cmd="gpt_generate",
        func=lambda e: on_gpt_button_clicked(editor),
        tip="Generate content using ChatGPT",
        label="WordGPT"
    )
    buttons.append(button)
    return buttons

gui_hooks.editor_did_init_buttons.append(add_gpt_button)
