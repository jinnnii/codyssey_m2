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
import random

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

        # 문자열이 비어있을 때
        elif result == InputResult.EMPTY:
            return result
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

                print(result, ">>>")

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

    def _get_answer_input(self, prompt: str) -> tuple[InputResult, Optional[int]]:
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

    def play_quiz(self) -> None:
        """
        등록된 퀴즈를 섞어서 한 판 퀴즈를 진행하고, 결과 출력
        """
        if not self.quizzes:
            print("\n 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해주세요.")
            return

        try:
            # (선택 과제) 문제 수 선택
            if self.config.qcount:
                selected_quizzes = self._select_quizzes()
            # (선택 과제) 랜덤 출제
            elif self.config.shuffle:
                selected_quizzes = self._shuffle_quizzes()
            else:
                selected_quizzes = self.quizzes.copy()

            # 문제 총 개수
            total = len(selected_quizzes)
            # 퀴즈 실행
            correct, hint_used = self._run_quiz(selected_quizzes)
            # 점수 계산
            final_score, percentage = self._calculate_score(total, correct, hint_used)
            # 최고 점수 갱신 여부 확인
            is_new_best = self._update_best_score(final_score, total)
            # 히스토리 저장
            # self._save_history(final_score, total, hint_used)
            # 결과 출력
            self._print_result(total, correct, hint_used, percentage, is_new_best)

        except UserExit as e:
            if not e.is_run_quiz:
                print("\n퀴즈를 수행하지 않아 그대로 메뉴로 돌아갑니다.")
                return

            # # 중간 이력 저장 
            # save_history = self._get_bool_input(f"{e.curr_idx -1 }번째 문제까지 퀴즈를 풀었습니다. 퀴즈 결과를 히스토리에 저장하시겠습니까? (y/n): ")
            # if save_history:
            #     print(" ㄴ 중간 퀴즈 결과를 저장합니다...\n")
            #     final_score, _ = self._calculate_score(e.curr_idx -1, e.correct, e.hint_used)
            #     self._save_history(final_score, e.curr_idx -1, e.hint_used)
            # else:
            #     print(" ㄴ 퀴즈를 중단하고 메뉴로 돌아갑니다.")


    def _select_quizzes(self) -> list[Quiz]:
        """
        문제 수 선택 후, 문제 랜덤 선택
        """
        # 문제 수 선택
        total = len(self.quizzes)
        try: 
            # 문제 수 입력 받기
            count = self._get_int_input(f"풀고 싶은 문제 수를 입력하세요 (1~{total}개): ", 1, total)
        except ValueError:
            # 숫자 변환 실패 시 모든 문제 풀기
            count = total

        # 문제 랜덤 선택
        # random.sample(population, k): population에서 k개의 요소를 랜덤하게 선택하여 리스트로 반환
        return random.sample(self.quizzes, k=count) # noqa: S2245


    def _shuffle_quizzes(self) -> list[Quiz]:
        """
        문제 랜덤 선택
        """
        # shuffle: 리스트를 섞는 함수, 리스트를 변경하고 반환값은 None
        # noqa (No Quality Assurance): 품질 검사 예외 처리, 보안 경고를 무시하고 코드를 실행
        # S2245: SonarQube 규칙 번호, random 모듈은 예측 가능한 기본 난수 생성기를 써서 보안 경고가 납니다.
        # 비밀번호, 토큰, 세션 키같은 보안이 중요한 용도에는 SystemRandom을 사용해야 하며, (예: secrets.SystemRandom().shuffle(리스트))
        # 퀴즈 게임에는 예측 가능한 기본 난수 생성기를 사용해도 문제 없으므로 noqa 처리합니다.
        quizzes_to_play = self.quizzes.copy()
        random.shuffle(quizzes_to_play) # noqa: S2245
        return quizzes_to_play

    def _run_quiz(self, quizzes: list[Quiz]) -> tuple[int, int]:
        """
        퀴즈를 실행합니다.

        args:
            quizzes: 퀴즈 리스트

        returns:
            correct: 정답 개수
            hint_used: 힌트 사용 횟수
        """
        total = len(quizzes)
        print(f"\n 퀴즈를 시작합니다! (총 {total}문제)")

        # 정답 개수 초기화
        correct = 0

        # 힌트 사용 여부 초기화
        hint_used = 0
        # enumerate(iterable, start=0): 순서가 있는 자료형(리스트, 튜플, 문자열)을 인덱스와 함께 반복
        #   iterable: 순서가 있는 자료형(리스트, 튜플, 문자열)
        #   start: 인덱스의 시작값

        try:

            # 문제 번호를 1부터 시작하기 위해 enumerate의 시작값을 1로 준다.
            for i, quiz in enumerate(quizzes, 1):
                # 문제를 표시하는 메서드 호출
                quiz.display(index=i)
                # 답변 입력 받기 (힌트 사용 입력 포함)
                answer, used_hint = self._ask_answer(quiz)

                # 힌트 사용 시
                if used_hint:
                    # 힌트 사용 횟수 증가
                    hint_used += 1

                # 정답 확인
                if answer is not None and quiz.check_answer(answer):
                    print(" 정답입니다!")
                    # 정답 개수 증가
                    correct += 1
                else:
                    # 오답 시 정답 번호 표시
                    print(f" 오답입니다. 정답은 {quiz.answer}번입니다.")
            return correct, hint_used

        except UserExit: # 퀴즈 중단 시 정답 개수와 힌트 사용 횟수 반환
            raise UserExit(total, correct, hint_used, i)

    def _ask_answer(self, quiz: Quiz) -> tuple[InputResult, Optional[int], bool]:
        """같은 문제에서 정답 번호가 나올 때까지 다시 묻는다.

        힌트를 봐도 다음 문제로 넘기지 않는다.
        힌트가 없으면 감점하지 않고, 같은 문제에서 여러 번 봐도 감점은 한 번이다.
        
        args:
            quiz: 퀴즈 객체

        returns:
            answer: 정답 번호
            used_hint: 힌트 사용 여부
        """
        used_hint = False
        while True:
            # 정답 입력 받기
            result, answer = self._get_answer_input(
                "정답 입력: "
            )
            # 힌트보기를 요청하지 않은 경우 정답 번호 반환
            if result is not InputResult.HINT:
                return answer, used_hint

            # 힌트보기를 요청했지만 힌트가 없으면 힌트 없다고 알림
            if not quiz.hint:
                print("💡 힌트가 없습니다.")
                continue

            # 힌트를 한 번도 보여주지 않은 경우 힌트를 보여준다.
            if not used_hint:
                print(f"💡 힌트: {quiz.hint} ({self.config.hint_penalty}점 감점)")
                used_hint = True
            # 힌트를 한 번 이상 보여준 경우, 감점하지 않고 힌트만 보여준다.
            else:
                print(f"💡 힌트: {quiz.hint}")


    def _calculate_score(self, total: int,correct: int, hint_used: int) -> int:
        """
        점수를 계산합니다.

        args:
            total: 문제 총 개수
            correct: 정답 개수
            hint_used: 힌트 사용 횟수

        returns:
            final_score: 최종 점수
            percentage: 정답 비율(%)
        """

        # 문제가 0개면 0으로 나눌 수 없으므로 점수는 0으로 둔다.
        # 정답 비율(%) 계산, 소수점을 버리고 정수로 표시

        # int(number) -> 99 로 소수점을 버리고 정수로 표시
        # round(number, ndigits=0) -> 99.99 -> 100 반올림 하고 정수로 표시

        # 힌트 사용 시 패널티 점수 감점, 최종 점수 계산에서 점수 감점,
        # 0점 이하로 내려가지 않도록 max(0, 점수 - (힌트 사용 횟수 * 힌트 패널티 점수))
        final_score = max(0.0, correct - (hint_used * self.config.hint_penalty))
        # 정답 비율(%) 계산, 소수점을 버리고 정수로 표시
        percentage = round((final_score / total) * 100, 1) if total > 0 else 0.0
        return final_score, percentage

    def _update_best_score(self, score: float, total: int) -> None:
        """
        최고 점수를 갱신합니다.

        args:
            score: 최종 점수
            total: 문제 총 개수
        returns:
            is_new_best: 최고 점수 갱신 여부
        """
        if total ==0:
            return

        # 현재 정답 비율 계산
        current_ratio = score / total
        # 기존 최고 점수 비율 계산
        best_ratio = (self.best_score / self.best_total) if self.best_total > 0 else 0

        # 현재 점수 비율이 최고 점수를 넘지 못하는 경우 그대로 리턴
        if current_ratio <= best_ratio:
            return

        self.best_score = score
        self.best_total = total

        # 최고 점수, 문제 수 저장
        self.save_data()

    def _print_result(self, total: int, correct: int, hint_used: int, percentage: int, is_new_best: bool) -> None:
        """
        결과를 출력합니다.

        args:
            total: 출제된 전체 문제 수
            correct: 맞힌 개수
            hint_used: 힌트를 사용한 횟수
            percentage: 최종 점수 (힌트 감점 반영, 퍼센트)
            is_new_best: 이번 결과가 최고 기록을 갱신했는지
        """
        print("\n" + "=" * 40)
        print(f" 결과: {total}문제 중 {correct}문제 정답, 힌트 {hint_used}회 ({percentage}점)")
        print("=" * 40)

        # 최고 점수인 경우
        if is_new_best:
            print(" 새로운 최고 점수입니다!")
        print("=" * 40)


    def add_quiz(self) -> None:
        """
        문제, 선택지 4개, 정답 번호를 받아 퀴즈를 하나 추가합니다.

        문제나 선택지가 비어 있으면 추가를 취소합니다.
        일부만 입력된 상태는 저장하지 않아서, 선택지가 모자란 문제가 생기지 않습니다.
        모든 입력이 끝난 뒤에만 목록에 넣고 state.json에 저장합니다.
        """
        print("\n 새로운 퀴즈를 추가합니다.\n")

        question = self._get_str_input("문제를 입력하세요: ").strip()

        choices = []
        for i in range(1, 5):
            choice = self._get_str_input(f"선택지 {i}: ").strip()
            if not choice:
                # 앞 선택지만 있고 뒤가 비면 문제가 불완전하므로 전부 버린다.
                print("⚠️ 선택지를 모두 입력해주세요.")
                return
            choices.append(choice)

        answer = self._get_int_input("정답 번호 : ", 1, 4)
        hint_text = self._get_str_input("힌트 (없으면 Enter): ", allow_empty=True).strip()
        new_quiz = Quiz(question, choices, answer, hint_text or None)
        self.quizzes.append(new_quiz)
        self.save_data()
        print("\n 퀴즈가 추가되었습니다!")



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
                    self.play_quiz()
                elif choice == 2:
                    self.add_quiz()
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
