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

from quiz import Quiz  # quiz.py 파일에서 Quiz 클래스 가져오기
from config import GameConfig

import json
import os
import sys

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
        self.load_data() # 프로그램 시작하자마자 저장된 데이터 불러오기


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


    def load_data(self) -> None:
        """
        state.json 파일에서 퀴즈와 점수를 불러옵니다.

        - 파일이 없으면 → 기본 퀴즈로 시작하고, 다음 실행을 위해 바로 저장
        - 퀴즈 목록이 비어 있으면 → 기본 퀴즈로 다시 채움
        - 파일이 깨졌거나 형식이 다르면 → 안내 후 기본 퀴즈로 복구
        """

        # 첫 실행이거나 저장 파일을 지운 경우, 기본 데이터 로드 및 저장
        if not os.path.exists(self.config.state_path):
            print("⚠️ 저장된 데이터가 없습니다. 기본 퀴즈로 시작합니다.")
            self._load_default_quizzes()
            self.save_data()
            return

        try:
            # 파일 '읽기' 모드로 열고, JSON 형식으로 파싱합니다.
            with open(self.config.state_path, "r", encoding="utf-8") as f:
                data = json.load(f) # json -> dict

            # 'get' 메서드를 사용하여 키가 누락되어 있으면 기본값을 사용
            # 'from_dict' 메서드를 사용하여 json 데이터를 Quiz 객체로 변환
            # 퀴즈 항목 하나의 형식이 잘못되면 KeyError를 내고,
            # 아래 except에서 기본 퀴즈로 복구한다.
            self.quizzes = [Quiz.from_dict(q) for q in data.get("quizzes", [])] # dict -> Quiz
            self.best_score = data.get("best_score", 0.0)
            self.best_total = data.get("best_total", 0)

            # 파일은 있지만 퀴즈가 하나도 없으면 게임을 진행할 수 없으므로 기본 문제를 채우고 저장
            if not self.quizzes:
                print("⚠️ 저장된 퀴즈가 없습니다. 기본 퀴즈를 불러옵니다.")
                self._load_default_quizzes()
                self.save_data()
            else:
                print(
                    f"✅ 저장된 데이터를 불러왔습니다. \n"
                    f"문제: 총 {len(self.quizzes)}개\n최고 점수: {self._format_score()}"
                )

        except (json.JSONDecodeError, KeyError, TypeError, IOError) as e:
            # JSONDecodeError: JSON 문법 오류
            # KeyError, TypeError: 필요한 키 누락, 값의 형태가 예상과 다름
            # IOError: 파일은 있지만 읽지 못함
            print(f"⚠️ 데이터 파일이 손상되었습니다: {e}")
            print("⚠️ 기본 퀴즈 데이터로 복구합니다.")
            self._load_default_quizzes()
            self.save_data()

    def _load_default_quizzes(self) -> None:
        """
        기본 퀴즈 6개를 직접 작성해서 넣는 메서드
        (주제: 파이썬 프로그래밍 기초)

        기본 문제로 되돌릴 때는 최고 점수도 함께 0으로 초기화
        """
        default_data = [
            {
                "question": "파이썬의 창시자는 누구인가요?",
                "choices": ["귀도 반 로섬", "리누스 토르발스", "빌 게이츠", "제임스 고슬링"],
                "answer": 1,
                "hint": "네덜란드 출신으로, 1989년 크리스마스 무렵 이 언어를 만들기 시작했습니다.",
            },
            {
                "question": "파이썬에서 리스트를 나타내는 기호는 무엇인가요?",
                "choices": ["()", "[]", "{}", "<>"],
                "answer": 2,
                "hint": "소괄호는 튜플, 중괄호는 딕셔너리에 쓰입니다. 여러 값을 순서대로 담는 쪽을 고르세요.",
            },
            {
                "question": "파이썬에서 들여쓰기는 어떤 역할을 하나요?",
                "choices": ["주석을 달 때 사용", "코드 블록을 구분", "변수 선언", "함수 호출"],
                "answer": 2,
                "hint": "파이썬은 중괄호 대신 공백으로 어디에 속한 코드인지 구분합니다.",
            },
            {
                "question": "다음 중 파이썬의 기본 데이터 타입이 아닌 것은?",
                "choices": ["int", "str", "bool", "array"],
                "answer": 4,
                "hint": "int, str, bool은 파이썬에 기본으로 있습니다. 나머지를 고르세요.",
            },
            {
                "question": "파이썬에서 함수를 정의할 때 사용하는 키워드는?",
                "choices": ["function", "def", "func", "define"],
                "answer": 2,
                "hint": "define의 앞 세 글자입니다. 함수 이름 바로 앞에 붙습니다.",
            },
            {
                "question": "파이썬에서 조건문을 작성할 때 사용하는 키워드는?",
                "choices": ["if", "when", "check", "condition"],
                "answer": 1,
                "hint": "조건이 참일 때만 아래 코드를 실행합니다. else와 짝으로 자주 씁니다.",
            },
        ]
        self.quizzes = [Quiz.from_dict(d) for d in default_data]
        self.best_score = 0.0
        self.best_total = 0

    def save_data(self) -> None:
        """
        state.json 파일에 퀴즈 목록과 최고 점수를 저장
        프로그램을 종료해도 데이터가 유지
        Quiz 객체는 JSON이 바로 저장할 수 없어서 'to_dict()' 메서드를 사용하여 딕셔너리로 변환하고 저장
        저장에 실패해도 게임 자체가 멈추지는 않고, 오류 메시지만 출력
        """
        data = {
            "quizzes": [q.to_dict() for q in self.quizzes], # Quiz -> dict
            "best_score": self.best_score,
            "best_total": self.best_total,
        }
        try:
            # json.dump: JSON 데이터를 파일에 씀
            # ensure_ascii=False: 한글을 유니코드 이스케이프(\\uXXXX) 로 바꾸지 않고 그대로 저장, 한글 파일일 때 거의 필수
            # indent=2: 보기 좋게 줄바꿈, 들여쓰기해서 저장 (2칸)
            with open(self.config.state_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"⚠️ 데이터 저장 중 오류가 발생했습니다: {e}")


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
