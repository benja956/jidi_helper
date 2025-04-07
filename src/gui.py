from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QFrame, QApplication, QPushButton)
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QColor, QPalette
import win32gui
import win32con
from .data_manager import DataManager
from .lcu import LCUClient

class RestartButton(QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(200-12)
        self.setup_ui()
        self.setup_style()
        self.lcu_client = LCUClient()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 10, 25)  # 左侧边距增加到25px
        layout.setSpacing(10)
        
        # 创建重启按钮
        restart_btn = QPushButton("重启客户端")
        restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restart_btn.clicked.connect(self.restart_client)
        layout.addWidget(restart_btn)
        
    def setup_style(self):
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 180);
                border: none;
            }
            QPushButton {
                background-color: rgba(30, 30, 30, 180);
                color: white;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(60, 60, 60, 180);
                border: 1px solid #888888;
            }
            QPushButton:pressed {
                background-color: rgba(70, 70, 70, 180);
                border: 1px solid #aaaaaa;
            }
        """)
        
    def restart_client(self):
        try:
            self.lcu_client.get_client_key()
            self.lcu_client.restart_client()
        except Exception as e:
            print(f"重启客户端失败: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |  # 无边框
            Qt.WindowType.WindowStaysOnTopHint |  # 置顶
            Qt.WindowType.Tool  # 不在任务栏显示
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 透明背景
        
        # 初始化游戏窗口跟踪
        self.game_hwnd = None
        self.find_game_window()
        
        # 设置定时器检测游戏窗口位置
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_window_position)
        self.update_timer.start(100)  # 每100ms检查一次
        
        # 先创建UI
        self.setup_ui()
        
        # 初始化数据管理器
        self.data_manager = DataManager()
        if not self.data_manager.init_data():
            print("初始化数据失败")
        
        # 设置数据更新定时器
        self.data_update_timer = QTimer(self)
        self.data_update_timer.timeout.connect(self.data_manager.update_game_data)
        self.data_update_timer.start(2000)  # 每2秒更新一次数据
        
        # 连接信号
        self.data_manager.summoner_data_updated.connect(self.summoner_panel.update_summoner)
        self.data_manager.champion_data_updated.connect(self.champion_panel.update_champions)
        
    def find_game_window(self):
        """查找英雄联盟客户端窗口"""
        def callback(hwnd, extra):
            if win32gui.GetWindowText(hwnd) == "League of Legends":
                self.game_hwnd = hwnd
                return False
            return True
        
        win32gui.EnumWindows(callback, None)
        if not self.game_hwnd:
            print("未找到游戏窗口")
            
    def update_window_position(self):
        """更新窗口位置"""
        if not self.game_hwnd:
            self.find_game_window()
            return
            
        try:
            # 获取游戏窗口位置
            rect = win32gui.GetWindowRect(self.game_hwnd)
            game_x, game_y = rect[0], rect[1]
            game_w, game_h = rect[2] - rect[0], rect[3] - rect[1]
            
            # 检查窗口是否最小化
            if win32gui.IsIconic(self.game_hwnd):
                self.hide()
                return
                
            # 检查窗口是否可见
            if not win32gui.IsWindowVisible(self.game_hwnd):
                self.hide()
                return
                
            # 设置主窗口位置（包含整个区域）
            self.setGeometry(
                game_x - 200,  # 向左扩展200px
                game_y - 200,  # 向上扩展200px
                game_w + 200,  # 增加左侧面板宽度
                game_h + 200   # 增加上方面板高度
            )
            
            # 设置左侧面板位置
            self.summoner_panel.setGeometry(
                0,  # 相对于主窗口的左边缘
                200,  # 从上方面板下方开始
                200,  # 宽度
                game_h  # 与游戏窗口等高
            )
            
            # 设置上方面板位置
            self.champion_panel.setGeometry(
                200 - 280,  # 从左侧面板右侧开始，再向左偏移280px
                0,  # 相对于主窗口的上边缘
                game_w,  # 与游戏窗口等宽
                200  # 高度
            )
            
            self.show()
            
        except Exception as e:
            print(f"更新窗口位置失败: {str(e)}")
            self.game_hwnd = None

    def setup_ui(self):
        """设置UI布局"""
        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建水平布局
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 添加左侧面板
        self.summoner_panel = SummonerPanel()
        layout.addWidget(self.summoner_panel)
        
        # 添加右侧容器（包含上方面板）
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # 添加上方面板
        self.champion_panel = ChampionPanel()
        right_layout.addWidget(self.champion_panel)
        
        # 添加占位符（填充剩余空间）
        spacer = QWidget()
        spacer.setFixedSize(1080, 520)  # 1280 - 200 = 1080 (宽度), 720 - 200 = 520 (高度)
        spacer.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)  # 鼠标事件穿透
        right_layout.addWidget(spacer)
        
        layout.addWidget(right_container)

class SummonerPanel(QFrame):
    """左侧召唤师信息面板"""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(200)
        self.setFixedHeight(720)
        self.summoner_labels = []  # [(name_label, aram_label, win_rate_label, kda_label, champion_label), ...]
        self.setup_ui()
        self.setup_style()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        for i in range(5):
            # 创建水平布局容器
            row_container = QFrame()
            row_layout = QHBoxLayout(row_container)
            row_layout.setContentsMargins(5, 5, 5, 5)
            row_layout.setSpacing(5)
            
            # 左侧召唤师信息
            summoner_box = QFrame()
            summoner_layout = QVBoxLayout(summoner_box)
            summoner_layout.setSpacing(2)
            
            name_label = QLabel("等待数据...")
            aram_label = QLabel("含量: --")
            win_rate_label = QLabel("胜率: --")
            kda_label = QLabel("KDA: --")
            
            summoner_layout.addWidget(name_label)
            summoner_layout.addWidget(aram_label)
            summoner_layout.addWidget(win_rate_label)
            summoner_layout.addWidget(kda_label)
            
            # 右侧英雄信息
            champion_box = QFrame()
            champion_layout = QVBoxLayout(champion_box)
            champion_layout.setSpacing(2)
            
            # 分开显示英雄信息的各个部分
            champion_name_label = QLabel("--")  # 英雄名称
            champion_rank_label = QLabel("--")  # 排名
            champion_winrate_label = QLabel("--")  # 胜率
            
            champion_layout.addWidget(champion_name_label)
            champion_layout.addWidget(champion_rank_label)
            champion_layout.addWidget(champion_winrate_label)
            
            # 将两个框添加到水平布局中
            row_layout.addWidget(summoner_box)
            row_layout.addWidget(champion_box)
            
            # 保存标签引用
            self.summoner_labels.append((
                name_label, aram_label, win_rate_label, 
                kda_label, (champion_name_label, champion_rank_label, champion_winrate_label)
            ))
            
            layout.addWidget(row_container)
            
        # 添加重启按钮面板
        self.restart_button = RestartButton()
        layout.addWidget(self.restart_button)
        
        layout.addStretch()
        
    def setup_style(self):
        self.setStyleSheet("""
            SummonerPanel {
                background-color: rgba(0, 0, 0, 180);
                border: none;
            }
            QFrame {
                background-color: rgba(30, 30, 30, 180);
                border-radius: 5px;
                color: white;
            }
            QLabel {
                color: white;
                background-color: transparent;
            }
        """)

    def update_summoner(self, index, name, aram_rate, win_rate, kda, champion_info):
        """更新召唤师信息"""
        if 0 <= index < len(self.summoner_labels):
            labels = self.summoner_labels[index]
            # 更新召唤师信息
            labels[0].setText(name)
            labels[1].setText(f"含量: {aram_rate}%")
            labels[2].setText(f"胜率: {win_rate}%")
            labels[3].setText(f"KDA: {kda}")
            
            # 更新英雄信息
            if champion_info != "未选择":
                # 解析英雄信息字符串
                # 格式: "{name} [{rank}] {win_rate}%"
                try:
                    name_end = champion_info.find(" [")
                    rank_start = champion_info.find("[") + 1
                    rank_end = champion_info.find("]")
                    
                    hero_name = champion_info[:name_end]
                    hero_rank = champion_info[rank_start:rank_end]
                    hero_winrate = champion_info[rank_end+2:-1]  # 去掉最后的%
                    
                    labels[4][0].setText(f"[{hero_name}]")
                    labels[4][1].setText(f"排名: {hero_rank}")
                    labels[4][2].setText(f"胜率: {hero_winrate}%")
                except:
                    # 如果解析失败，直接显示原始信息
                    labels[4][0].setText(champion_info)
                    labels[4][1].setText("")
                    labels[4][2].setText("")
            else:
                labels[4][0].setText("未选择")
                labels[4][1].setText("")
                labels[4][2].setText("")

class ChampionPanel(QFrame):
    """上方英雄选择面板"""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedHeight(200)
        self.setFixedWidth(1280)
        self.champion_boxes = []
        self.setup_ui()
        self.setup_style()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(210, 10, 10, 10)
        layout.setSpacing(10)
        
        # 添加12个英雄选择框
        for i in range(12):
            champion_box = QFrame()
            box_layout = QVBoxLayout(champion_box)
            box_layout.setContentsMargins(5, 5, 5, 5)  # 减小内边距
            box_layout.setSpacing(2)  # 减小标签之间的间距
            
            name_label = QLabel("等待数据...")
            win_rate_label = QLabel("胜率: --")
            rank_label = QLabel("排名: --")
            
            # 设置标签对齐方式
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            win_rate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            rank_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # 设置自动换行
            name_label.setWordWrap(True)
            
            self.champion_boxes.append((name_label, win_rate_label, rank_label))
            
            box_layout.addWidget(name_label)
            box_layout.addWidget(win_rate_label)
            box_layout.addWidget(rank_label)
            
            layout.addWidget(champion_box)
        
        layout.addStretch()
        
    def setup_style(self):
        self.setStyleSheet("""
            ChampionPanel {
                background-color: rgba(0, 0, 0, 180);
                border: none;
            }
            QFrame {
                background-color: rgba(30, 30, 30, 180);
                border-radius: 5px;
                color: white;
            }
            QLabel {
                color: white;
                background-color: transparent;
            }
        """)

    def update_champions(self, champions):
        """更新英雄信息"""
        # 先清空所有框的数据
        for labels in self.champion_boxes:
            labels[0].setText("")
            labels[1].setText("")
            labels[2].setText("")
        
        # 更新有数据的框
        for i, (champion_id, name, rank, win_rate) in enumerate(champions):
            if i < len(self.champion_boxes):
                labels = self.champion_boxes[i]
                labels[0].setText(name)
                labels[1].setText(f"胜率: {win_rate:.1f}%")
                labels[2].setText(f"排名: {rank}")

                # 获取标签所在的 QFrame
                champion_box = labels[0].parent()
                
                # 直接使用 rank 判断是否是优质选择
                if rank <= 30:
                    champion_box.setStyleSheet("""
                        QFrame {
                            background-color: rgba(30, 30, 30, 180);
                            border: 2px solid #FFD700;  /* 金色边框 */
                            border-radius: 5px;
                        }
                        QLabel {
                            color: white;
                            background: transparent;
                            border: none;  /* 移除标签的边框 */
                        }
                    """)
                else:
                    # 普通样式
                    champion_box.setStyleSheet("""
                        QFrame {
                            background-color: rgba(30, 30, 30, 180);
                            border: 1px solid #666666;
                            border-radius: 5px;
                        }
                        QLabel {
                            color: white;
                            background: transparent;
                            border: none;  /* 移除标签的边框 */
                        }
                    """) 