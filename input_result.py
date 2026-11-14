from enum import Enum, auto

class InputResult(Enum):
    """
    사용자 입력 결과를 구분하는 열거형.

    숫자나 일반 문자열 외에, 특별한 명령(q, h, exit 등)을
    일관된 방식으로 처리하기 위해 사용한다.

    Members:
        VALUE: 일반 입력 (숫자, 문제 텍스트 등)
        EMPTY: 빈 입력 (Enter만 친 경우)
        HINT:  힌트 요청 ("h")
        EXIT:  프로그램 종료 ("exit")
        HELP:  도움말 출력 ("help")
        QUIT:  현재 작업 취소 후 메뉴로 ("q")
    """


    VALUE = auto()      # 그 외 모든 일반 입력
    EMPTY = ""          # 빈 문자열
    HINT = "h"          # 힌트 보기
    EXIT = "exit"       # 프로그램 완전 종료
    HELP = "help"       # 약어/도움말 출력
    QUIT = "q"          # 현재 화면에서 나가기 (메뉴로)

    @classmethod
    def from_input(cls, raw: str) -> "InputResult | None":
        """
        입력 문자열을 InputResult로 변환한다.

        - 빈 문자열이면 EMPTY
        - "h", "q", "exit", "help" 등 정의된 값이면 해당 멤버
        - 그 외에는 VALUE

        Args:
            raw: 사용자 입력 문자열

        Returns:
            InputResult: 해석된 입력 결과
        """

        if not raw.strip(): # 빈 문자열인 경우
            return cls.EMPTY 
        for item in cls: # 약어 입력 시
            if item.value == raw:
                return item
        return cls.VALUE # 그 외 입력 시