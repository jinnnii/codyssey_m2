#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QuizGame 클래스 정의 파일

게임 전체의 흐름을 관리합니다.
메뉴 표시, 퀴즈 진행, 퀴즈 추가, 최고 점수 확인,
그리고 state.json을 통한 데이터 저장/불러오기를 담당합니다.

이 파일은 "게임 진행"만 맡고, 문제 하나(문장·선택지·정답)의
표현은 quiz.py의 Quiz 클래스에 맡겨 둡니다.
"""

import json
import os
import sys
import random
from typing import List, Optional
from quiz import Quiz  # quiz.py 파일에서 Quiz 클래스 가져오기
from config import GameConfig

class QuizGame:
    """
    퀴즈 게임 전체를 관리하는 클래스

    attributes:
        quizzes (list)     : Quiz 객체들의 리스트. 저장·목록에 쓰는 원래 순서
        best_score (float)   : 최고 점수
        best_total (int)   : 최고 점수 문제 수

    methods:
        show_menu()        : 메뉴 출력
        run()              : 게임 메인 루프
    """

    def __init__(self, config: GameConfig):
        """
        게임 시작 시 실행되는 초기화 메서드
        """
        self.quizzes: List[Quiz] = []
        self.best_score: float = 0
        self.best_total: int = 0
        self.history: List[dict] = []
        self.config: GameConfig = config or GameConfig()


    def show_menu(self) -> None:
        """메인 메뉴를 화면에 출력합니다. 입력은 받지 않고, 선택은 run()에서 처리합니다."""
        print("\n" + "=" * 40)
        print("      🎯 나만의 퀴즈 게임 🎯")
        print("=" * 40)
        print("  1. 퀴즈 풀기")
        print("  2. 퀴즈 추가")
        print("  3. 퀴즈 삭제")
        print("  4. 퀴즈 목록")
        print("  5. 점수 확인")
        print("  6. 히스토리 확인")
        print("  7. 도움말")
        print("  8. 종료")
        print("=" * 40)


    def run(self) -> None:
        """
        게임의 메인 루프입니다. 종료를 고르기 전까지 메뉴를 반복합니다.

        1 퀴즈 풀기, 2 퀴즈 추가, 3 퀴즈 목록, 4 점수 확인, 5 종료.
        5를 고르거나, 메뉴 처리 도중 Ctrl+C / EOF가 발생하면
        현재 데이터를 저장하고 루프를 빠져나갑니다.
        """
        print("\n🎮 퀴즈 게임에 오신 것을 환영합니다!")
        print("\n 활성화 된 설정:")
        print(f"    - 힌트 사용 여부: {'예' if self.config.hint else '아니오'}")
        print(f"    - 힌트 패널티: {self.config.hint_penalty}점")
        print(f"    - 히스토리 저장 여부: {'예' if self.config.save_history else '아니오'}")
        print(f"    - 문제 수 선택 여부: {'예' if self.config.qcount else '아니오'}")
        print(f"    - 문제 랜덤 선택 여부: {'예' if self.config.shuffle else '아니오'}")

        while True:
            try:
                self.show_menu()
                choice = input("선택: ")
                if choice == 1:
                    # todo
                    return
                elif choice == 2:
                    # todo
                    return
                elif choice == 3:
                    # todo
                    return
                elif choice == 4:
                    # todo
                    return
                elif choice == 5:
                    # todo
                    return
                elif choice == 6:
                    # todo
                    return
                elif choice == 7:
                    # todo
                    return
                elif choice == 8:
                    print("\n👋 게임을 종료합니다. 데이터가 저장되었습니다.")
                    return
            except:
                print("\n\n프로그램을 안전하게 종료합니다.")
                break
