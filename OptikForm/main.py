import sys
import os
import json
import datetime
import glob
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QGridLayout, 
                            QScrollArea, QTabWidget, QLineEdit, QComboBox, 
                            QMessageBox, QFrame, QSizePolicy, QTableWidget,
                            QTableWidgetItem, QHeaderView, QSplitter)
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QIcon, QFont, QColor, QPixmap, QPainter

class OptionButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(25, 25)
        self.setMaximumSize(30, 30)
        self.setStyleSheet("""
            QPushButton {
                border: 1px solid #ccc;
                border-radius: 15px;
                padding: 0px;
                background-color: #f8f9fa;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:checked {
                background-color: #4CAF50;
                color: white;
                border-color: #388E3C;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)

class Question(QWidget):
    def __init__(self, question_number, parent=None):
        super().__init__(parent)
        self.question_number = question_number
        self.selected_option = None
        self.correct_answer = None
        self.is_locked = False
        self.is_correct = False
        self.is_checked = False
        self.was_empty = False
        self.test_tab = None  # TestTab referansı
        self.state = "unmarked"  # unmarked, correct, wrong, empty olabilir
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)  # Daha az boşluk
        main_layout.setSpacing(3)  # Daha az boşluk
        self.setLayout(main_layout)
        
        # Soru numarası gösterimi
        question_container = QWidget()
        question_container.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        question_container.setMinimumWidth(20)
        question_container.setMaximumWidth(35)
        question_layout = QHBoxLayout(question_container)
        question_layout.setContentsMargins(0, 0, 0, 0)
        
        self.question_label = QLabel(f"{question_number}.")
        self.question_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        self.question_label.setFont(font)
        question_layout.addWidget(self.question_label)
        
        main_layout.addWidget(question_container)
        
        # Şıklar
        options_container = QWidget()
        options_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        options_layout = QHBoxLayout(options_container)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(5)  # Şıklar arası boşluk azaltıldı
        
        self.options = {}
        for option in ['A', 'B', 'C', 'D', 'E']:
            btn = OptionButton(option)
            btn.clicked.connect(lambda checked, opt=option: self.select_option(opt))
            self.options[option] = btn
            options_layout.addWidget(btn)
        
        main_layout.addWidget(options_container)
        
        # Doğru/Yanlış/Boş göstergeleri
        self.indicators_container = QWidget()
        self.indicators_container.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.indicators_container.setMinimumWidth(80)
        self.indicators_container.setMaximumWidth(100)
        indicators_layout = QHBoxLayout(self.indicators_container)
        indicators_layout.setContentsMargins(0, 0, 0, 0)
        indicators_layout.setSpacing(3)
        
        # Doğru işaret
        self.correct_btn = QPushButton("✓")
        self.correct_btn.setMinimumSize(20, 20)
        self.correct_btn.setMaximumSize(25, 25)
        self.correct_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.correct_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4CAF50;
                color: white;
            }
        """)
        self.correct_btn.setToolTip("Doğru olarak işaretle")
        self.correct_btn.clicked.connect(lambda: self.mark_state("correct"))
        indicators_layout.addWidget(self.correct_btn)
        
        # Yanlış işaret
        self.wrong_btn = QPushButton("✗")
        self.wrong_btn.setMinimumSize(20, 20)
        self.wrong_btn.setMaximumSize(25, 25)
        self.wrong_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.wrong_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f44336;
                color: white;
            }
        """)
        self.wrong_btn.setToolTip("Yanlış olarak işaretle")
        self.wrong_btn.clicked.connect(lambda: self.mark_state("wrong"))
        indicators_layout.addWidget(self.wrong_btn)
        
        # Boş işaret
        self.empty_btn = QPushButton("○")
        self.empty_btn.setMinimumSize(20, 20)
        self.empty_btn.setMaximumSize(25, 25)
        self.empty_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.empty_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2196F3;
                color: white;
            }
        """)
        self.empty_btn.setToolTip("Boş olarak işaretle")
        self.empty_btn.clicked.connect(lambda: self.mark_state("empty"))
        indicators_layout.addWidget(self.empty_btn)
        
        main_layout.addWidget(self.indicators_container)
        
        # Arka planı hafif gri yapalım
        self.setStyleSheet("background-color: #f5f5f5; border-radius: 5px;")
        
        # Layout boşluklarını ayarlayalım
        main_layout.setStretch(0, 1)  # Soru numarası
        main_layout.setStretch(1, 3)  # Şıklar
        main_layout.setStretch(2, 2)  # Durum göstergeleri
        
    def select_option(self, option):
        # Eğer kilitliyse ve boş değilse şık seçimi devre dışı
        if self.is_locked and self.state != "empty":
            return
        
        # Eğer doğru veya yanlış işaretlendiyse değiştirme
        if self.state == "correct" or self.state == "wrong":
            return
            
        # Eğer aynı şık tekrar tıklanırsa, seçimi kaldır
        if self.selected_option == option:
            # Seçimi temizle
            self.selected_option = None
            # Şık stilini normale çevir
            for opt, btn in self.options.items():
                btn.setChecked(False)
                btn.setStyleSheet("""
                    QPushButton {
                        border: 1px solid #ccc;
                        border-radius: 15px;
                        padding: 0px;
                        background-color: #f8f9fa;
                        font-weight: bold;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #e9ecef;
                    }
                    QPushButton:checked {
                        background-color: #4CAF50;
                        color: white;
                        border-color: #388E3C;
                    }
                """)
            # TestTab'ı bilgilendir
            if self.test_tab:
                self.test_tab.calculate_and_show_results()
            return
            
        # Eğer durum boş olarak işaretlendiyse, özel durumu ele al
        if self.state == "empty":
            # Önce diğer tüm şıkları temizle
            for opt, btn in self.options.items():
                if opt != option:
                    btn.setChecked(False)
                    btn.setStyleSheet("""
                        QPushButton {
                            border: 1px solid #ccc;
                            border-radius: 15px;
                            padding: 0px;
                            background-color: #f8f9fa;
                            font-weight: bold;
                            font-size: 11px;
                        }
                        QPushButton:checked {
                            background-color: #4CAF50;
                            color: white;
                            border-color: #388E3C;
                        }
                        QPushButton:hover {
                            background-color: #e9ecef;
                        }
                    """)
                
            # Şimdi seçilen şıkkı işaretle ve mavi yap
            self.options[option].setChecked(True)
            self.options[option].setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: 1px solid #ccc;
                    border-radius: 15px;
                    padding: 0px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:checked {
                    background-color: #2196F3;
                    color: white;
                    border-color: #1565C0;
                }
            """)
            self.selected_option = option
            
            # TestTab'ı bilgilendir
            if self.test_tab:
                self.test_tab.calculate_and_show_results()
            
            return
            
        # Normal şık seçimi (boş değilse)
        if self.state != "empty":
            # Eğer yanlış olarak işaretlendiyse
            if self.state == "wrong" and self.selected_option:
                # Yanlış işaretli şıkkı kırmızıda bırak
                # Ve doğru şıkkı işaretle
                self.correct_answer = option
                self.options[option].setChecked(True)
                self.options[option].setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: 1px solid #ddd;
                        border-radius: 15px;
                        padding: 0px;
                        font-weight: bold;
                        font-size: 11px;
                    }
                    QPushButton:checked {
                        background-color: #4CAF50;
                        color: white;
                        border-color: #388E3C;
                    }
                """)
                return
                
            # Normal şık seçimi
            for opt, btn in self.options.items():
                if opt != option:
                    btn.setChecked(False)
                    
            self.selected_option = option
            self.options[option].setChecked(True)
    
    def mark_state(self, state):
        """Sorunun durumunu işaretle (doğru, yanlış, boş)"""
        
        # Eğer aynı duruma tekrar tıklandıysa, durumu normale döndür
        if self.state == state:
            # Durumu sıfırla (unmarked)
            self.state = "unmarked"
            
            # Tüm gösterge butonlarını normale döndür
            self.correct_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    color: #333;
                    border-radius: 12px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #4CAF50;
                    color: white;
                }
            """)
            self.wrong_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    color: #333;
                    border-radius: 12px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #f44336;
                    color: white;
                }
            """)
            self.empty_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    color: #333;
                    border-radius: 12px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #9e9e9e;
                    color: white;
                }
            """)
            
            # Seçilen şıkkı normal yap (eğer varsa)
            if self.selected_option:
                # Normal seçili şık stili
                self.options[self.selected_option].setChecked(True)
                self.options[self.selected_option].setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: 1px solid #ddd;
                        border-radius: 15px;
                        padding: 0px;
                        font-weight: bold;
                        font-size: 11px;
                    }
                    QPushButton:checked {
                        background-color: #4CAF50;
                        color: white;
                        border-color: #388E3C;
                    }
                """)
            
            # TestTab'ı bilgilendir
            if self.test_tab:
                self.test_tab.calculate_and_show_results()
                
            return
            
        # Normal state değiştirme (farklı bir state seçildiğinde)
        self.state = state
        
        # İşaretlerine göre butonların renklerini güncelle
        if state == "correct":
            self.correct_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 12px;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
            self.wrong_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    color: #333;
                    border-radius: 12px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #f44336;
                    color: white;
                }
            """)
            self.empty_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    color: #333;
                    border-radius: 12px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #9e9e9e;
                    color: white;
                }
            """)
            
            # Seçilen şıkkı yeşil yap
            if self.selected_option:
                self.correct_answer = self.selected_option
                self.is_correct = True
                self.options[self.selected_option].setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: 1px solid #ddd;
                        border-radius: 15px;
                        padding: 0px;
                        font-weight: bold;
                        font-size: 11px;
                    }
                    QPushButton:checked {
                        background-color: #4CAF50;
                        color: white;
                        border-color: #388E3C;
                    }
                """)
        
        elif state == "wrong":
            self.correct_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    color: #333;
                    border-radius: 12px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #4CAF50;
                    color: white;
                }
            """)
            self.wrong_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border-radius: 12px;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
            self.empty_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    color: #333;
                    border-radius: 12px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #9e9e9e;
                    color: white;
                }
            """)
            
            # Seçilen şıkkı kırmızı yap
            if self.selected_option:
                self.is_correct = False
                self.options[self.selected_option].setStyleSheet("""
                    QPushButton {
                        background-color: #f44336;
                        color: white;
                        border: 1px solid #ddd;
                        border-radius: 15px;
                        padding: 0px;
                        font-weight: bold;
                        font-size: 11px;
                    }
                    QPushButton:checked {
                        background-color: #f44336;
                        color: white;
                        border-color: #B71C1C;
                    }
                """)
        
        elif state == "empty":
            self.correct_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    color: #333;
                    border-radius: 12px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #4CAF50;
                    color: white;
                }
            """)
            self.wrong_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    color: #333;
                    border-radius: 12px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #f44336;
                    color: white;
                }
            """)
            self.empty_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border-radius: 12px;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
            
            # Eğer seçilmiş bir şık varsa onu mavi yap
            if self.selected_option:
                self.options[self.selected_option].setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: 1px solid #ccc;
                        border-radius: 15px;
                        padding: 0px;
                        font-weight: bold;
                        font-size: 11px;
                    }
                    QPushButton:checked {
                        background-color: #2196F3;
                        color: white;
                        border-color: #1565C0;
                    }
                """)
            
            # Diğer şıkları sıfırla
            for opt, btn in self.options.items():
                if opt != self.selected_option:
                    btn.setChecked(False)
                    btn.setStyleSheet("""
                        QPushButton {
                            border: 1px solid #ccc;
                            border-radius: 15px;
                            padding: 0px;
                            background-color: #f8f9fa;
                            font-weight: bold;
                            font-size: 11px;
                        }
                        QPushButton:checked {
                            background-color: #4CAF50;
                            color: white;
                            border-color: #388E3C;
                        }
                        QPushButton:hover {
                            background-color: #e9ecef;
                        }
                    """)
            
            self.is_correct = False
            self.was_empty = True
            
        # TestTab'ı bilgilendir
        if self.test_tab:
            self.test_tab.calculate_and_show_results()
    
    def lock_options(self):
        """Sınavı bitir işlemi - sadece durumu kaydet, değişiklik yapma"""
        self.is_locked = True
        
    def reset(self):
        """Soruyu sıfırla"""
        self.selected_option = None
        self.correct_answer = None
        self.is_locked = False
        self.is_correct = False
        self.is_checked = False
        self.was_empty = False
        self.state = "unmarked"
        
        # Şıkları sıfırla
        for opt, btn in self.options.items():
            btn.setChecked(False)
            btn.setStyleSheet("""
                QPushButton {
                    border: 1px solid #ccc;
                    border-radius: 15px;
                    padding: 0px;
                    background-color: #f8f9fa;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:checked {
                    background-color: #4CAF50;
                    color: white;
                    border-color: #388E3C;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                }
            """)
            
        # İşaretleri sıfırla
        self.correct_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4CAF50;
                color: white;
            }
        """)
        self.wrong_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f44336;
                color: white;
            }
        """)
        self.empty_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #9e9e9e;
                color: white;
            }
        """)

class TestTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.questions = []
        self.is_test_completed = False
        self.wrong_ratio = 4  # Default: 4 wrong answers cancel 1 correct
        self.test_saved = False  # Test kaydedildi mi?
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(5, 5, 5, 5)  # Daha az kenar boşluğu
        self.main_layout.setSpacing(5)  # Daha az dikey boşluk
        self.setLayout(self.main_layout)
        
        # Test Settings - Başlık ve Ayarlar Bölümü
        settings_frame = QFrame()
        settings_frame.setFrameShape(QFrame.StyledPanel)
        settings_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 5px;")
        settings_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        settings_layout = QHBoxLayout(settings_frame)
        settings_layout.setContentsMargins(5, 5, 5, 5)  # Daha az iç boşluk
        
        # Test başlık alanı
        title_container = QWidget()
        title_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(3)
        
        self.title_label = QLabel("Test Başlığı:")
        self.title_label.setStyleSheet("font-weight: bold;")
        self.title_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        title_layout.addWidget(self.title_label)
        
        self.title_input = QLineEdit("Yeni Test")
        self.title_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.title_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 3px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
            }
        """)
        title_layout.addWidget(self.title_input)
        
        settings_layout.addWidget(title_container, 3)  # Başlık alanına daha fazla genişlik
        
        # Yanlış doğruyu götürme oranı ayarı
        ratio_container = QWidget()
        ratio_container.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        ratio_layout = QHBoxLayout(ratio_container)
        ratio_layout.setContentsMargins(0, 0, 0, 0)
        ratio_layout.setSpacing(3)
        
        self.ratio_label = QLabel("Kaç yanlış bir doğruyu götürür:")
        self.ratio_label.setStyleSheet("font-weight: bold;")
        ratio_layout.addWidget(self.ratio_label)
        
        self.ratio_combo = QComboBox()
        self.ratio_combo.addItems(["2", "3", "4", "5"])
        self.ratio_combo.setCurrentIndex(2)  # Default: 4
        self.ratio_combo.currentIndexChanged.connect(self.update_wrong_ratio)
        self.ratio_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 3px;
                background-color: #f8f9fa;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #ddd;
                border-left-style: solid;
            }
        """)
        ratio_layout.addWidget(self.ratio_combo)
        
        settings_layout.addWidget(ratio_container, 2)
        
        self.main_layout.addWidget(settings_frame)
        
        # Test Soruları Bölümü
        questions_frame = QFrame()
        questions_frame.setFrameShape(QFrame.StyledPanel)
        questions_frame.setStyleSheet("background-color: white; border-radius: 8px;")
        questions_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        questions_layout = QVBoxLayout(questions_frame)
        questions_layout.setContentsMargins(5, 5, 5, 5)  # Daha az iç boşluk
        questions_layout.setSpacing(5)
        
        # Sorular için bir scroll alanı
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.questions_widget = QWidget()
        self.questions_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.questions_layout = QVBoxLayout(self.questions_widget)
        self.questions_layout.setContentsMargins(3, 3, 3, 3)  # Daha az iç boşluk
        self.questions_layout.setSpacing(5)  # Sorular arası mesafeyi azalt
        
        # Create questions
        for i in range(1, 21):
            question = Question(i)
            question.test_tab = self  # Test tab referansını soruya ver
            self.questions.append(question)
            self.questions_layout.addWidget(question)
            
            # Add a separator line except for the last question
            if i < 20:
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setFrameShadow(QFrame.Sunken)
                line.setStyleSheet("color: #e0e0e0; max-height: 1px;")  # İnce çizgi
                self.questions_layout.addWidget(line)
        
        self.scroll_area.setWidget(self.questions_widget)
        questions_layout.addWidget(self.scroll_area)
        
        self.main_layout.addWidget(questions_frame)
        
        # Kontrol butonları ve sonuç etiketi
        controls_frame = QFrame()
        controls_frame.setFrameShape(QFrame.StyledPanel)
        controls_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 5px;")
        controls_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(5, 5, 5, 5)  # Daha az iç boşluk
        
        buttons_container = QWidget()
        buttons_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(5)  # Butonlar arası boşluğu azalttık
        
        # Sınavı Bitir Butonu
        self.finish_button = QPushButton("Sınavı Bitir")
        self.finish_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.finish_button.setMinimumWidth(80)
        self.finish_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:pressed {
                background-color: #2E7D32;
            }
        """)
        self.finish_button.clicked.connect(self.finish_test)
        buttons_layout.addWidget(self.finish_button)
        
        # Sınavı Kaydet Butonu
        self.save_button = QPushButton("Sınavı Kaydet")
        self.save_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.save_button.setMinimumWidth(80)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #B0BEC5;
                color: #ECEFF1;
            }
        """)
        self.save_button.clicked.connect(self.save_test)
        self.save_button.setEnabled(False)  # Başlangıçta devre dışı
        buttons_layout.addWidget(self.save_button)
        
        # Testi Temizle Butonu
        self.clear_button = QPushButton("Testi Temizle")
        self.clear_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.clear_button.setMinimumWidth(80)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
            QPushButton:pressed {
                background-color: #616161;
            }
        """)
        self.clear_button.clicked.connect(self.clear_test)
        buttons_layout.addWidget(self.clear_button)
        
        # Yeni Test Butonu
        self.new_test_button = QPushButton("Yeni Test")
        self.new_test_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.new_test_button.setMinimumWidth(80)
        self.new_test_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """)
        self.new_test_button.clicked.connect(self.reset_test)
        buttons_layout.addWidget(self.new_test_button)
        
        controls_layout.addWidget(buttons_container)
        
        # Sonuç etiketi
        self.result_label = QLabel("")
        self.result_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.result_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        controls_layout.addWidget(self.result_label)
        
        controls_layout.setStretch(0, 1)
        controls_layout.setStretch(1, 1)
        
        self.main_layout.addWidget(controls_frame)
        
        # Ana layout için stretch faktörleri
        self.main_layout.setStretch(0, 1)  # Settings
        self.main_layout.setStretch(1, 8)  # Questions
        self.main_layout.setStretch(2, 1)  # Controls
    
    def update_wrong_ratio(self, index):
        self.wrong_ratio = int(self.ratio_combo.currentText())
        self.calculate_and_show_results()
    
    def finish_test(self):
        if not self.is_test_completed:
            # Lock questions and show correct answers
            for question in self.questions:
                question.lock_options()
            
            self.is_test_completed = True
            self.finish_button.setEnabled(False)
            
            # Artık sonuçları hesapla ve göster
            self.calculate_and_show_results()
            
            # Kaydet butonu aktif
            self.save_button.setEnabled(True)
    
    def save_test(self):
        if not self.is_test_completed:
            return
            
        # Calculate score
        total_questions = 20
        correct_count = sum(1 for q in self.questions if q.state == "correct")
        wrong_count = sum(1 for q in self.questions if q.state == "wrong")
        empty_count = sum(1 for q in self.questions if q.state == "empty" or (not q.selected_option and q.state == "unmarked"))
        
        score = ((correct_count - (wrong_count / self.wrong_ratio)) / total_questions) * 100
        score = max(0, score)  # Prevent negative scores
        
        # Save the test results
        self.save_test_results(score, correct_count, wrong_count, empty_count)
        
        # Test kaydedildi olarak işaretle
        self.test_saved = True
        self.save_button.setEnabled(False)
        self.save_button.setText("Kaydedildi ✓")
        
        QMessageBox.information(self, "Sınav Kaydedildi", "Sınav sonuçlarınız başarıyla kaydedildi.", QMessageBox.Ok)
    
    def reset_test(self):
        # Yeni test için sıfırla
        for question in self.questions:
            question.reset()
        
        self.is_test_completed = False
        self.test_saved = False
        self.finish_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.save_button.setText("Sınavı Kaydet")
        self.result_label.setText("")
        
    def calculate_and_show_results(self):
        """Sonuçları hesapla ve göster"""
        if not self.is_test_completed:
            return
            
        # Calculate score
        total_questions = 20
        correct_count = sum(1 for q in self.questions if q.state == "correct")
        wrong_count = sum(1 for q in self.questions if q.state == "wrong")
        empty_count = sum(1 for q in self.questions if q.state == "empty" or (not q.selected_option and q.state == "unmarked"))
        
        score = ((correct_count - (wrong_count / self.wrong_ratio)) / total_questions) * 100
        score = max(0, score)  # Prevent negative scores
        
        result_text = f"Puan: {score:.1f}/100 | Doğru: {correct_count} | Yanlış: {wrong_count} | Boş: {empty_count}"
        self.result_label.setText(result_text)
    
    def save_test_results(self, score, correct, wrong, empty):
        # Test sorularının durumlarını kaydet
        questions_data = []
        for i, question in enumerate(self.questions):
            question_data = {
                "number": i + 1,
                "selected_option": question.selected_option,
                "state": question.state,
                "is_correct": question.is_correct,
                "was_empty": question.was_empty
            }
            questions_data.append(question_data)
            
        test_data = {
            "title": self.title_input.text(),
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "score": score,
            "correct": correct,
            "wrong": wrong,
            "empty": empty,
            "wrong_ratio": self.wrong_ratio,
            "questions": questions_data
        }
        
        # Ensure data directory exists
        if not os.path.exists("test_results"):
            os.makedirs("test_results")
        
        # Save to file
        filename = f"test_results/{self.title_input.text()}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(test_data, f)

    def clear_test(self):
        """Testi temizler (yalnızca işaretlemeleri sıfırlar)"""
        reply = QMessageBox.question(
            self, 'Testi Temizle',
            'Tüm işaretlemeleri temizlemek istediğinizden emin misiniz?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Tüm soruları sıfırla ama test ayarlarını koru
            for question in self.questions:
                question.reset()
                
            # Eğer test bitmişse, bitir durumunu koru ama sıfırla
            if self.is_test_completed:
                for question in self.questions:
                    question.is_locked = True
                    
            # Sonuç etiketini güncelle
            self.calculate_and_show_results()
            
            # Kaydet butonunu devre dışı bırak
            self.save_button.setEnabled(False)
            self.test_saved = False
            
            QMessageBox.information(self, "Başarılı", "Test temizlendi.", QMessageBox.Ok)

class HistoryTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(3, 3, 3, 3)
        self.main_layout.setSpacing(5)
        self.setLayout(self.main_layout)
        
        # Table for showing test history
        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setColumnCount(4)  # 5'den 4'e düşürüldü (Oran sütunu silindi)
        self.table.setHorizontalHeaderLabels(['Test Adı', 'Puan', 'D/Y/B', 'Tarih'])  # Yeni sıralama
        
        # Sütunların manuel olarak boyutlandırılabilmesi için:
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        # İlk başta uygun genişlikler ayarla
        self.table.setColumnWidth(0, 150)  # Test Adı - daha geniş
        self.table.setColumnWidth(1, 50)   # Puan 
        self.table.setColumnWidth(2, 70)   # D/Y/B
        self.table.setColumnWidth(3, 90)   # Tarih
        
        # Son sütunun geri kalan alanı doldurmasını sağla
        self.table.horizontalHeader().setStretchLastSection(True)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 11px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 3px;
                border: 1px solid #ddd;
                font-weight: bold;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 2px;
            }
            QTableWidget::item:selected {
                background-color: #e0f2f1;
            }
        """)
        self.main_layout.addWidget(self.table)
        
        # Çift tıklamayı bağla
        self.table.itemDoubleClicked.connect(self.open_test_details)
        
        # Butonlar
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(3)
        
        # Yenile butonu
        self.refresh_button = QPushButton("Yenile")
        self.refresh_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 3px 5px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.refresh_button.clicked.connect(self.load_history)
        buttons_layout.addWidget(self.refresh_button)
        
        # Detay Göster butonu
        self.show_details_button = QPushButton("Detayları Göster")
        self.show_details_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.show_details_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 3px 5px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.show_details_button.clicked.connect(self.show_selected_test_details)
        buttons_layout.addWidget(self.show_details_button)
        
        # Sil butonu
        self.delete_button = QPushButton("Seçili Testi Sil")
        self.delete_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 3px 5px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.delete_button.clicked.connect(self.delete_selected_test)
        buttons_layout.addWidget(self.delete_button)
        
        # Tüm Kayıtları Sil butonu
        self.delete_all_button = QPushButton("Tüm Test Geçmişini Sil")
        self.delete_all_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.delete_all_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 3px 5px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        self.delete_all_button.clicked.connect(self.delete_all_tests)
        buttons_layout.addWidget(self.delete_all_button)
        
        self.main_layout.addLayout(buttons_layout)
        
        # Load history data
        self.load_history()
        
        # Test dosya adlarını sakla
        self.test_files = []
    
    def load_history(self):
        # Clear existing data
        self.table.setRowCount(0)
        
        # Check if test_results directory exists
        if not os.path.exists("test_results"):
            return
        
        # Load all test results
        self.test_files = glob.glob("test_results/*.json")
        
        # Sort by date (newest first)
        self.test_files.sort(key=os.path.getmtime, reverse=True)
        
        row = 0
        for file_path in self.test_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                self.table.insertRow(row)
                
                # Test adı
                self.table.setItem(row, 0, QTableWidgetItem(data.get('title', 'Bilinmeyen')))
                
                # Puan
                score_item = QTableWidgetItem(f"{data.get('score', 0):.1f}")
                self.table.setItem(row, 1, score_item)
                
                # D/Y/B (Doğru/Yanlış/Boş)
                correct = data.get('correct', 0)
                wrong = data.get('wrong', 0)
                empty = data.get('empty', 0)
                dyb_item = QTableWidgetItem(f"{correct}/{wrong}/{empty}")
                self.table.setItem(row, 2, dyb_item)
                
                # Tarih
                self.table.setItem(row, 3, QTableWidgetItem(data.get('date', '-')))
                
                # Color based on score
                score = data.get('score', 0)
                if score >= 85:
                    score_item.setBackground(QColor(200, 255, 200))  # Light green
                elif score >= 70:
                    score_item.setBackground(QColor(220, 255, 220))  # Lighter green
                elif score >= 60:
                    score_item.setBackground(QColor(255, 255, 200))  # Light yellow
                elif score >= 50:
                    score_item.setBackground(QColor(255, 230, 200))  # Light orange
                else:
                    score_item.setBackground(QColor(255, 200, 200))  # Light red
                
                row += 1
            except Exception as e:
                print(f"Error loading test result {file_path}: {e}")
    
    def delete_selected_test(self):
        current_row = self.table.currentRow()
        if current_row >= 0 and current_row < len(self.test_files):
            file_path = self.test_files[current_row]
            
            reply = QMessageBox.question(
                self, 'Testi Sil',
                'Seçili testi silmek istediğinize emin misiniz?',
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    os.remove(file_path)
                    self.load_history()  # Yeniden yükle
                    QMessageBox.information(self, "Başarılı", "Test başarıyla silindi.", QMessageBox.Ok)
                except Exception as e:
                    QMessageBox.warning(self, "Hata", f"Test silinirken hata oluştu: {e}", QMessageBox.Ok)
    
    def delete_all_tests(self):
        # Test dosyalarını yeniden yükle - en güncel listeyi almak için
        if not os.path.exists("test_results"):
            QMessageBox.information(self, "Bilgi", "Silinecek test kaydı bulunmamaktadır.", QMessageBox.Ok)
            return
            
        # Yeniden dosyaları oku
        self.test_files = glob.glob("test_results/*.json")
        
        if len(self.test_files) == 0:
            QMessageBox.information(self, "Bilgi", "Silinecek test kaydı bulunmamaktadır.", QMessageBox.Ok)
            return
            
        reply = QMessageBox.question(
            self, 'Tüm Test Geçmişini Sil',
            'TÜM test kayıtlarını silmek istediğinize emin misiniz? Bu işlem geri alınamaz!',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            confirm_reply = QMessageBox.warning(
                self, 'Son Uyarı',
                'Bu işlem TÜM test kayıtlarınızı KALICI olarak silecektir. Devam etmek istiyor musunuz?',
                QMessageBox.Yes | QMessageBox.No
            )
            
            if confirm_reply == QMessageBox.Yes:
                error_count = 0
                try:
                    for file_path in self.test_files:
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            print(f"Dosya silinirken hata: {file_path}, {str(e)}")
                            error_count += 1
                            
                    self.load_history()  # Yeniden yükle
                    
                    if error_count > 0:
                        QMessageBox.warning(self, "Kısmi Başarı", f"{len(self.test_files) - error_count} test kaydı silindi, {error_count} kayıt silinemedi.", QMessageBox.Ok)
                    else:
                        QMessageBox.information(self, "Başarılı", "Tüm test kayıtları başarıyla silindi.", QMessageBox.Ok)
                except Exception as e:
                    QMessageBox.warning(self, "Hata", f"Testler silinirken bir hata oluştu: {e}", QMessageBox.Ok)

    def show_selected_test_details(self):
        """Seçili testin detaylarını göster"""
        current_row = self.table.currentRow()
        if current_row >= 0 and current_row < len(self.test_files):
            self.open_test_details(self.table.item(current_row, 0))
    
    def open_test_details(self, item):
        """Test detaylarını göster"""
        row = item.row() if hasattr(item, 'row') else self.table.currentRow()
        if row >= 0 and row < len(self.test_files):
            file_path = self.test_files[row]
            
            try:
                with open(file_path, 'r') as f:
                    test_data = json.load(f)
                
                # Test detaylarını göster
                test_window = TestDetailWindow(test_data, self)
                test_window.show()
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Test detayları yüklenirken bir sorun oluştu: {e}", QMessageBox.Ok)

# Test Detay Penceresi
class TestDetailWindow(QMainWindow):
    def __init__(self, test_data, parent=None):
        super().__init__(parent)
        self.test_data = test_data
        
        # Pencere özellikleri
        self.setWindowTitle(f"Test Detayları: {test_data['title']}")
        self.setMinimumSize(800, 600)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Üst bilgi alanı
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 10px;")
        info_layout = QGridLayout(info_frame)
        
        # Bilgi etiketleri
        title_label = QLabel(f"<b>Test Adı:</b> {test_data['title']}")
        date_label = QLabel(f"<b>Tarih:</b> {test_data['date']}")
        score_label = QLabel(f"<b>Puan:</b> {test_data['score']:.1f}/100")
        
        # Puanı renklendir
        score_value = test_data['score']
        if score_value >= 85:
            score_label.setStyleSheet("color: #2E7D32;")  # Koyu yeşil
        elif score_value >= 70:
            score_label.setStyleSheet("color: #388E3C;")  # Yeşil
        elif score_value >= 60:
            score_label.setStyleSheet("color: #FBC02D;")  # Sarı
        elif score_value >= 50:
            score_label.setStyleSheet("color: #F57F17;")  # Turuncu
        else:
            score_label.setStyleSheet("color: #C62828;")  # Kırmızı
            
        correct_label = QLabel(f"<b>Doğru:</b> {test_data['correct']}")
        correct_label.setStyleSheet("color: #4CAF50;")
        
        wrong_label = QLabel(f"<b>Yanlış:</b> {test_data['wrong']}")
        wrong_label.setStyleSheet("color: #F44336;")
        
        empty_label = QLabel(f"<b>Boş:</b> {test_data['empty']}")
        empty_label.setStyleSheet("color: #2196F3;")
        
        ratio_label = QLabel(f"<b>Yanlış Götürme Oranı:</b> {test_data['wrong_ratio']}")
        
        # Düzene ekle
        info_layout.addWidget(title_label, 0, 0)
        info_layout.addWidget(date_label, 0, 1)
        info_layout.addWidget(score_label, 1, 0)
        info_layout.addWidget(correct_label, 1, 1)
        info_layout.addWidget(wrong_label, 2, 0)
        info_layout.addWidget(empty_label, 2, 1)
        info_layout.addWidget(ratio_label, 3, 0, 1, 2)
        
        main_layout.addWidget(info_frame)
        
        # Soru detayları tablosu
        question_frame = QFrame()
        question_frame.setFrameShape(QFrame.StyledPanel)
        question_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 10px;")
        question_layout = QVBoxLayout(question_frame)
        
        # Tablo başlığı
        table_title = QLabel("<b>Soru Detayları</b>")
        table_title.setAlignment(Qt.AlignCenter)
        question_layout.addWidget(table_title)
        
        # Soru detayları tablosu
        self.question_table = QTableWidget()
        self.question_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.question_table.setColumnCount(4)
        self.question_table.setHorizontalHeaderLabels(['Soru No', 'Seçilen Şık', 'Durum', 'Açıklama'])
        
        # Sütunların manuel olarak boyutlandırılabilmesi için:
        self.question_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        # İlk başta uygun genişlikler ayarla
        self.question_table.setColumnWidth(0, 60)    # Soru No
        self.question_table.setColumnWidth(1, 80)    # Seçilen Şık
        self.question_table.setColumnWidth(2, 80)    # Durum
        
        # Son sütunun geri kalan alanı doldurmasını sağla
        self.question_table.horizontalHeader().setStretchLastSection(True)
        
        self.question_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #ddd;
                font-weight: bold;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #e0f2f1;
            }
        """)
        
        # Sorular varsa yükle
        if 'questions' in test_data:
            self.load_questions_data(test_data['questions'])
        else:
            # Eski formatta kaydedilmiş testler için
            no_data_row = self.question_table.rowCount()
            self.question_table.insertRow(no_data_row)
            self.question_table.setItem(no_data_row, 0, QTableWidgetItem("--"))
            self.question_table.setItem(no_data_row, 1, QTableWidgetItem("--"))
            self.question_table.setItem(no_data_row, 2, QTableWidgetItem("--"))
            self.question_table.setItem(no_data_row, 3, QTableWidgetItem("Bu test için soru detayları mevcut değil"))
        
        question_layout.addWidget(self.question_table)
        main_layout.addWidget(question_frame)
        
        # Grafik gösterimi için bir resim ekleyebiliriz
        chart_frame = QFrame()
        chart_frame.setFrameShape(QFrame.StyledPanel)
        chart_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 10px;")
        chart_layout = QVBoxLayout(chart_frame)
        
        # Grafik başlığı
        chart_title = QLabel("<b>Test Sonuç Grafiği</b>")
        chart_title.setAlignment(Qt.AlignCenter)
        chart_layout.addWidget(chart_title)
        
        # Sonuç grafiği (basit bir görsel temsil)
        chart_widget = QWidget()
        chart_widget.setMinimumHeight(150)
        chart_layout.addWidget(chart_widget)
        
        # Grafik çizimi
        chart_widget.paintEvent = lambda event, d=test_data: self.draw_chart(event, d, chart_widget)
        
        main_layout.addWidget(chart_frame)
        
        # Layout ağırlıkları
        main_layout.setStretch(0, 1)  # Bilgi alanı
        main_layout.setStretch(1, 3)  # Soru detayları
        main_layout.setStretch(2, 2)  # Grafik
        
        # Kapat butonu
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Kapat")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        close_btn.clicked.connect(self.close)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        
        main_layout.addLayout(btn_layout)
    
    def load_questions_data(self, questions_data):
        """Soru verilerini tabloya yükle"""
        self.question_table.setRowCount(0)
        
        for question in questions_data:
            row = self.question_table.rowCount()
            self.question_table.insertRow(row)
            
            # Soru numarası
            self.question_table.setItem(row, 0, QTableWidgetItem(str(question['number'])))
            
            # Seçilen şık
            selected_option = question.get('selected_option', '-')
            self.question_table.setItem(row, 1, QTableWidgetItem(str(selected_option) if selected_option else '-'))
            
            # Durum
            state = question.get('state', 'unmarked')
            state_item = QTableWidgetItem(self.get_state_text(state))
            self.question_table.setItem(row, 2, state_item)
            
            # Durum rengini ayarla
            if state == 'correct':
                state_item.setBackground(QColor(200, 255, 200))  # Açık yeşil
                state_item.setForeground(QColor(0, 100, 0))      # Koyu yeşil yazı
            elif state == 'wrong':
                state_item.setBackground(QColor(255, 200, 200))  # Açık kırmızı
                state_item.setForeground(QColor(150, 0, 0))      # Koyu kırmızı yazı
            elif state == 'empty':
                state_item.setBackground(QColor(200, 220, 255))  # Açık mavi
                state_item.setForeground(QColor(0, 0, 150))      # Koyu mavi yazı
            
            # Açıklama
            description = self.get_question_description(question)
            self.question_table.setItem(row, 3, QTableWidgetItem(description))
    
    def get_state_text(self, state):
        """Durum metnini döndür"""
        if state == 'correct':
            return 'Doğru'
        elif state == 'wrong':
            return 'Yanlış'
        elif state == 'empty':
            return 'Boş'
        else:
            return 'İşaretlenmemiş'
    
    def get_question_description(self, question):
        """Soru durumuna göre açıklama oluştur"""
        state = question.get('state', 'unmarked')
        selected = question.get('selected_option', None)
        
        if state == 'correct':
            return f"{selected} işaretlendi - Doğru"
        elif state == 'wrong':
            return f"{selected} işaretlendi - Yanlış"
        elif state == 'empty':
            if selected:
                return f"{selected} işaretlendi - Boş bırakıldı olarak değerlendirildi"
            else:
                return "Boş bırakıldı"
        else:
            if selected:
                return f"{selected} işaretlendi - Değerlendirilmedi"
            else:
                return "İşaretlenmedi"
    
    def draw_chart(self, event, data, widget):
        """Basit sonuç grafiği çizimi"""
        painter = QPainter(widget)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Grafik alanı
        width = widget.width()
        height = widget.height()
        margin = 20
        
        # Renkleri tanımla
        colors = {
            'correct': QColor('#4CAF50'),
            'wrong': QColor('#F44336'),
            'empty': QColor('#2196F3')
        }
        
        # Toplam soru sayısı
        total = data['correct'] + data['wrong'] + data['empty']
        if total == 0:
            return
        
        # Çubuk grafik çiz
        bar_width = int((width - 2 * margin) / 3)
        bar_spacing = 10
        
        # Doğrular
        correct_height = int((data['correct'] / total) * (height - 2 * margin))
        x = margin
        y = int(height - margin - correct_height)
        painter.setBrush(colors['correct'])
        painter.setPen(Qt.NoPen)
        painter.drawRect(x, y, bar_width - bar_spacing, correct_height)
        painter.setPen(Qt.black)
        painter.drawText(QRect(x, height - margin + 5, bar_width - bar_spacing, 20), 
                         Qt.AlignCenter, f"Doğru ({data['correct']})")
        
        # Yanlışlar
        wrong_height = int((data['wrong'] / total) * (height - 2 * margin))
        x = margin + bar_width
        y = int(height - margin - wrong_height)
        painter.setBrush(colors['wrong'])
        painter.setPen(Qt.NoPen)
        painter.drawRect(x, y, bar_width - bar_spacing, wrong_height)
        painter.setPen(Qt.black)
        painter.drawText(QRect(x, height - margin + 5, bar_width - bar_spacing, 20), 
                         Qt.AlignCenter, f"Yanlış ({data['wrong']})")
        
        # Boşlar
        empty_height = int((data['empty'] / total) * (height - 2 * margin))
        x = margin + 2 * bar_width
        y = int(height - margin - empty_height)
        painter.setBrush(colors['empty'])
        painter.setPen(Qt.NoPen)
        painter.drawRect(x, y, bar_width - bar_spacing, empty_height)
        painter.setPen(Qt.black)
        painter.drawText(QRect(x, height - margin + 5, bar_width - bar_spacing, 20), 
                         Qt.AlignCenter, f"Boş ({data['empty']})")

class OptikFormApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kaplan Optik Form Uygulaması")
        self.setMinimumSize(800, 600)  # Minimum boyutu küçülttüm
        
        # İkon ayarla (eğer dosya varsa)
        icon_path = ""
        if os.path.exists("kaplanlogo_icon.png"):
            icon_path = "kaplanlogo_icon.png"
        elif os.path.exists("kaplan_optik_logo_icon.png"):
            icon_path = "kaplan_optik_logo_icon.png"
        
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        else:
            print("İkon dosyası bulunamadı")
        
        # Central Widget and Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)  # Daha az kenar boşluğu
        main_layout.setSpacing(5)
        
        # Test Paneli ve Geçmiş Paneli arasında ayarlanabilir bir ayırıcı (splitter) ekleyelim
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # Test Paneli (Sol Taraf)
        test_panel = QWidget()
        test_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        test_layout = QVBoxLayout(test_panel)
        test_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header Container
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Logo'yu kaldırdık, sadece başlık gösteriliyor
        # Test paneli başlığı
        test_header = QLabel("Kaplan Optik")
        test_header.setAlignment(Qt.AlignCenter)
        test_header.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333;
            padding: 10px;
        """)
        header_layout.addWidget(test_header)
        
        # Header'ı test paneline ekle
        test_layout.addWidget(header_container)
        
        # Ana test alanı
        self.test_tab = TestTab()
        test_layout.addWidget(self.test_tab)
        
        # Sol panel ana düzene ekleniyor (artık main_layout değil, splitter'a ekliyoruz)
        self.main_splitter.addWidget(test_panel)
        
        # Geçmiş Paneli (Sağ Taraf)
        history_panel = QWidget()
        history_layout = QVBoxLayout(history_panel)
        history_layout.setContentsMargins(0, 0, 0, 0)
        
        # Geçmiş paneli başlığı
        history_header = QLabel("Test Geçmişi")
        history_header.setAlignment(Qt.AlignCenter)
        history_header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333;
            padding: 10px;
            background-color: #f5f5f5;
            border-radius: 8px;
        """)
        history_layout.addWidget(history_header)
        
        # Geçmiş tablosu
        self.history_tab = HistoryTab()
        history_layout.addWidget(self.history_tab)
        
        # Sağ panel ana düzene ekleniyor (artık main_layout değil, splitter'a ekliyoruz)
        self.main_splitter.addWidget(history_panel)
        
        # Splitter'ın başlangıç boyutlarını ayarla (70-30 oranı)
        self.main_splitter.setSizes([int(self.width() * 0.7), int(self.width() * 0.3)])
    
    def closeEvent(self, event):
        # Eğer test tamamlandı ama kaydedilmediyse uyarı göster
        if hasattr(self, 'test_tab') and self.test_tab.is_test_completed and not self.test_tab.test_saved:
            reply = QMessageBox.question(
                self, 'Sınav Kaydedilmedi',
                'Tamamlanmış sınavınız henüz kaydedilmedi. Çıkmadan önce kaydetmek ister misiniz?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Yes:
                self.test_tab.save_test()
                event.accept()
            elif reply == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Uygulama ikonu doğru şekilde ayarlanıyor - QApplication için
    icon_path = ""
    if os.path.exists("kaplanlogo_icon.png"):
        icon_path = "kaplanlogo_icon.png"
    elif os.path.exists("kaplan_optik_logo_icon.png"):
        icon_path = "kaplan_optik_logo_icon.png"
    
    if icon_path:
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    else:
        print("İkon dosyası bulunamadı")
    
    window = OptikFormApp()
    window.show()
    sys.exit(app.exec_()) 