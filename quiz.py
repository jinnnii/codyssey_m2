#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quiz 클래스 정의 파일
개별 퀴즈 하나하나를 표현하는 클래스입니다.
"""

from typing import List, Optional, Dict, Any


class Quiz:
    """
    개별 퀴즈를 표현하는 클래스

    속성(attribute):
        question (str)  : 문제 내용
        choices (list)  : 선택지 리스트
        answer (int)    : 정답 번호
        hint (str|None) : 힌트. 없으면 None

    메서드(method):
        display()       : 퀴즈를 화면에 출력
        check_answer()  : 사용자가 입력한 답이 맞는지 확인
        to_dict()       : JSON 저장을 위해 딕셔너리로 변환
        from_dict()     : 딕셔너리에서 Quiz 객체 생성 (클래스 메서드)
    """

    def __init__(self, question: str, choices: List[str], answer: int, hint: Optional[str] = None):
        """
        Quiz 객체 생성 (생성자)

        Args:
            question: 문제 내용
            choices: 선택지 리스트 (예: ["선택1", "선택2", "선택3", "선택4"])
            answer: 정답 번호 (1, 2, 3, 4 중 하나)
            hint: 힌트. 없거나 공백이면 None
        """
        self.question = question
        self.choices = choices
        self.answer = answer
        self.hint = hint

    def display(self, index: Optional[int] = None) -> None:
        """
        퀴즈를 터미널에 예쁘게 출력하는 메서드

        Args:
            index: 문제 번호 (있으면 [문제 1] 형태로 표시)
        """
        if index is not None:
            print(f"\n[문제 {index}]")
        else:
            print("\n" + "-" * 40)

        # 문제 출력
        print(self.question)
        print()

        # 선택지 출력 (1부터 번호 매김)
        for i, choice in enumerate(self.choices, 1):
            print(f"  {i}. {choice}")
        print()

    def check_answer(self, user_answer: int) -> bool:
        """
        사용자가 입력한 답과 정답을 비교

        Args:
            user_answer: 사용자가 입력한 번호 (1~4)

        Returns:
            bool: 맞으면 True, 틀리면 False
        """
        return user_answer == self.answer

    def to_dict(self) -> Dict[str, Any]:
        """
        Quiz 객체를 딕셔너리로 변환
        (JSON 파일에 저장하기 위해 사용)
        """
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint,
        }


    # classmethod: 인스턴스 대신 클래스 자체를 첫 번째 인자로 받는 메서드
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Quiz":
        """
        딕셔너리 데이터로부터 Quiz 객체를 생성하는 클래스 메서드
        (JSON 파일에서 불러올 때 사용)

        Args:
            data: Quiz 필드를 담은 딕셔너리
            예: {"title": "Python 퀴즈", "questions": [...]}

        Returns:
            Quiz 객체
        """
        return cls(
            question=data["question"],
            choices=data["choices"],
            answer=data["answer"],
            hint=data.get("hint"),
        )