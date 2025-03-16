import streamlit as st
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser

# 프롬프트 템플릿 가져오기
from prompts import question_generation_prompt, re_write_prompt, report_prompt

# 법률 카테고리 데이터 가져오기
from legal_categories import categories

# 상수 정의
INITIAL_MESSAGE = "법률 사건의 정확한 이해를 돕기 위해 상담을 진행합니다."
MODEL = "gpt-4o-mini"  
TEMPERATURE = 0.2
API_KEY = ""


# 초기 세션 상태 설정 함수
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": INITIAL_MESSAGE}]
    
    # 딕셔너리로 초기화를 간소화
    initial_states = {
        "current_step": "initial",
        "legal_specification": "",
        "additional_questions": "",  # 리스트 대신 문자열로 저장
        "additional_responses": "",
        "extra_information": "",
        "final_report": "",
        # 카테고리 관련 상태 변수 추가
        "current_category": None,
        "category_selected": False,
        "current_question": 0,
        "user_answers": {},
        "show_questions": True,
        "questionnaire_completed": False
    }
    
    for key, value in initial_states.items():
        if key not in st.session_state:
            st.session_state[key] = value


# 메시지 추가 함수
def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})
    st.chat_message(role).write(content)


# LLM 인스턴스 생성 함수
def create_llm():
    return ChatOpenAI(api_key=API_KEY, model=MODEL, temperature=TEMPERATURE)


# 추가 질문 생성 함수
def generate_questions(llm, specification):
    chain = question_generation_prompt | llm | StrOutputParser()
    return chain.invoke({"specification": specification})


# 질문 개선 함수
def improve_questions(llm, questions_text):
    question_rewriter = re_write_prompt | llm | StrOutputParser()
    return question_rewriter.invoke({"question": questions_text})


# 법률 보고서 생성 함수
def generate_legal_report(llm, legal_specification, additional_responses, extra_information):
    chain = report_prompt | llm | StrOutputParser()
    return chain.invoke({
        "legal_specification": legal_specification,
        "additional_responses": additional_responses,
        "extra_information": extra_information
    })


# 법률 명세서 생성 함수 (설문지 응답 기반)
def generate_legal_specification():
    category = st.session_state.current_category
    specification = f"법률 카테고리: {category}\n\n"
    
    for question, answers in st.session_state.user_answers.items():
        if isinstance(answers, list):
            specification += f"- {question}: {', '.join(answers)}\n"
        else:
            specification += f"- {question}: {answers}\n"
    
    return specification


# 이전 메시지 표시
def display_chat_history():
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])


# 법률 카테고리 선택 함수
def show_category_selection():
    st.write("상담 카테고리를 선택해주세요.")
    cols = st.columns(2)
    
    categories_options = [
        {"name": "교통사고", "col": 0},
        {"name": "폭행/상해", "col": 0},
        {"name": "사기", "col": 1},
        {"name": "이혼", "col": 1}
    ]
    
    # 더 간결한 카테고리 버튼 생성
    for category in categories_options:
        with cols[category["col"]]:
            if st.button(category["name"], use_container_width=True):
                st.session_state.current_category = category["name"]
                st.session_state.category_selected = True
                st.session_state.current_question = 0
                st.session_state.user_answers = {}
                st.rerun()




# 질문 표시 및 응답 수집 함수
def show_question():
    if st.session_state.current_category and st.session_state.current_question < len(categories[st.session_state.current_category]):
        current_q = categories[st.session_state.current_category][st.session_state.current_question]
        total_questions = len(categories[st.session_state.current_category])

        # 질문 내용 표시
        st.write(f"{current_q['question']} ({st.session_state.current_question + 1}/{total_questions})")

        # 라디오 버튼 (단일 선택)
        if current_q['type'] == 'radio':
            selected_option = st.radio("선택하세요:", current_q['options'], key=f"radio_{st.session_state.current_question}")
            
            if st.button("다음", key=f"next_{st.session_state.current_question}"):
                # 응답 저장
                st.session_state.user_answers[current_q['question']] = selected_option
                
                # 다음 질문으로 이동
                st.session_state.current_question += 1
                
                # 모든 질문이 끝났을 때 다음 단계로 진행
                if st.session_state.current_question >= len(categories[st.session_state.current_category]):
                    # 설문지 완료 표시
                    st.session_state.questionnaire_completed = True
                    # 법률 명세서 생성
                    st.session_state.legal_specification = generate_legal_specification()
                    # 추가 정보 요청 단계로 전환
                    handle_questionnaire_completion()
                
                st.rerun()

        # 체크박스 (다중 선택)
        elif current_q['type'] == 'checkbox':
            selected_options = []
            for option in current_q['options']:
                if st.checkbox(option, key=f"checkbox_{st.session_state.current_question}_{option}"):
                    selected_options.append(option)
            
            if st.button("다음", key=f"next_{st.session_state.current_question}"):
                if selected_options:
                    # 응답 저장
                    st.session_state.user_answers[current_q['question']] = selected_options
                    
                    # 다음 질문으로 이동
                    st.session_state.current_question += 1
                    
                    # 모든 질문이 끝났을 때 다음 단계로 진행
                    if st.session_state.current_question >= len(categories[st.session_state.current_category]):
                        # 설문지 완료 표시
                        st.session_state.questionnaire_completed = True
                        # 법률 명세서 생성
                        st.session_state.legal_specification = generate_legal_specification()
                        # 추가 정보 요청 단계로 전환
                        handle_questionnaire_completion()
                    
                    st.rerun()
                else:
                    st.warning("최소 하나 이상의 옵션을 선택해주세요.")


# 설문지 완료 후 처리 함수
def handle_questionnaire_completion():
    try:
        # 먼저 사용자에게 법률 명세서 요약 표시
        legal_spec = st.session_state.legal_specification
        summary_message = f"작성하신 {st.session_state.current_category} 사건 명세서의 내용은 다음과 같습니다:\n\n"
        # summary_message += "입력하신 내용은 다음과 같습니다:\n\n"
        
        # 응답을 정리해서 표시
        for question, answers in st.session_state.user_answers.items():
            if isinstance(answers, list):
                summary_message += f"• {question}: {', '.join(answers)}\n\n"
            else:
                summary_message += f"• {question}: {answers}\n\n"
        
        # 사용자에게 법률 명세서 요약 표시
        add_message("user", summary_message)

        
        # 로딩 스피너 표시
        with st.spinner('법률 명세서를 분석하고 추가 질문을 생성 중입니다...'):
            # LLM 인스턴스 생성
            llm = create_llm()
            
            # 추가 질문 생성
            generated_questions = generate_questions(llm, legal_spec)
            
            # 생성된 질문 개선
            improved_questions = improve_questions(llm, generated_questions)
            
            # 개선된 질문 저장 (문자열 형태)
            st.session_state.additional_questions = improved_questions
        
        # 어시스턴트 응답 표시
        response_text = f"입력하신 내용을 바탕으로 분석했습니다. 추가 정보를 위해 다음 질문에 답변해주세요:\n\n{improved_questions}\n\n답변 가능한 선에서 최대한 구체적으로 작성해주세요."
        
        add_message("assistant", response_text)
        
        # 다음 단계로 이동
        st.session_state.current_step = "answering_questions"
        st.session_state.show_questions = False
        
    except Exception as e:
        st.error(f"법률 명세서 분석 중 오류가 발생했습니다: {str(e)}")
        add_message("assistant", f"오류가 발생했습니다. 다시 시도해주세요.")


# 사용자 입력 처리 함수
def handle_user_input(prompt):
    # 사용자 메시지 표시
    add_message("user", prompt)
    
    # 현재 단계에 따른 처리
    if st.session_state.current_step == "answering_questions":
        handle_answering_questions_step(prompt)
    elif st.session_state.current_step == "extra_information":
        handle_extra_information_step(prompt)
    else:  # completed 또는 기타 상태
        handle_completed_step(prompt)


# 질문 답변 단계 처리 함수
def handle_answering_questions_step(prompt):
    # 추가 질문에 대한 답변 처리
    st.session_state.additional_responses = prompt
    
    # 추가 정보 요청
    response_text = "추가 질문에 답변해주셔서 감사합니다. 추가로 알려주실 정보가 있으시면 입력해주세요. \n\n없으시면 '없음'이라고 입력해주세요."
    add_message("assistant", response_text)
    
    # 다음 단계로 이동
    st.session_state.current_step = "extra_information"


# 추가 정보 단계 처리 함수
def handle_extra_information_step(prompt):
    # 추가 정보 처리
    st.session_state.extra_information = prompt if prompt.lower() != "없음" else ""
    
    # 최종 보고서 생성
    try:
        # 로딩 스피너 표시
        with st.spinner(' 법률 보고서를 생성 중입니다. 잠시만 기다려주세요...'):
            llm = create_llm()
            
            final_report = generate_legal_report(
                llm,
                st.session_state.legal_specification,
                st.session_state.additional_responses,
                st.session_state.extra_information
            )
            
            # 최종 보고서 저장
            st.session_state.final_report = final_report
        
        # 어시스턴트 응답 표시
        response_text = "법률 보고서가 생성되었습니다:\n\n" + final_report
        add_message("assistant", response_text)
        
        # 마무리 메시지
        completion_text = "보고서 생성이 완료되었습니다. 곧 변호사 매칭이 이루어질 예정입니다. 추가 질문이 있으시면 말씀해주세요."
        add_message("assistant", completion_text)
        
        # 다음 단계로 이동
        st.session_state.current_step = "completed"


        st.download_button(
            label="📄 보고서 다운로드 (TXT)",
            data=st.session_state["final_report"],
            file_name="AI법률_자문_보고서.txt",
            mime="text/plain"
        )
        

        
    except Exception as e:
        error_message = f"보고서 생성 중 오류가 발생했습니다: {str(e)}"
        st.error(error_message)
        add_message("assistant", f"보고서 생성 중 오류가 발생했습니다. 다시 시도해주세요.")


# 완료 단계 처리 함수
def handle_completed_step(prompt):
    # 일반 대화 처리
    try:
        # 로딩 스피너 표시
        with st.spinner('답변을 생성 중입니다...'):
            client = OpenAI(api_key=API_KEY)
            response = client.chat.completions.create(
                model=MODEL,  # gpt-4o-mini 모델 사용
                messages=[
                    {"role": "system", "content": "You are a helpful legal assistant that has already generated a report. Answer any additional questions the user might have."},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ]
            )
            msg = response.choices[0].message.content
        
        add_message("assistant", msg)
    except Exception as e:
        error_message = f"답변 생성 중 오류가 발생했습니다: {str(e)}"
        st.error(error_message)
        add_message("assistant", "답변 생성 중 오류가 발생했습니다. 다시 시도해주세요.")


# 세션 상태 초기화 함수
def reset_session_state():
    # 초기화할 키 목록
    keys_to_reset = [
        "messages", "current_step", "legal_specification", 
        "additional_questions", "additional_responses", 
        "extra_information", "final_report",
        "current_category", "category_selected", "current_question",
        "user_answers", "show_questions", "questionnaire_completed"
    ]
    
    # 세션 상태 초기화
    for key in keys_to_reset:
        if key in st.session_state:
            if key == "messages":
                st.session_state[key] = [{"role": "assistant", "content": INITIAL_MESSAGE}]
            elif key == "current_step":
                st.session_state[key] = "initial"
            elif key == "current_category":
                st.session_state[key] = None
            elif key == "category_selected":
                st.session_state[key] = False
            elif key == "current_question":
                st.session_state[key] = 0
            elif key == "user_answers":
                st.session_state[key] = {}
            elif key == "show_questions":
                st.session_state[key] = True
            elif key == "questionnaire_completed":
                st.session_state[key] = False
            else:
                st.session_state[key] = ""
    st.rerun()


# 특정 단계가 완료되었는지 확인하는 함수

def steps_completed(current_step, step_key):
    step_order = {
        "initial": 0,
        "category_selection": 1,
        "questionnaire": 2,
        "answering_questions": 3,
        "extra_information": 4,
        "completed": 5
    }
    
    # 현재 상태를 평가하기 위한 현재 단계 결정
    current_status = current_step
    
    # 카테고리가 선택되었으면 category_selection 단계는 완료된 것으로 간주
    if step_key == "category_selection" and st.session_state.category_selected:
        return True
    
    # 설문지가 완료되었으면 questionnaire 단계는 완료된 것으로 간주
    if step_key == "questionnaire" and st.session_state.questionnaire_completed:
        return True
    
    # 현재 단계가 해당 단계보다 뒤에 있으면 완료된 것으로 간주
    return step_order.get(current_status, 0) > step_order.get(step_key, 0)


# 진행 상태 바의 값을 계산하는 함수 (0.0 ~ 1.0)
def get_progress_value(current_step):
    # 기본 진행 값
    progress_values = {
        "initial": 0.0,
        "category_selection": 0.1,
        "questionnaire": 0.4,
        "answering_questions": 0.6,
        "extra_information": 0.8,
        "completed": 1.0
    }
    
    # 현재 상태를 평가하기 위한 현재 단계 결정
    if current_step == "initial" and st.session_state.category_selected:
        current_status = "category_selection"
    elif current_step == "initial" and st.session_state.questionnaire_completed:
        current_status = "questionnaire"
    else:
        current_status = current_step
    
    # 설문지 진행 중인 경우 진행률 계산
    if current_status == "category_selection" and st.session_state.current_category:
        total_questions = len(categories.get(st.session_state.current_category, []))
        if total_questions > 0:
            questionnaire_progress = st.session_state.current_question / total_questions
            return progress_values["category_selection"] + questionnaire_progress * (progress_values["questionnaire"] - progress_values["category_selection"])
    
    return progress_values.get(current_status, 0.0)


# 사이드바 상태 표시 함수
def display_sidebar_status():
    with st.sidebar:
        st.subheader("진행 상태")
        
        # 모든 단계 정의
        steps = [
            {"key": "category_selection", "name": "법률 카테고리 선택"},
            {"key": "questionnaire", "name": "사건 명세서 작성"},
            {"key": "answering_questions", "name": "추가 질문 답변"},
            {"key": "extra_information", "name": "추가 정보 입력"},
            {"key": "completed", "name": "법률 자문 보고서 생성"}
        ]
        
        current_step = st.session_state["current_step"]

        # 진행 상태 바
        progress_value = get_progress_value(current_step)
        st.progress(progress_value)
        
        # 현재 선택된 카테고리 표시
        if st.session_state.current_category:
            st.info(f"선택한 법률 분야: {st.session_state.current_category}")


        # 상태에 따른 이모지 및 스타일 정의
        for step in steps:
            if steps_completed(current_step, step["key"]):
                # 완료된 단계 - 체크 표시와 함께 녹색으로 표시
                st.markdown(f"✅  **{step['name']}**")
            elif (current_step == "initial" and step["key"] == "category_selection" and st.session_state.category_selected) or \
                 (current_step == "initial" and step["key"] == "questionnaire" and not st.session_state.questionnaire_completed and st.session_state.category_selected) or \
                 (current_step == step["key"]):
                # 현재 진행 중인 단계 - 진행 중 표시와 함께 파란색으로 표시
                st.markdown(f"🔄  **{step['name']}**")
            else:
                # 아직 진행하지 않은 단계 - 회색으로 표시
                st.markdown(f"⬜  {step['name']}")


        # 보고서 다운로드 버튼 (보고서 생성이 완료된 경우에만)
        if current_step == "completed" and st.session_state["final_report"]:
            st.markdown("---")
            st.subheader("보고서 다운로드")
            st.download_button(
                label="📄 보고서 다운로드 (TXT)",
                data=st.session_state["final_report"],
                file_name="legal_report.txt",
                mime="text/plain"
            )
        
        # 처음부터 다시 시작하는 버튼
        st.markdown("---")
        if st.button("새 대화 시작"):
            reset_session_state()


# 메인 애플리케이션 실행 함수
def main():
    # 페이지 타이틀과 설명 설정
    st.title("💬 AI 법률 자문 보고서 생성")
    st.caption("👩🏻‍💼 법률 보고서 생성 후 변호사 매칭이 이루어집니다")
    
    # 세션 상태 초기화
    initialize_session_state()
    
    # 메시지 히스토리 표시
    display_chat_history()
    
    # 현재 단계에 따른 인터페이스 표시
    if st.session_state.show_questions:
        if not st.session_state.category_selected:
            show_category_selection()
        else:
            show_question()
    else:
        # 사용자 입력 처리
        if prompt := st.chat_input():
            handle_user_input(prompt)
    
    # 사이드바에 현재 상태 표시
    display_sidebar_status()


# 애플리케이션 시작
if __name__ == "__main__":
    main()

