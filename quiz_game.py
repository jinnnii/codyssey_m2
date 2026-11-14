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
from input_result import InputResult

import json
import os
import sys
from typing import List, Optional

class UserExit(Exception):
    """
    사용자가 퀴즈 진행 중 나가기(q)를 선택했을 때 발생하는 예외 처리

    단순히 메뉴로 돌아가는 것 외에도,
    지금까지 푼 문제 수, 정답 수, 힌트 사용 횟수를 함께 전달해서 중간 저장 여부를 판단할 수 있게 한다.
    """

    def __init__(self, total: int = 0, correct: int = 0, hint_used: int = 0, curr_idx: int = 0):
        self.total = total  # 문제 총 개수
        self.correct = correct  # 정답 개수
        self.curr_idx = curr_idx # 현재 문제 위치
        self.hint_used = hint_used # 힌트 사용 횟수
        super().__init__()

    @property
    def is_run_quiz(self) -> bool:
        """
        실제로 문제를 하나 이상 풀었는지 여부.

        curr_idx가 1보다 크면 최소 한 문제는 진행한 것으로 본다.
        (문제를 하나도 안 풀고 바로 나간 경우와 구분)
        """
        return self.total > 0 and self.curr_idx > 1



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
    
    def _format_score(self) -> str:
        """
        최고 점수를 화면에 보여줄 문자열로 만들어 반환
        퍼센트는 소수점을 버리고 정수로 표시

        """
        percentage = round((self.best_score / self.best_total) * 100, 1) if self.best_total > 0 else 0.0
        return f"{percentage}점 ({self.best_score}/{self.best_total})"


    def _get_input_result(self, user_input: str,  hint_yn: bool = False) -> InputResult:
        """
        사용자 입력 문자열을 해석해서 InputResult로 변환한다.

        InputResult.from_input()으로 1차 분류한 뒤,
        현재 상황(hint_yn)에 따라 실제로 어떻게 처리할지 결정한다.

        Args:
            user_input: 사용자가 입력한 문자열
            hint_yn: 힌트 입력을 허용할지 여부
                    (퀴즈 정답 입력 시에만 True)

        Returns:
            InputResult: 처리된 결과
                - HINT: 힌트 요청 (hint_yn=True일 때만)
                - VALUE: 일반 입력
                - 그 외는 이 메서드 안에서 처리되거나 예외 발생

        Raises:
            UserExit: "q" 입력 시 발생. 메뉴로 돌아간다.
        """

        # 문자열 입력 처리 결과에 따라 분기
        # 입력 문자열을 InputResult로 변환
        result = InputResult.from_input(user_input)

        # 힌트 허용 + "h" 입력인 경우
        if hint_yn and result == InputResult.HINT:
            return result

        # "q" → 현재 작업 취소 (메뉴로)
        elif result == InputResult.QUIT:
            raise UserExit()

        # "exit" → 프로그램 완전 종료
        elif result == InputResult.EXIT:
            self._handle_exit()

        # "help" → 약어 안내 출력
        elif result == InputResult.HELP:
            self._print_abbreviations()

        # 일반 입력 (숫자, 문제 텍스트 등)
        elif result == InputResult.VALUE:
            return result

        # 그 외 (예상치 못한 경우) → 일반 입력으로 처리
        else:
            return InputResult.VALUE


    def _get_bool_input(self, prompt: str) -> bool:
        """
        참/거짓을 입력받을 때까지 다시 물어봅니다.
        """
        while True:
            user_input = self._get_str_input(prompt)
            if user_input.strip().lower() == "y":
                return True
            elif user_input.strip().lower() == "n":
                return False
            else:
                print("⚠️ 올바른 입력이 아닙니다. 다시 입력해주세요.")
            

    def _get_str_input(self, prompt: str, max_length: int = 100, allow_empty: bool = False) -> str:
        """
        문자열을 입력받을 때까지 다시 물어봅니다.

        args:
            prompt: 사용자에게 보여줄 입력 안내 메시지
            max_length: 최대 문자 길이

        returns:
            str: 입력 문자열

        raises:
            KeyboardInterrupt: Ctrl+C를 눌렀을 때
            EOFError: 입력 스트림이 끊어졌을 때
            UserExit: 나가기를 요청했으면 메뉴로 돌아간다.
        """

        while True:
            try:
                # 입력 문자열 입력 받기
                user_input = input(prompt).strip()
                # 입력 문자열로 InputResult 찾기
                result = self._get_input_result(user_input)

                # 필수 입력일 때, 입력이 비어 있으면 안내 메시지 출력 후 재입력
                if not allow_empty and result is InputResult.EMPTY:
                    print("⚠️ 입력이 비어 있습니다. 다시 입력해주세요.")
                    continue

                # 입력 문자열 길이 체크
                if len(user_input) <= max_length:
                    return user_input # 정상 입력이면 입력 문자열을 반환한다.

                # 입력 문자열이 최대 글자수를 초과 시, 안내 메시지 출력 후 재입력
                print(f"⚠️ 입력이 {max_length}자 이하여야 합니다. 다시 입력해주세요.")
                
            except (KeyboardInterrupt, EOFError):
                self._handle_exit() # 종료를 요청했으면 프로그램을 종료한다.

    def _read_int(self, prompt: str, min_val: int, max_val: int, hint_yn: bool = False) -> tuple[InputResult, Optional[int]]:
        """
        범위 안의 정수를 입력받을 때까지 다시 물어봅니다.

        잘못된 입력은 예외로 프로그램을 끝내지 않고, 이유를 알려 준 뒤 같은 질문을 반복합니다.

        숫자 입력 케이스 처리:
            - 입력 앞뒤 공백 제거 후 처리
            - 숫자 변환 실패 (예: abc) 시 안내 메시지 출력 후 재입력 복귀
            - 허용 범위 밖 숫자 입력 시 안내 메시지 출력 후 재입력 복귀
            - 빈 입력(그냥 Enter) 시 안내 메시지 출력 후 재입력 복귀

        프로그램 실행 중 예외 처리:
            - Ctrl+C(KeyboardInterrupt)나 입력 스트림이 끊기는 경우(EOFError)는 여기서 저장한 뒤 프로그램을 종료

        args:
            prompt: 사용자에게 보여줄 입력 안내 메시지
            min_val: 허용되는 최소값
            max_val: 허용되는 최대값

        returns:
            (InputResult.VALUE, 숫자)   → 정상 입력
            (InputResult.HINT, None)    → h 또는 힌트. hint_yn일 때만
        """
        while True:
            try:
                user_input = input(prompt).strip()  # 앞뒤 공백 제거

                # 입력 문자열로 InputResult 찾기
                result = self._get_input_result(user_input, hint_yn=hint_yn)

                # 빈 입력 시 안내 메시지 출력
                if result is InputResult.EMPTY: 
                    print("⚠️ 입력이 비어 있습니다. 다시 입력해주세요.")
                    continue

                # 문자열 입력 처리 결과에 따라 분기
                if result is not InputResult.VALUE:
                    return (result, None)

                # 문자열에서 정수 변환. 실패하면 ValueError 예외 발생
                value = int(user_input)
                
                # 범위 내 숫자 입력 시, 반환
                if min_val <= value <= max_val:
                    return (result, value)
                else:
                    # 범위 밖의 숫자를 입력했을 때 안내 메시지 출력
                    print(f"⚠️ {min_val}~{max_val} 사이의 숫자를 입력해주세요.")

            except ValueError:
                # 숫자 변환 실패 시 안내 메시지 출력
                print("⚠️ 숫자만 입력해주세요.")
            except (KeyboardInterrupt, EOFError):
                # 예외 처리
                self._handle_exit()

    def _handle_exit(self) -> None:
        """
        프로그램을 안전하게 종료합니다.
        """
        print("\n\n프로그램을 안전하게 종료합니다.")
        self.save_data()
        sys.exit(0)

    def _get_int_input(self, prompt: str, min_val: int, max_val: int) -> int:
        """
        숫자를 입력받을 때까지 다시 물어봅니다.
        """
        _, value = self._read_int(prompt, min_val, max_val)
        return value

    def get_answer_input(self, prompt: str) -> tuple[InputResult, Optional[int]]:
        """
        정답 입력 받기
        """
        return self._read_int(prompt, 1, 4, hint_yn=self.config.hint)

    def _print_abbreviations(self) -> None:
        """
        약어를 출력합니다.
        """
        print("\n" + "=" * 40)
        print(" 약어 목록")
        print("=" * 40)
        print(f" q: 메누로 나가기")
        print(f" h: (정답 입력 시) 힌트 보기")
        print(f" help: 도움말")
        print(f" exit: 종료")
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
                choice = self._get_int_input("선택: ", 1, 8)
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
            except UserExit:
                print("\n\n프로그램을 안전하게 종료합니다.")
                self.save_data()
                break
