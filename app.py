import streamlit as st
import json
import os
import glob
from rapidfuzz import process, fuzz

# Cấu hình trang (Page Config)
st.set_page_config(
    page_title="LMS Tra Cứu Đa Môn",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS để tối ưu giao diện Mobile
st.markdown("""
<style>
    /* Ẩn menu hamburger và footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Tùy chỉnh thanh tìm kiếm */
    .stTextInput > div > div > input {
        border-radius: 20px;
        padding: 10px 15px;
    }
    
    /* Tùy chỉnh card kết quả */
    .result-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #e0e0e0;
    }
    
    .correct-answer {
        color: #0f5132;
        background-color: #d1e7dd;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

DATA_DIR = "data"

def get_available_subjects():
    """Lấy danh sách các môn học từ thư mục data"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        return []
    # Lấy các thư mục con trong DATA_DIR
    subjects = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    return sorted(subjects)

@st.cache_data
def load_subject_data(subject_name):
    """Load tất cả file json trong thư mục của môn học"""
    all_data = []
    subject_path = os.path.join(DATA_DIR, subject_name)
    
    # Tìm tất cả file .json trong thư mục môn học
    json_files = glob.glob(os.path.join(subject_path, "*.json"))
    
    if not json_files:
        return []

    for jf in json_files:
        try:
            with open(jf, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_data.extend(data)
                else:
                    st.warning(f"File {os.path.basename(jf)} không đúng định dạng list.")
        except Exception as e:
            st.error(f"Lỗi khi đọc file {os.path.basename(jf)}: {e}")
            
    return all_data

def main():
    st.title("📚 Tra cứu LMS Đa Môn")
    
    # Sidebar chọn môn học
    subjects = get_available_subjects()
    
    if not subjects:
        st.warning(f"Chưa có dữ liệu môn học nào trong thư mục `{DATA_DIR}`.")
        st.info("Vui lòng tạo thư mục môn học trong `data/` và thêm file .json vào đó.")
        return

    # Chọn môn học (Mặc định chọn môn đầu tiên)
    selected_subject = st.selectbox("📖 Chọn môn học:", subjects)
    
    if selected_subject:
        # Load dữ liệu của môn đã chọn
        data = load_subject_data(selected_subject)
        
        if not data:
            st.warning(f"Môn **{selected_subject}** chưa có câu hỏi nào.")
            return

        st.caption(f"Đang tra cứu môn: **{selected_subject}** ({len(data)} câu hỏi)")

        # Tạo danh sách câu hỏi để tìm kiếm
        questions = [item.get('question', '') for item in data]
        
        # Thanh tìm kiếm
        query = st.text_input("", placeholder="Nhập từ khóa câu hỏi...", help="Gõ từ khóa để tìm kiếm")

        if query:
            # Tìm kiếm mờ (Fuzzy Search)
            results = process.extract(query, questions, scorer=fuzz.token_set_ratio, limit=20)
            
            found_count = 0
            # Container cho kết quả
            results_container = st.container()
            
            with results_container:
                for match_text, score, index in results:
                    if score < 40: # Ngưỡng lọc kết quả
                        continue
                    
                    found_count += 1
                    item = data[index]
                    
                    # Hiển thị dạng Card
                    with st.container(border=True):
                        st.markdown(f"**{item.get('question', 'Câu hỏi lỗi')}**")
                        
                        correct = item.get('correct_answer', 'Chưa có đáp án')
                        st.markdown(f":white_check_mark: **Đáp án:** {correct}")
                        
                        with st.expander("Xem chi tiết"):
                            options = item.get('options', [])
                            for opt in options:
                                if opt == correct:
                                    st.markdown(f"- **{opt}** (Đúng)")
                                else:
                                    st.markdown(f"- {opt}")
            
            if found_count > 0:
                st.toast(f"Tìm thấy {found_count} kết quả!", icon="✅")
            else:
                st.info("Không tìm thấy kết quả phù hợp.")
        else:
            st.info("👋 Nhập từ khóa để bắt đầu tìm kiếm.")

if __name__ == "__main__":
    main()
