# Quiz Game

터미널에서 동작하는 퀴즈 게임.  
Python 표준 라이브러리만 사용하며, 클래스 기반으로 구조화하고 JSON으로 상태를 영속화한다.

## 프로젝트 개요

메뉴 기반 CLI 퀴즈 게임

- 퀴즈 풀기 / 추가 / 목록 / 삭제 / 점수 확인
- 프로그램을 종료해도 `state.json`에 데이터가 유지됨
- 힌트, 문제 수 선택, 랜덤 출제, 히스토리 저장 지원

## 퀴즈 주제 선정 이유

**주제: 파이썬 프로그래밍 기초**

이 미션 자체가 Python을 배우는 과정이므로,  
학습 내용과 직접 연관된 주제를 선택했다.  
문제를 풀면서 기초 개념을 복습할 수 있도록 구성했다.

## 요구 사항

- Python 3.10+
- 외부 라이브러리 없음

## 실행 방법

```bash
python main.py
```

## 실행 (`main.py`)
```python
from config import GameConfig
from quiz_game import QuizGame

config = GameConfig(
    shuffle=True, # (선택 과제) 문제 랜덤 출제
    qcount=True, # (선택 과제) 문제 개수 선택
    hint=True, # (선택 과제) 힌트 사용
    hint_penalty=0.5, # (선택 과제) 힌트 패널티
    save_history=True, # (선택 과제) 히스토리
)
game = QuizGame(config)
game.run()
```
- 설정 데이터 클래스를 만들어 실행


## 기능 목록
| 번호 | 기능 | 설명 |
| --- | --- | --- |
| 1 | 퀴즈 풀기 | 퀴즈 출제 및 채점 |
| 2 | 퀴즈 추가 | 문제, 선택지, 정답, 힌트 입력 |
| 3 | 퀴즈 삭제 | 등록된 퀴즈 삭제 |
| 4 | 퀴즈 목록 | 등록된 퀴즈 확인 |
| 5 | 점수 확인 | 최고 점수 확인 |
| 6 | 히스토리 | 게임 기록 확인 |
| 7 | 도움말 | 명령어 안내 |
| 8 | 종료 | 저장 후 종료 |


## 입력 명령어
- `q` : 현재 작업 취소 (메뉴로 이동)
- `h` : 힌트 보기 (문제 답변 입력 시)
- `exit` : 프로그램 종료
- `help` : 도움말

## 파일 구조
```
.
├── main.py            # 진입점
├── quiz.py            # Quiz 클래스
├── quiz_game.py       # QuizGame 클래스
├── config.py          # GameConfig
├── input_result.py    # InputResult 열거형
├── state.json         # 퀴즈 + 최고 점수
├── history.json       # 이력 (선택)
├── .gitignore
└── README.md
```



## 데이터 파일 
### `state.json`
```json
{
  "quizzes": [
    {
      "question": "문제 내용",
      "choices": ["선택지1", "선택지2", "선택지3", "선택지4"],
      "answer": 1,
      "hint": "힌트"
    }
  ],
  "best_score": 4.0,
  "best_total": 5
}
```
- 파일 없음 -> 기본 퀴즈 데이터로 생성
- 파일 손상 -> 안내 후 기본 퀴즈 데이터로 복구


### `history.json`
```json
[
  {
    "date": "2026-11-14 15:30:00", 
    "total_questions": 5,
    "score": 4.0,
    "hint_used": 1
  }
]
```
- 파일 없음 -> 게임 종료 후 자동 생성
- 새로운 기록은 최신 순으로 추가


## `GameConfig`: 설정
```python
@dataclass
class GameConfig:
    state_path: str = "state.json"
    history_path: str = "history.json"
    save_history: bool = True
    shuffle: bool = False
    hint: bool = False
    hint_penalty: float = 0.5
    qcount: bool = False
```

## `Quiz`: 개별 퀴즈 클래스
```python
class Quiz:
    def __init__(self, question: str, choices: list[str], answer: int, hint: str = None):
        self.question = question
        self.choices = choices
        self.answer = answer      # 1~4
        self.hint = hint

    def display(self, index: int) -> None:
        """문제와 선택지를 출력"""

    def check_answer(self, user_answer: int) -> bool:
        """정답 여부 확인"""

    def to_dict(self) -> dict:
        """JSON 저장용 딕셔너리로 변환"""

    @classmethod
    def from_dict(cls, data: dict) -> "Quiz":
        """딕셔너리에서 Quiz 객체 생성"""
```

## `QuizGame`: 게임 전체 흐름을 관리하는 클래스
```python
class QuizGame:
    def __init__(self, config: GameConfig):
        """설정 주입 후 데이터 로드"""

    def run(self) -> None:
        """메인 루프. 메뉴를 반복 표시하고 선택에 따라 분기"""

    def play_quiz(self) -> None:
        """퀴즈 진행 (출제, 채점, 결과)"""

    def add_quiz(self) -> None:
        """새 퀴즈 추가"""

    def delete_quiz(self) -> None:
        """퀴즈 삭제"""

    def list_quizzes(self) -> None:
        """등록된 퀴즈 목록 출력"""

    def show_score(self) -> None:
        """최고 점수 출력"""

    def show_history(self) -> None:
        """플레이 기록 출력"""

    def load_data(self) -> None:
        """state.json에서 퀴즈와 점수 불러오기"""

    def save_data(self) -> None:
        """state.json에 퀴즈와 점수 저장"""
```

### 내부 메서드 (`_`)
- 클래스 내부에서만 사용하는 메서드
```python
def _load_default_quizzes(self) -> None:
    """기본 퀴즈 6개 로드"""

def _run_quiz(self, quizzes) -> tuple[int, int]:
    """퀴즈 진행. (정답 수, 힌트 사용 수) 반환"""

def _ask_answer(self, quiz) -> tuple:
    """한 문제 정답 입력 (힌트 처리 포함)"""

def _select_quizzes(self) -> list:
    """문제 수 선택 후 랜덤 추출"""

def _shuffle_quizzes(self) -> list:
    """퀴즈 순서 섞기"""

def _calculate_score(self, total, correct, hint_used) -> tuple:
    """점수 계산 (힌트 감점 반영)"""

def _update_best_score(self, score, total) -> None:
    """최고 점수 갱신"""

def _print_result(self, ...) -> None:
    """문제 체점 결과 출력"""

def _save_history(self, score, total, hint_used) -> None:
    """히스토리 저장 (최신순)"""

def _read_int(self, prompt, min_val, max_val, hint_yn=False) -> tuple:
    """숫자 입력 공통 처리"""

def _get_int_input(self, prompt, min_val, max_val) -> int:
    """숫자만 입력받기"""

def _get_answer_input(self, prompt) -> tuple:
    """정답 입력 (힌트 허용)"""

def _get_str_input(self, prompt, ...) -> str:
    """문자열 입력"""

def _get_bool_input(self, prompt) -> bool:
    """y/n 입력"""

def _get_input_result(self, user_input, hint_yn=False) -> InputResult:
    """입력을 InputResult로 변환"""

def _handle_exit(self) -> None:
    """안전 종료 (저장 후 종료)"""

def _format_score(self) -> str:
    """최고 점수를 문자열로 반환"""

def _print_abbreviations(self) -> None:
    """명령어 도움말 출력"""
```


## `InputResult`: 특수 입력을 구분하는 열거형 
```python
class InputResult(Enum):
    VALUE = auto()   # 일반 입력
    EMPTY = ""       # 빈 입력
    HINT = "h"       # 힌트
    QUIT = "q"       # 메뉴로 나가기
    EXIT = "exit"    # 프로그램 종료
    HELP = "help"    # 도움말
```

## Git
- 기능 단위로 커밋하고 브랜치를 사용했다.

```bash
git switch -b feature/play-quiz
# 커밋 진행 후
git checkout main
git merge feature/play-quiz
```


## 과제 목표

이 미션을 마친 후 아래 내용을 스스로 설명할 수 있어야 한다.

### Python 기초

**변수**  
값을 저장하는 이름 있는 공간. 정확히는 객체를 가리키는 이름이다.  
불변 객체(`int`, `str`)는 값을 바꾸면 새 객체가 생기고,  
가변 객체(`list`, `dict`)는 같은 객체를 여러 변수가 참조할 수 있다.
```
불변:
[a] ──→ 10
[b] ──→ 20

가변:
[x] ──┐
      ├──→ [1, 2, 3, 4]
[y] ──┘
```

**자료형**

| 자료형 | 설명 |
|--------|------|
| `int` | 정수 |
| `str` | 문자열 |
| `bool` | 참/거짓 |
| `list` | 순서가 있는 여러 값 |
| `dict` | 키-값 쌍 |

**조건문**  
`if` / `elif` / `else`로 조건에 따라 다른 코드를 실행한다.

**반복문**  
- `for`: 횟수나 대상이 정해져 있을 때  
- `while`: 조건이 참인 동안 반복할 때

**함수**  
특정 작업을 묶어 이름을 붙인 것. 매개변수(`args`) 로 값을 받고, `return`으로 결과를 돌려준다.

### 클래스와 객체

**클래스**  
`속성`과 `메서드`를 하나로 묶은 사용자 정의 타입.  
같은 구조의 객체를 여러 개 만들 수 있다.

**`__init__`과 `self`**  
- `__init__`: 객체가 생성될 때 실행되는 초기화 메서드  
- `self`: 객체 자기 자신을 가리킴

**속성과 메서드**  
- 속성: 객체가 가지는 데이터  
- 메서드: 객체가 수행하는 동작

### 파일 입출력

**파일 열기/읽기/쓰기**

```python
# 쓰기
with open("파일명", "w", encoding="utf-8") as f:
    f.write("내용")

# 읽기
with open("파일명", "r", encoding="utf-8") as f:
    data = f.read()
```

### Git 기초
**주요 명령어**

| 명령어 | 설명 |
|--------|------|
| `git init` | 현재 폴더를 Git 저장소로 초기화 |
| `git add` | 변경된 파일을 스테이징(커밋 대기 상태)에 올림 |
| `git commit` | 스테이징된 변경 사항을 기록 |
| `git push` | 로컬 커밋을 원격 저장소(GitHub)에 업로드 |
| `git pull` | 원격 저장소의 변경 사항을 가져와 병합 |
| `git checkout` | 브랜치 전환 또는 새 브랜치 생성 (`-b`) |
| `git clone` | 원격 저장소를 통째로 로컬에 복제 |

**clone / pull / fetch**
| 명령어 | 설명 |
| --- | --- |
| `clone` | 원격 저장소를 처음 내 컴퓨터로 통째로 복제 |
| `fetch` | 원격 변경 사항을 가져오기만 하고, 현재 브랜치에는 반영하지 않음 |
| `pull` | 원격 변경 사항을 가져와서 현재 브랜치에 병합 (fetch + merge) |


**checkout vs switch**
| 명령어 | 설명 |
|--------|------|
| `checkout` | 예전부터 쓰던 명령. 브랜치 전환 + 파일 복원 등 여러 용도 |
| `switch` | 브랜치 전환만 담당|
- 요즘은 `switch`를 쓰는 경우가 늘고 있지만, 기존 자료나 습관 때문에 `checkout`도 여전히 많이 사용된다.