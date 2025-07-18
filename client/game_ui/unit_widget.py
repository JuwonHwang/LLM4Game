from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
from ..game_ui.util import unit_to_text, get_info, get_price
from ..baseWidget import BaseWidget
from PyQt6.QtCore import Qt

class UnitWidget(BaseWidget):
    def __init__(self, parent):
        super().__init__("client/game_ui/unit_styles.qss")
        self.parent = parent

        # 메인 레이아웃
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(5)  # 전체 여백 최소화
        self.main_layout.setContentsMargins(5, 5, 5, 5)

        # ----- [1] Unit Basic Information (Compact) -----
        self.name_label = QLabel()
        self.gold_label = QLabel()

        unit_info_layout = QHBoxLayout()  # 가로 정렬
        unit_info_layout.setSpacing(3)
        unit_info_layout.addWidget(self.name_label)
        unit_info_layout.addWidget(self.gold_label)

        # ----- [2] Traits (Synergy, Items) -----
        self.synergy_label = QLabel()
        self.item_label = QLabel()

        trait_layout = QHBoxLayout()  # 가로 정렬
        trait_layout.setSpacing(3)
        trait_layout.addWidget(self.synergy_label)
        trait_layout.addWidget(self.item_label)

        # ----- 상단 정보 (기본 정보 + 특성) 가로 배치 -----
        top_layout = QVBoxLayout()
        top_layout.addLayout(unit_info_layout)
        top_layout.addLayout(trait_layout)

        # ----- [3] Status Information (3개 열로 배치) -----
        self.hp_label = QLabel()
        self.mp_label = QLabel()
        self.attack_label = QLabel()
        self.defense_label = QLabel()
        self.attack_speed_label = QLabel()
        self.special_attack_label = QLabel()
        self.special_defense_label = QLabel()
        self.critical_rate_label = QLabel()
        self.critical_damage_label = QLabel()
        self.attack_range_label = QLabel()

        # 상태 정보를 3열로 정렬
        left_status_layout = QVBoxLayout()
        left_status_layout.setSpacing(3)
        left_status_layout.addWidget(self.hp_label)
        left_status_layout.addWidget(self.mp_label)
        left_status_layout.addWidget(self.attack_label)
        left_status_layout.addWidget(self.defense_label)

        middle_status_layout = QVBoxLayout()
        middle_status_layout.setSpacing(3)
        middle_status_layout.addWidget(self.attack_speed_label)
        middle_status_layout.addWidget(self.special_attack_label)
        middle_status_layout.addWidget(self.special_defense_label)

        right_status_layout = QVBoxLayout()
        right_status_layout.setSpacing(3)
        right_status_layout.addWidget(self.critical_rate_label)
        right_status_layout.addWidget(self.critical_damage_label)
        right_status_layout.addWidget(self.attack_range_label)

        # 3개의 열을 가로로 배치
        status_layout = QHBoxLayout()
        status_layout.setSpacing(5)
        status_layout.addLayout(left_status_layout)
        status_layout.addLayout(middle_status_layout)
        status_layout.addLayout(right_status_layout)

        # ----- UI 추가 -----
        self.main_layout.addLayout(top_layout)
        self.main_layout.addWidget(self.create_section("⚔️ Status", status_layout))

        self.setLayout(self.main_layout)
        self.update_state(None)

    def update_state(self, unit):
        unit_info = get_info(unit)
        if unit is None:
            unit = {
                "cost": 1,
                "level": 1,
            }
        name = unit_to_text(unit)
        self.name_label.setText(f"{name}")
        self.name_label.setStyleSheet("""
            QLabel {
                background-color:rgb(89, 103, 124);
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
                padding-bottom: 10px;
                padding: 4px;    
                min-width: 80px;
                min-height: 20px;
            }
        """)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.gold_label.setText(f"💰 {get_price(unit)}")
        self.gold_label.setStyleSheet("""
            QLabel {
                background-color:rgb(89, 103, 124);
                color: white;
                font-size: 28px;
                font-weight: bold;
                border-radius: 10px;
                padding-bottom: 10px;
                padding: 4px;    
                min-width: 80px;
                min-height: 20px;
            }
        """)
        self.gold_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hp_label.setText(f"❤️ {int(unit_info['hp'])}")
        self.attack_label.setText(f"ATK {int(unit_info['attack'])}")
        self.defense_label.setText(f"DEF {int(unit_info['defense'])}")
        self.attack_speed_label.setText(f"Speed {float(unit_info['attackSpeed']):.2f}")
        self.attack_range_label.setText(f"🏹 {int(unit_info['attackRange'])}")

    def create_section(self, title, layout):
        frame = QFrame()
        title_label = QLabel(f"<b>{title}</b>")

        section_layout = QVBoxLayout()
        section_layout.addWidget(title_label)
        section_layout.addLayout(layout)  

        frame.setLayout(section_layout)  
        return frame
