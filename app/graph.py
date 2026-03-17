from typing import TypedDict, List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END

load_dotenv()

# Pydantic 스키마 정의 (LLM 출력 규격을 강제)
class InvoiceItem(BaseModel):
    """인보이스 내 개별 구매 품목"""
    item_name: str = Field(description="품목의 이름 또는 설명")
    quantity: int = Field(description="구매 수량 (반드시 정수)")
    unit_price: float = Field(description="단가 (숫자만 추출)")
    total_price: float = Field(description="해당 품목의 총액 (수량 * 단가)")

class InvoiceSchema(BaseModel):
    """전체 인보이스 구조"""
    vendor_name: str = Field(description="공급자 또는 발행 기업의 이름")
    invoice_date: str = Field(description="발행 일자 (YYYY-MM-DD 형식으로 변환할 것)")
    due_dtate: Optional[str] = Field(description="결제 기한 (YYYY-MM-DD 형식, 없으면 null)") 
    items: List[InvoiceItem] = Field(description="구매 품목 리스트")
    subtotal: float = Field(description="세금 제외 공급가액 합계")
    tax: float = Field(description="세금 (VAT 등)")
    total_amount: float = Field(description="최종 청구 금액")
    currency: str = Field(description="통화 코드 (예: KRW, USD, EUR 등)")
    
# 상태 정의
class DocumentState(TypedDict):
    raw_text: str               #원본 인보이스 텍스트
    parsed_data: dict           # Pydantic을 통해 구조화 및 검증된 데이터 (딕셔너리로 변환하여 저장)
    error: str                  # 파싱 실패 시 에러 메시지
    
# 노드 구현
def extract_invoice_node(state: DocumentState):
    """원본 텍스트에서 Pydantic 스키마에 맞춰 데이터를 추출합니다."""
    llm = ChatOpenAI(model="gpt-5-mini", reasoning_effort="low")

    # LLM에 Pydantic 스키마를 바인딩하여 구조화된 출력을 강제
    structured_llm = llm.with_structured_output(InvoiceSchema)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 기업 재무팀의 데이터 추출 AI입니다.
입력된 인보이스나 발주서 텍스트에서 정보를 추출하여 지정된 데이터 스키마에 완벽하게 일치하도록 반환하십시오.
정보가 누락된 경우 지어내지 말고 null 또는 0을 반환하십시오."""),
        ("user", "인보이스 원본 텍스트:\n{raw_text}")      
    ])

    chain = prompt | structured_llm

    try:
        # Pydantic 객체로 응답을 받음
        result: InvoiceSchema = chain.invoke({"raw_text": state.get("raw_text", "")})
        # 상태 딕셔너리에 저장하기 위해 dict 형태로 변환
        return {"parsed_data": result.model_dump(), "error": ""}
    except Exception as e:
        # 스키마 검증 실패 시 에러를 포착
        return {"error": f"데이터 추출 및 검증 실패: {str(e)}"}
    
# 그래프 조립 및 컴파일
workflow = StateGraph(DocumentState)

workflow.add_node("extract_invoice", extract_invoice_node)

workflow.add_edge(START, "extract_invoice")
workflow.add_edge("extract_invoice", END)

app_graph = workflow.compile()