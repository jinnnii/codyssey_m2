#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
프로그램 진입점 (Entry Point)
이 파일을 실행하면 퀴즈 게임이 시작됩니다.

실행 방법:
    python main.py
    또는
    python3 main.py
"""

from quiz_game import QuizGame
from config import GameConfig

def main():
    """프로그램의 시작점"""

    # 퀴즈 게밍 설정
    config = GameConfig(
        state_path = "state.json",
        save_history = True,
        shuffle = True,
        hint = True,
        qcount = True,
        hint_penalty = 0.5,
    )
    game = QuizGame(config = config)  # 게임 객체 생성 (이때 데이터도 자동으로 불러옴)
    game.run()         # 메인 루프 시작

# 이 파일이 직접 실행될 때만 main() 함수를 호출
# (다른 파일에서 import 할 때는 실행되지 않음)
if __name__ == "__main__":
    main()