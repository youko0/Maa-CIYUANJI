from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, 
    QTextEdit, QLabel
)


class NovelTabWidget(QWidget):
    """小说Tab控件"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 上部分：小说信息和进度
        info_group = QGroupBox("小说识别信息")
        info_layout = QVBoxLayout()
        
        # 当前小说信息
        self.current_novel_label = QLabel("当前小说: 无")
        self.progress_label = QLabel("进度: 0/0")
        info_layout.addWidget(self.current_novel_label)
        info_layout.addWidget(self.progress_label)
        
        # 进度条（简化为标签）
        self.progress_info = QTextEdit()
        self.progress_info.setReadOnly(True)
        self.progress_info.setMaximumHeight(100)
        info_layout.addWidget(QLabel("识别进度:"))
        info_layout.addWidget(self.progress_info)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 下部分：识别日志
        log_group = QGroupBox("识别日志")
        log_layout = QVBoxLayout()
        
        self.novel_log = QTextEdit()
        self.novel_log.setReadOnly(True)
        log_layout.addWidget(self.novel_log)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # 操作按钮
        novel_tab_btn_layout = QHBoxLayout()
        self.stop_novel_btn = QPushButton("停止识别")
        self.stop_novel_btn.clicked.connect(self.main_window.stop_novel_recognition)
        self.stop_novel_btn.setEnabled(False)
        self.export_novel_btn = QPushButton("导出小说")
        self.export_novel_btn.clicked.connect(self.main_window.export_current_novel)
        
        novel_tab_btn_layout.addWidget(self.stop_novel_btn)
        novel_tab_btn_layout.addWidget(self.export_novel_btn)
        layout.addLayout(novel_tab_btn_layout)