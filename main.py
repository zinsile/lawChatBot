import streamlit as st
import base64
from PIL import Image
import os
import time
from datetime import datetime
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="AI 법률 서비스 '사고닷'",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 이미지를 base64로 인코딩하는 함수
def get_image_as_base64(file_path):
    try:
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

# CSS 스타일 적용
def local_css():
    st.markdown("""
    <style>
        /* 전체 폰트 및 색상 스타일 */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
        
        * {
            font-family: 'Noto Sans KR', sans-serif;
        }
        
        /* 헤더 스타일 */
        .main-header {
            background-color: #3d6aff;
            padding: 1.5rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: none; 
        }
        
        /* 카드 스타일 */
        .service-card {
            background-color: white;
            border-radius: 10px;
            padding: 2rem;
            padding-left: 2.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            height: 100%;
            transition: transform 0.3s;
            cursor: pointer;
        }
        
        .service-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        .card-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            color: #3d6aff;
        }
        
        .card-title {
            font-size: 1.3rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
            color: #3d6aff;
        }
        
        .card-description {
            color: #4B5563;
            font-size: 0.9rem;
        }
        
        /* 푸터 스타일 */
        .footer {
            text-align: center;
            padding: 1rem;
            font-size: 0.8rem;
            color: #6B7280;
            margin-top: 2rem;
        }
        
        /* 배경색 변경 */
        .stApp {
            background-color: #F8FAFC;
        }

        /* 사이드바 스타일 */
        .css-1d391kg {
            background-color: #F1F5F9;
        }
        
        /* 버튼 스타일 */
        .stButton>button {
            background-color: white;
            border-radius: 10px;
            border: none;
            font-weight: 500;
            border-radius: 5px;
            width: 100%;
            margin-bottom: 3px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s;
            cursor: pointer;
            padding: 0.8em;
        }
        
        .stButton>button:hover {
            background-color: #3d6aff;
            color: white;
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
                
        
        /* 프로필 카드 스타일 */
        .profile-card {
            background-color: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            text-align: center;
            height: 100%;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        .profile-image {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            margin: 0 auto 10px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #F1F5F9;
            overflow: hidden;
        }
        
        .profile-name {
            font-size: 1.4rem;
            font-weight: 500;
            color: #374151;
            margin-bottom: 8px;
            text-align: center;
        }
        
        .profile-desc {
            color: #4B5563;
            font-size: 0.9rem;
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

local_css()

# 사이드바
with st.sidebar:
    st.image("images/저울.webp", width=100)
    st.title("AI 법률 서비스 사고닷")
    st.markdown('<p>AI와 법률 전문가가 함께하는 스마트 법률 서비스.<br>승리를 만드는 길, 사고닷과 함께 준비하세요.</p>', unsafe_allow_html=True)
    
    
    st.divider()
    
    # 메뉴란 대신 버튼으로 대체
    st.subheader("소개합니다")
    show_services = st.button("👩🏻‍⚖️ 우리 서비스 소개")
    show_team = st.button("☀️ 우리 팀 소개")
    show_home = st.button("🏠 홈 돌아가기")
    
    st.divider()
    
    # 연락처 정보
    st.caption("고객센터: 02-1004-1004")
    st.caption("이메일: happy6team@skala.com")
    st.caption("운영시간: 연중무휴 24시간!")

# 세션 상태로 현재 페이지 관리
if 'current_page' not in st.session_state:
    st.session_state.current_page = "홈"

# 버튼 클릭에 따라 페이지 상태 변경
if show_home:
    st.session_state.current_page = "홈"
if show_team:
    st.session_state.current_page = "우리 팀 소개"
if show_services:
    st.session_state.current_page = "우리 서비스 소개"

# 홈 화면
if st.session_state.current_page == "홈":
    st.markdown("<div class='main-header'><h1>🚀 사고닷 🚀</h1><p>실시간 AI 상담부터 맞춤형 법률 보고서<br>변호사 연결까지, 사고닷에서 법률 고민 끝!</p></div>", unsafe_allow_html=True)

    # 서비스 소개
    st.markdown("### 주요 서비스")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='service-card' onclick="window.location.href='#'">
            <div class='card-icon'>💬</div>
            <div class='card-title'>실시간 AI 법률 상담</div>
            <div class='card-description'>
                AI 법률 비서가 실시간으로 법률 상담을 제공합니다.<br>
                간단한 법률 질문부터 검색까지 신속하게 답변해 드립니다.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='service-card' onclick="window.location.href='#'">
            <div class='card-icon'>📝</div>
            <div class='card-title'>AI 법률 자문 보고서 생성</div>
            <div class='card-description'>
                케이스에 맞는 맞춤형 법률 자문 보고서를 생성합니다.<br>이를 바탕으로 국내 최고의 변호사들과 바로 연결됩니다. 
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='service-card' onclick="window.location.href='#'">
            <div class='card-icon'>📋</div>
            <div class='card-title'>방명록</div>
            <div class='card-description'>
                서비스에 대해 자유롭게 의견을 남길 수 있는 공간입니다.<br>방명록을 작성하거나 좋아요를 눌러보세요!
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 변호사 소개
    st.markdown("### 국내 Top 변호사 소개")
    
    # 변호사 정보와 이미지 정의
    lawyers = [
        {"name": "손지영", "specialty": "• 서울대학교 법학과 졸업 ㅋ<br>안녕", "image": "images/손지영.png"},
        {"name": "김민주", "specialty": "상법 전문", "image": "images/김민주.png"},
        {"name": "김다은", "specialty": "특허법 전문", "image": "images/김다은.png"},
        {"name": "이재웅", "specialty": '“자신이 없습니다. 질 자신이.<br>가장 확실한 해결책, 포기 없는 변호.”<br><br>• 성격 : INFJ (근데 사실 T임)<br><br>• 한국대학교 법합전문대학학원<br>(법학스칼라전문박사, 박사 졸업, 2018)<br>• 너뭐대학교<br>(한국사, 문학과, 수석 졸업, 2015)<br>• 사고닷 법률 사무소 (2016 - 현재)', "image": "images/이재웅.png"},
        {"name": "진실", "specialty": '"믿음, 소망, 사랑, 그중에 제일은 사랑이라.<br>이혼 전문 맡겨만 주세요.”<br><br>• 성격: ISFP (공감 잘함. 의뢰인과 울음 대결 가능)<br><br>• 제9회 변호사시험 합격 (2020)<br>• 한국대학교 법학전문대학원<br>(법학스칼라전문석사, 수석졸업, 2020)<br>• 두번 다시 사랑모대학교<br>(문학사, 서양사학, 수석졸업, 2017)<br>• 사고닷 법률사무소 (2020-현재)', "image": "images/진실.png"},
        {"name": "이효정", "specialty": '"오직 노동자만을 위한<br>노동자의, 노동자에 의한, 노동자를 위한 법률 서비스"<br><br>• 성격: INTJ (노동자에게만 F)<br><br>• 한국대학교(법학, 2020)<br>• 한국대학교 법학전문대학원(법학전문석사, 2023)<br>• 한국노동교육원 법률 자문(2023 - 현재)<br>• 사고닷 법률 사무소(2024 - 현재)', "image": "images/이효정.png"}
    ]
    
    # 2행 3열로 변경
    # 첫 번째 행 (변호사 0, 1, 2)
    row1_cols = st.columns(3)
    
    for i in range(3):
        lawyer = lawyers[i]
        img_path = lawyer["image"]
        img_base64 = get_image_as_base64(img_path)
        
        if img_base64:
            img_html = f'<img src="data:image/jpeg;base64,{img_base64}" style="width:100%; height:100%; object-fit:cover;">'
        else:
            # 이미지가 없을 경우 기본 아이콘 사용
            gender_icon = "👩‍⚖️" if lawyer["name"] not in ["이재웅"] else "👨‍⚖️"
            img_html = f'<span style="font-size: 30px;">{gender_icon}</span>'
        
        profile_html = f"""
        <div class="profile-card">
            <div class="profile-image">
                {img_html}
            </div>
            <div class="profile-name">{lawyer["name"]}</div>
            <div class="profile-desc">{lawyer["specialty"]}</div>
        </div>
        """
        
        with row1_cols[i]:
            st.markdown(profile_html, unsafe_allow_html=True)
    
    # 첫 번째 행과 두 번째 행 사이의 간격 추가
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
    # 두 번째 행 (변호사 3, 4, 5)
    row2_cols = st.columns(3)
    
    for i in range(3, 6):
        lawyer = lawyers[i]
        img_path = lawyer["image"]
        img_base64 = get_image_as_base64(img_path)
        
        if img_base64:
            img_html = f'<img src="data:image/jpeg;base64,{img_base64}" style="width:100%; height:100%; object-fit:cover;">'
        else:
            # 이미지가 없을 경우 기본 아이콘 사용
            gender_icon = "👩‍⚖️" if lawyer["name"] not in ["이재웅"] else "👨‍⚖️"
            img_html = f'<span style="font-size: 30px;">{gender_icon}</span>'
        
        profile_html = f"""
        <div class="profile-card">
            <div class="profile-image">
                {img_html}
            </div>
            <div class="profile-name">{lawyer["name"]}</div>
            <div class="profile-desc">{lawyer["specialty"]}</div>
        </div>
        """
        
        with row2_cols[i-3]:
            st.markdown(profile_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 통계 섹션
    st.markdown("### 서비스 통계")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="누적 상담 건수", value="12,450건", delta="증가 추세")
    
    with col2:
        st.metric(label="월간 활성 사용자", value="3,200명", delta="15% 증가")
    
    with col3:
        st.metric(label="사용자 만족도", value="4.8/5.0", delta="0.2 상승")
    
    # 푸터
    st.markdown("<div class='footer'>© 2025 AI 법률 서비스 '사고닷' by Happy6Team🙂</div>", unsafe_allow_html=True)



# 우리 팀 소개 페이지
elif st.session_state.current_page == "우리 팀 소개":
    st.title("행복한 6조를 소개합니다😆")



# 우리 서비스 소개 페이지
elif st.session_state.current_page == "우리 서비스 소개":
    st.title("서비스 이용 안내")
    
    st.markdown("### 서비스 이용 방법")
    st.write("1. 회원가입 및 로그인을 합니다.")
    st.write("2. 원하는 서비스를 선택합니다.")
    st.write("3. 질문이나 필요한 정보를 입력합니다.")
    st.write("4. AI가 답변을 생성하는 동안 잠시 기다립니다.")
    st.write("5. 결과를 확인하고 필요한 경우 추가 질문을 할 수 있습니다.")
    
    st.markdown("### 자주 묻는 질문")
    
    expander1 = st.expander("Q: 서비스 이용료는 얼마인가요?")
    expander1.write("A: 기본 서비스는 무료로 제공되며, 고급 기능은 월 구독료가 발생합니다. 자세한 내용은 요금제 페이지를 참고해 주세요.")
    
    expander2 = st.expander("Q: AI 상담의 정확도는 어느 정도인가요?")
    expander2.write("A: 저희 AI는 최신 법률 데이터베이스를 기반으로 약 95% 이상의 정확도를 보여줍니다. 다만, 최종적인 법률 결정은 전문 변호사와의 상담을 권장합니다.")
    
    expander3 = st.expander("Q: 개인정보는 안전하게 보호되나요?")
    expander3.write("A: 네, 모든 데이터는 암호화되어 저장되며, 개인정보보호법을 준수합니다. 자세한 내용은 개인정보처리방침을 참고해 주세요.")

# 모든 페이지에 공통으로 표시되는 푸터
st.markdown("<div class='footer'>© 2025 AI 법률 서비스 '사고닷' by Happy6Team🙂</div>", unsafe_allow_html=True)