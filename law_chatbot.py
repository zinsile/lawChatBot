import os
import streamlit as st
from langchain_community.retrievers import TavilySearchAPIRetriever
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema.output_parser import StrOutputParser
from openai import OpenAI
from langchain_openai import ChatOpenAI
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.schema import Document
from langchain.prompts import PromptTemplate


# ####################################################
# [ code 순서 ]                              
# 1. openai-api key
# 2. 챗봇 프롬프트, agent 정의
# 3. chatbot객체(streamlit) 생성 및 기능 구현
# 4. DB구축 및 pdf_rag_chain 생성
# 5. tavily검색하는 web_rag_chain 생성
# 6. 디비, 웹 검색 기능 추가
####################################################


################ 1. openai-api key #################
# ✅ OpenAI API Key 입력받기 (Streamlit Sidebar)
with st.sidebar:
    openai_api_key = st.text_input("🔑 OpenAI API Key", key="chatbot_api_key", type="password")
    st.markdown("[Get an OpenAI API key](https://platform.openai.com/account/api-keys)")

# OpenAI 클라이언트 연결
client = OpenAI(api_key=" [ your key ] ")
os.environ["TAVILY_API_KEY"] = " [ your key  "

st.title("🚀 사고닷 - 법률 상담 AI 챗봇")
st.caption("💬 법률 관련 질문을 입력하고 AI 변호사와 상담해보세요.")
####################################################

############# 2. 챗봇 프롬프트, agent 정의 ############
# ✅ 시스템 프롬프트 (단계별 상담 + 가이드라인 유지)
system_prompt = """
당신은 사고 관련 법률 정보를 제공하는 AI 법률 상담사입니다.
사용자가 사고와 관련된 법률적 도움을 요청할 때, 아래의 단계별 질문 프레임워크를 따라 포괄적인 질문에서 구체적인 질문으로 진행하며 정확한 법률 정보를 제공해야 합니다.

# 시스템 지침
1. 사용자의 첫 질문이나 문의를 들은 후, 단계별로 질문을 진행하세요.
2. 각 단계마다 답변을 듣고 그에 맞는 다음 단계의 질문을 선택하세요.
3. 사용자의 응답에 따라 관련 법률 정보와 조언을 제공하세요.
4. 모든 법률 정보는 정확하고 최신의 정보여야 합니다.
5. 전문적이지만 이해하기 쉬운 언어로 소통하세요.
6. 사용자가 추가 질문이나 명확한 설명을 요청할 경우, 즉시 응답하세요.
7. 법률적 조언이 필요한 경우 실제 변호사와 상담할 것을 권장하세요.
8. 사고닷에는 각 분야의 전문 변호사가 있어 언제든 법률상담을 받을 수 있다는 걸 알려주세요.

# 응답 가이드라인
1. 사용자의 응답이 불분명하거나 부족한 경우, 추가 질문을 통해 명확히 하세요.
2. 사용자가 질문 단계를 건너뛰거나 다른 주제로 전환하려 할 경우, 필요한 정보를 얻기 위해 질문을 다시 유도하세요.
3. 사용자가 특정 법률 용어나 절차에 대해 이해하지 못하는 경우, 이해하기 쉽게 설명해주세요.
4. 유사한 판례나 법률 조항을 인용할 때는 정확한 출처와 내용을 제공하세요.
5. 모든 정보와 조언은 객관적이고 사실에 기반해야 합니다.
6. 사용자의 감정적 상태를 고려하여 공감적인 태도를 유지하세요.
7. 사용자의 상황이 긴급하거나 심각한 경우, 적절한 긴급 조치나 전문가 상담을 권장하세요.
8. 변호사 매칭 서비스에서 사용자의 상황에 맞는 전문 변호사를 찾아보라고 권장하세요요.

# 질문 프로세스
1. Thought: 질문을 분석하여 어떤 정보를 더 수집해야 하는지 결정하세요.
2. Action: 필요한 정보를 얻기 위한 질문을 생성하세요.
3. 사용자 응답 후 다음 단계로 진행하세요.
"""

# ✅ Agent 클래스 정의
class Agent:
    def __init__(self, system_prompt=""):
        self.system_prompt = system_prompt
        self.messages = [{"role": "system", "content": system_prompt}]  # 초기 프롬프트 포함
        self.user_queries = []

    def __call__(self, message):
        """사용자의 입력을 받아 AI 응답을 생성"""
        self.messages.append({"role": "user", "content": message})
        self.user_queries.append(message)

        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        """AI에게 메시지를 보내고 응답을 받음"""
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=self.messages
        )
        return completion.choices[0].message.content

    def summarize_conversation(self):
        """사용자 상담 내용을 한 문장으로 요약"""
        summary_prompt = f"""
        다음 사용자의 질문을 한 문장으로 요약하세요: {self.user_queries}
        """
        print(self.user_queries)
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[{"role": "system", "content": "대화 내용을 한 문장으로 요약하는 역할을 수행합니다."},
                      {"role": "user", "content": summary_prompt}]
        )
        return completion.choices[0].message.content
####################################################

##### 3. chatbot객체(streamlit) 생성 및 기능 구현 #####
# ✅ 챗봇 인스턴스 저장 (세션 상태 관리)
if "chatbot" not in st.session_state:
    st.session_state["chatbot"] = Agent(system_prompt=system_prompt)

# ✅ 기존 대화 기록 관리
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "안녕하세요! 법률 상담이 필요하시면 질문해주세요."}]

# ✅ 기존 대화 UI 출력
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


# ✅ 사용자 입력 받기
if user_input := st.chat_input("질문을 입력하세요..."):
    if not openai_api_key:
        st.info("🔑 OpenAI API Key를 입력해주세요.")
        st.stop()

    client = OpenAI(api_key=openai_api_key)

    # 사용자 입력 저장
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # 챗봇 응답 생성
    chatbot_response = st.session_state["chatbot"](user_input)
    st.session_state.messages.append({"role": "assistant", "content": chatbot_response})
    st.chat_message("assistant").write(chatbot_response)
####################################################


########## 4. DB구축 및 pdf_rag_chain 생성 ##########
# 1. PDF에서 텍스트 추출 함수
def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)  # PDF 열기
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

# 2. 저장된 PDF 파일들 처리
pdf_folder = "pdf_files"
pdf_texts = {}

for pdf_file in os.listdir(pdf_folder):
    pdf_path = os.path.join(pdf_folder, pdf_file)
    text = extract_text_from_pdf(pdf_path)
    pdf_texts[pdf_file] = text
    print(f"텍스트 추출 완료: {pdf_file}")

# 3. ✅ Document 객체로 변환
documents = []
for pdf_file, text in pdf_texts.items():
    doc = Document(page_content=text, metadata={"source": pdf_file})  # ✅ page_content 필드 사용
    documents.append(doc)

# 4. 텍스트를 청크로 분할
chunk_size = 2000  # 청크 크기
chunk_overlap = 200  # 오버랩 크기
text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

chunks = text_splitter.split_documents(documents)
print(f"총 {len(chunks)}개의 청크 생성 완료")

# 5. 기존 ChromaDB 데이터 삭제 (옵션)
Chroma().delete_collection()

# 6. ChromaDB에 저장
db = Chroma.from_documents(
    documents=chunks,
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),  # 임베딩 모델 설정
    persist_directory="./chroma_Web",
    collection_metadata={"hnsw:space": "l2"}  # L2 거리 기반 검색
)

print("Chroma DB 저장 완료 ✅")

# 7. 검색 수행
retriever = db.as_retriever()

# 8. LLM 연결 및 요약 기능 추가
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)

# 검색 결과를 포맷팅하는 함수
def format_docs(docs):
    return "\n\n---\n\n".join([doc.page_content + f"\n출처: {doc.metadata['source']}" for doc in docs])

# 프롬프트 설정
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
        Answer the question based only on the following context:
        {context}
        Question: {question}

        사용자에게 얻은 정보에 따라 웹을 검색하고, 검색된 사건 관련 법률 정보와 사례를 아래 형식에 맞게 정리하여 답변을 생성해주세요.
        <법률 정보>

        법률 제목: 절도에 관한 형법
        법률 조항: "타인의 재산을 불법적으로 취득한 경우, 절도로 간주되어 형사 처벌을 받을 수 있습니다."
        법률 요약: 절도는 타인의 재산을 불법적으로 취득하는 행위로, 이 법은 절도의 정의 및 처벌 내용을 명시하고 있습니다.
        법률 제목: 형법 제329조 (절도)
        법률 조항: "절도의 경우, 피해 금액에 따라 처벌이 달라지며, 피해자가 10만원 이상을 잃은 경우 형사 처벌을 받게 됩니다."
        법률 요약: 이 법은 절도의 처벌 기준을 정하며, 금액에 따라 다르게 처벌됩니다. 특히, 절도 금액이 10만원 이상일 경우, 형사 처벌이 부과됩니다.
        """
)

# RAG 체인 구성
pdf_rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
####################################################


######## 5. tavily검색하는 web_rag_chain 생성 ########

# ✅ Tavily 검색 연동 (법률 사례 검색)
def format_docs(docs):
    """Tavily 검색 결과를 정리하는 함수"""
    formatted_docs = ""
    for d in docs:
        # d.page_content는 텍스트 내용, d.metadata에 URL이 포함되어 있을 수 있습니다.
        formatted_docs += f"Content: {d.page_content}\n"  # 문서 내용
        if hasattr(d, 'metadata') and 'source' in d.metadata:
            formatted_docs += f"URL: {d.metadata['source']}\n"  # 문서 URL
        formatted_docs += "\n"  # 항목 간 구분
    return formatted_docs


# ✅ Tavily 검색 설정
template = """Answer the question based only on the following context:

{context}

Question: {question}

사용자에게 얻은 정보에 따라 웹을 검색하고, 검색된 사건 관련 사례를 아래 형식에 맞게 정리하여 답변을 생성해주세요.
<관련 사례>
사례 제목: 서울 절도 사건 배상 책임 사례
사례 요약: "2020년에 발생한 서울의 한 절도 사건에서, 피고인은 50만원 규모의 절도로 유죄 판결을 받았으며, 금전적 배상 및 징역형을 선고받았습니다."
링크: 외부로부터 받아오는 문서의 'URL' 정보를 링크로 달아주세요.
사례 제목: 절도 사건의 판결: 피해자 배상 사례
사례 요약: "2019년 발생한 절도 사건에서, 피해자는 가해자에게 법적 배상을 청구했습니다. 법원은 피해 금액을 기준으로 배상액을 산정하며, 피해자가 입은 피해를 보상받게 했습니다."
링크: 외부로부터 받아오는 문서의 'URL' 정보를 링크로 달아주세요.
사례 제목: 절도 사건의 합의 판결 사례
사례 요약: "2021년에 발생한 절도 사건에서, 피해자는 가해자와 합의를 통해 금전적 배상금을 받기로 했으며, 법원은 그 합의를 인정하여 사건을 종결했습니다."
링크: 외부로부터 받아오는 문서의 'URL' 정보를 링크로 달아주세요.
<예상 결과>
승률: "절도 사건의 승률은 피해 금액과 증거에 따라 다르며, 현 상황에서는 50만원 규모의 절도로 유죄 판결을 받을 것으로 예상됩니다.."
형량: "형량은 범죄의 심각성과 피해 금액에 따라 다르며, 일반적으로 금전적 배상과 함께 형사 처벌이 부과됩니다."
소요 기간: "절도 사건의 경우 보통 3개월에서 6개월 정도 소요될 수 있으며, 피해자가 법적 배상을 청구한 경우 기간이 더 길어질 수 있습니다.">
"""
prompt_template = ChatPromptTemplate.from_template(template)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
retriever = TavilySearchAPIRetriever(k=3, search_depth="advanced", include_domains=["news"])

web_rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt_template
    | llm
)
####################################################


############ 6. 디비, 웹 검색 기능 추가 ###############

# ✅ 챗봇 대화가 종료된 후 Tavily 검색 수행
if st.button("🔎 관련사례 및 예상결과"):
    summary = st.session_state["chatbot"].summarize_conversation()
    search_result = web_rag_chain.invoke(f"{summary} 관련된 형량이나 벌금 정보")

    st.subheader("🔍 검색된 관련사례 및 예상결과")
    st.write(search_result.content)


# ✅ 챗봇 대화가 종료된 후 Tavily 검색 수행
if st.button("🔎 관련 법률정보"):
    summary = st.session_state["chatbot"].summarize_conversation()
    search_result = pdf_rag_chain.invoke(f"{summary} 관련된 법률 정보")

    st.subheader("🔍 검색된 법률정보")
    st.write(search_result.content)