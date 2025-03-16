import base64
import streamlit as st

# CSS 스타일
def load_css():
    st.markdown("""
    <style>
        .container-card {
            background-color: white;
            border-radius: 10px;
            padding: rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
        }
        
        .modal-title {
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        .lawyer-card {
            border-radius: 10px;
            border: 1px solid #E5E7EB;
            padding: 1rem;
            background-color: white;
            transition: all 0.3s;
            height: 100%;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
            align-items: center;  /* 가로 중앙 정렬 */
            justify-content: center; /* 세로 중앙 정렬 */
            text-align: center; /* 텍스트 중앙 정렬 */
        }
        
        .lawyer-card:hover {
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            transform: translateY(-5px);
        }
        
        .selected {
            border: 3px solid #e77d2f;
            box-shadow: 0 10px 15px -3px rgba(30, 58, 138, 0.3);
        }
        
        .lawyer-name {
            font-size: 1.2rem;
            font-weight: bold;
            margin-top: 0.5rem;
            color: #1E3A8A;
        }
        
        .lawyer-specialty {
            color: #4B5563;
            font-weight: 500;
        }
        
        .lawyer-description {
            margin-top: 0.5rem;
            font-size: 0.9rem;
            color: #6B7280;
        }
        
        .lawyer-stats {
            display: flex;
            justify-content: space-between;
            margin-top: 1rem;
            color: #4B5563;
            font-size: 0.8rem;
        }
        
        .select-button {
            background-color: #1E3A8A;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            cursor: pointer;
            width: 100%;
            margin-top: 1rem;
            font-weight: bold;
        }
        
        .select-button:hover {
            background-color: #1E40AF;
        }
        
        .action-buttons {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-top: 2rem;
        }
        
        .profile-img {
            border-radius: 50%;
            object-fit: cover;
        }
    </style>
    """, unsafe_allow_html=True)

# 변호사 데이터
def get_lawyers():
    return [
        {
            "id": 1,
            "name": "손지영",
            "specialty": "이혼 • 가사",
            "description": "10년 경력의 이혼 전문 변호사로, 재산분할, 양육권 관련 사건을 다수 담당했습니다.",
            "cases": 250,
            "rating": 4.8,
            "image": "rawChatBot\images\lawyer1.png"
        },
        {
            "id": 2,
            "name": "김민주",
            "specialty": "형사 • 범죄",
            "description": "전직 검사 출신으로 형사사건에 대한 깊은 이해와 경험을 바탕으로 최선의 변호를 약속합니다.",
            "cases": 310,
            "rating": 4.7,
            "image": "rawChatBot\images\lawyer1.png"
        },
        {
            "id": 3,
            "name": "이재웅",
            "specialty": "부동산 • 임대차",
            "description": "부동산 계약 및 분쟁 전문 변호사로 임대차보호법에 대한 전문 지식을 보유하고 있습니다.",
            "cases": 180,
            "rating": 4.9,
            "image": "rawChatBot\images\lawyer1.png"
        },
        {
            "id": 4,
            "name": "김다은",
            "specialty": "상속 • 증여",
            "description": "상속 관련 복잡한 법률 문제를 쉽게 풀어드리는 맞춤형 법률 서비스를 제공합니다.",
            "cases": 150,
            "rating": 4.6,
            "image": "./images/lawyer1.png"
        },
        {
            "id": 5,
            "name": "진실",
            "specialty": "노동 • 산재",
            "description": "근로자의 권익 보호를 위해 노력하는 노동법 전문 변호사입니다. 부당해고, 산재보상 등을 담당합니다.",
            "cases": 220,
            "rating": 4.9,
            "image":"rawChatBot/images/lawyer1.png"
        },
        {
            "id": 6,
            "name": "이효정",
            "specialty": "기업 • 계약",
            "description": "기업 법무 15년 경력으로 계약서 검토부터 기업 분쟁까지 모든 법률 문제를 해결해 드립니다.",
            "cases": 280,
            "rating": 4.7,
            "image": "images/lawyer1.png"
        }
    ]

# 세션 상태 초기화 함수
def init_session_state():
    if 'selected_lawyer' not in st.session_state:
        st.session_state.selected_lawyer = None

# 변호사 선택 함수
def select_lawyer(lawyer_id):
    st.session_state.selected_lawyer = lawyer_id
    
# 변호사 선택 확정 함수
def confirm_selection():
    if st.session_state.selected_lawyer:
        st.session_state.confirmed_lawyer = next((l for l in get_lawyers() if l["id"] == st.session_state.selected_lawyer), None)
        st.session_state.show_modal = False
        st.session_state.selected_lawyer = None

# 모달 닫기 함수
def close_modal():
    st.session_state.show_modal = False
    st.session_state.selected_lawyer = None

def get_base64_image(image_path):
    """이미지를 Base64로 변환"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
    
# 변호사 선택 화면 표시 함수
def show_lawyer_selection_modal():

    # 세션 상태 초기화
    init_session_state()
    
    # CSS 로드
    load_css()
    
    # 변호사 선택 카드 컨테이너
    st.markdown("<h2 class='modal-title'>원하시는 변호사를 선택해 주세요!</h2>", unsafe_allow_html=True)
    
    # 변호사 카드 표시
    lawyers = get_lawyers()
    cols = st.columns(3)
    for i, lawyer in enumerate(lawyers):
        with cols[i % 3]:
            # 선택된 변호사 스타일 적용
            card_class = "lawyer-card"
            if st.session_state.selected_lawyer == lawyer["id"]:
                card_class += " selected"

            local_image_path = "rawChatBot/images/lawyer1.png"  # 같은 디렉토리에 있는 경우
            image_base64 = get_base64_image(local_image_path)

            st.markdown(f"""
        <div class='{card_class}'>
            <img src="data:image/png;base64,{image_base64}" width=150 alt="변호사 사진">
            <div class='lawyer-name'>{lawyer['name']} 변호사</div>
            <div class='lawyer-specialty'>{lawyer['specialty']}</div>
            <div class='lawyer-description'>{lawyer['description']}</div>
            <div class='lawyer-stats'>
                <span>담당 사건 {lawyer['cases']}건</span>
                <span>평점 {lawyer['rating']}/5.0</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
                
            if st.button("선택", key=f"select_{lawyer['id']}", use_container_width=True):
                select_lawyer(lawyer["id"])
    
    # 확인/취소 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button("선택 완료", key="confirm_btn", type="primary", use_container_width=True):
            confirm_selection()
    with col2:
        if st.button("취소", key="cancel_btn", use_container_width=True):
            close_modal()
    
    st.markdown("</div>", unsafe_allow_html=True)

# 이 모듈을 직접 실행했을 때의 테스트 코드
if __name__ == "__main__":
    st.set_page_config(page_title="변호사 선택 테스트", layout="wide")
    show_lawyer_selection_modal()