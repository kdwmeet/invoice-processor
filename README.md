# Intelligent Document Processing (지능형 B2B 인보이스 및 발주서 파이프라인)

## 1. 프로젝트 개요

Intelligent Document Processing 파이프라인은 정제되지 않은 형태의 비즈니스 문서(인보이스, 발주서, 영수증 등) 텍스트를 입력받아, 사내 ERP 및 데이터베이스 시스템에 즉시 연동할 수 있는 엄격한 규격의 JSON 데이터로 변환하는 자동화 시스템입니다.

기존 프롬프트 엔지니어링의 한계인 런타임 파싱 에러(Parsing Error)와 데이터 환각(Hallucination)을 원천 차단하기 위해, LangChain의 `with_structured_output` API와 파이썬의 `Pydantic` 라이브러리를 결합했습니다. 이를 통해 AI 모델이 개발자가 정의한 데이터 타입(문자열, 정수, 부동소수점, 날짜 포맷 등)과 중첩된 계층 구조(Nested Schema)에 완벽하게 맞춰 응답하도록 강제합니다.

## 2. 시스템 아키텍처

본 시스템은 단일 노드로 구성되어 있으나, 내부적으로 강력한 스키마 검증 로직을 포함하고 있습니다.

1. **Schema Definition:** `Pydantic`을 사용하여 인보이스 전체 정보(공급자, 발행일, 결제기한, 총액 등)와 개별 구매 품목 리스트(품목명, 수량, 단가)에 대한 엄격한 데이터 클래스를 정의합니다.
2. **Input Processing:** 사용자가 OCR로 추출하거나 복사한 거친 형태의 인보이스 원본 텍스트를 입력합니다.
3. **Structured Extraction:** LLM(gpt-5-mini)이 텍스트를 분석하고, 내부적으로 Pydantic 스키마 규격에 맞추어 변수 타입을 캐스팅(Type Casting)합니다. 자연어로 표기된 날짜(예: "다음달 15일")나 포맷이 섞인 금액(예: "1,500,000 원")을 시스템 규격에 맞게 자동 정제합니다.
4. **Validation & Output:** 스키마 검증을 통과한 데이터만 최종 상태(State)에 딕셔너리 형태로 저장되며, 관제 대시보드에 구조화된 JSON 형태로 출력됩니다.

## 3. 기술 스택

* **Language:** Python 3.10+
* **Package Manager:** uv
* **LLM:** OpenAI gpt-5-mini (구조화된 출력 및 데이터 파싱에 최적화)
* **Data Validation:** Pydantic (v2)
* **Orchestration:** LangGraph, LangChain (langchain_core)
* **Web Framework:** Streamlit

## 4. 프로젝트 구조

```text
invoice-processor/
├── .env                  # OpenAI API 키 설정
├── requirements.txt      # 의존성 패키지 목록
├── main.py               # Streamlit 기반 실시간 데이터 추출 관제 대시보드
└── app/
    ├── __init__.py
    └── graph.py          # Pydantic 스키마 정의 및 구조화된 추출 노드 구현
```

## 5. 설치 및 실행 가이드
### 5.1. 환경 변수 설정
프로젝트 루트 경로에 .env 파일을 생성하고 API 키를 입력하십시오.

```Ini, TOML
OPENAI_API_KEY=sk-your-api-key-here
```
### 5.2. 의존성 설치 및 앱 실행
독립된 가상환경을 구성하고 애플리케이션을 구동합니다.

```Bash
uv venv
uv pip install -r requirements.txt
uv run streamlit run main.py
```
## 6. 테스트 시나리오 및 검증 방법
애플리케이션 구동 후, 비정형 데이터가 포함된 인보이스 텍스트를 입력하여 다음 사항을 검증합니다.

* **날짜 포맷 정제**: "다음달 15일까지 부탁드립니다"와 같은 자연어 표현이 YYYY-MM-DD 형태의 정확한 날짜 데이터로 파싱되는지 확인합니다.

* **타입 캐스팅(Type Casting)**: 단가와 합계에 포함된 문자(원, KRW)나 콤마(,)가 제거되고 순수한 숫자(Integer 또는 Float) 타입으로만 반환되는지 확인합니다.

* **중첩 구조(Nested Structure) 생성**: 여러 개의 구매 품목이 items라는 키 값 하위의 리스트(List) 형태로 누락 없이 모두 분리되어 담기는지 확인합니다.

## 7. 실행 화면