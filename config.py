from dataclasses import dataclass
import os
import sys


@dataclass
class GameConfig:
    state_path: str = "state.json"
    history_path: str = "history.json"
    save_history: bool = True

    shuffle: bool = False
    hint: bool = False
    hint_penalty: float = 0.5
    qcount: bool = False

    def __post_init__(self):
        # state 파일 검증
        if not self.state_path or not self.state_path.strip():
            raise ValueError("퀴즈 데이터 파일은 필수 입니다.")
        if not self.state_path.endswith(".json"):
            raise ValueError("퀴즈 데이터 파일은 JSON 파일이어야 합니다.")
        if not os.path.exists(self.state_path):
            print(f"ℹ️ {self.state_file} 파일이 없습니다. 기본 데이터로 시작합니다.")

        # history 검증
        if self.save_history:
            if not self.history_path or not self.history_path.strip():
                raise ValueError("히스토리 파일은 필수 입니다.")
            if not self.history_path.endswith(".json"):
                raise ValueError("히스토리 파일은 JSON 파일이어야 합니다.")

        # 힌트 검증
        if self.hint and self.hint_penalty < 0:
            raise ValueError("힌트 패널티는 0 이상이어야 합니다.")