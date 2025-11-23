import streamlit as st
import json
from rapidfuzz import process, fuzz

# Cấu hình trang (Page Config)
st.set_page_config(
    page_title="LMS Tra Cứu",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS để tối ưu giao diện Mobile
st.markdown("""
<style>
    /* Ẩn menu hamburger và footer để giao diện sạch hơn */
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

# Hàm load dữ liệu (Cache để tối ưu hiệu năng)
@st.cache_data
def load_data():
    try:
        with open('database.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("Không tìm thấy file database.json!")
        return []
    except Exception as e:
        st.error(f"Lỗi khi đọc dữ liệu: {e}")
        return []

def main():
    st.title("🔍 Tra cứu LMS")
    
    # Load dữ liệu
    data = load_data()
    
    if not data:
        return

    # Tạo danh sách câu hỏi để tìm kiếm
    questions = [item['question'] for item in data]
    
    # Thanh tìm kiếm (Sticky top logic is hard in pure Streamlit without extra components, 
    # but placing it first makes it appear at top)
    query = st.text_input("", placeholder="Nhập từ khóa câu hỏi (VD: cơ sở dữ liệu...)", help="Gõ từ khóa để tìm kiếm")

    if query:
        # Tìm kiếm mờ (Fuzzy Search)
        # limit=20 để hiển thị 20 kết quả tốt nhất
        results = process.extract(query, questions, scorer=fuzz.token_set_ratio, limit=20)
        
        st.write(f"Tìm thấy {len(results)} kết quả liên quan:")
        
        for match_text, score, index in results:
            if score < 40: # Bỏ qua các kết quả độ trùng khớp quá thấp
                continue
                
            item = data[index]
            
            # Hiển thị dạng Card
            with st.container(border=True):
                st.markdown(f"**{item['question']}**")
                
                # Hiển thị đáp án đúng nổi bật
                st.markdown(f":white_check_mark: **Đáp án:** {item['correct_answer']}")
                
                # Expander để xem các lựa chọn khác (nếu cần đối chiếu)
                with st.expander("Xem tất cả lựa chọn"):
                    for opt in item['options']:
                        if opt == item['correct_answer']:
                            st.markdown(f"- **{opt}** (Đúng)")
                        else:
                            st.markdown(f"- {opt}")
    else:
        st.info("👋 Nhập từ khóa vào ô tìm kiếm để bắt đầu.")
        st.caption(f"Đang có {len(data)} câu hỏi trong cơ sở dữ liệu.")

if __name__ == "__main__":
    main()
