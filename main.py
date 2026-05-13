# 1. NẠP BIẾN MÔI TRƯỜNG (PHẢI LÀM ĐẦU TIÊN)
from dotenv import load_dotenv
load_dotenv()  # Đọc file .env để lấy GOOGLE_API_KEY trước khi các thư viện khác cần dùng đến nó.

# 2. IMPORT CÁC THƯ VIỆN HỖ TRỢ
from typing import List, Sequence
from langchain_core.messages import BaseMessage, HumanMessage  # Các kiểu dữ liệu tin nhắn của LangChain.
from langgraph.graph import END, MessageGraph  # Công cụ xây dựng luồng (Graph) của LangGraph.

# 3. IMPORT CÁC CHAIN ĐÃ ĐỊNH NGHĨA Ở FILE chains.py
from chains import generate_chain, reflect_chain

# 4. ĐẶT TÊN CHO CÁC NODE (NÚT) TRONG SƠ ĐỒ
REFLECT = "reflect"   # Node dùng để phê bình bài viết.
GENERATE = "generate" # Node dùng để viết hoặc sửa bài viết.

# 5. ĐỊNH NGHĨA NODE VIẾT BÀI (GENERATION NODE)
def generation_node(state: Sequence[BaseMessage]):
    # Nhận vào danh sách tin nhắn (state), gửi vào LLM để tạo bài viết mới.
    return generate_chain.invoke({"messages": state})

# 6. ĐỊNH NGHĨA NODE PHÊ BÌNH (REFLECTION NODE)
def reflection_node(messages: Sequence[BaseMessage]) -> List[BaseMessage]:
    # Gửi bài viết vừa tạo cho AI phê bình. 
    res = reflect_chain.invoke({"messages": messages})
    # Chuyển nội dung phê bình của AI thành một HumanMessage để "đánh lừa" 
    # luồng tiếp theo rằng đây là yêu cầu chỉnh sửa từ người dùng.
    return [HumanMessage(content=res.content)]

# 7. KHỞI TẠO VÀ XÂY DỰNG ĐỒ THỊ (GRAPH)
builder = MessageGraph() # Khởi tạo đồ thị chuyên quản lý tin nhắn.

# Thêm các nút vào sơ đồ
builder.add_node(GENERATE, generation_node) # Đăng ký node viết bài.
builder.add_node(REFLECT, reflection_node)   # Đăng ký node phê bình.

# Điểm bắt đầu của chương trình là node GENERATE
builder.set_entry_point(GENERATE)

# 8. HÀM KIỂM TRA ĐIỀU KIỆN DỪNG (ROUTING)
def should_continue(state: List[BaseMessage]):
    # Nếu danh sách tin nhắn > 6 (tương ứng khoảng 3 vòng lặp Viết -> Chê -> Viết)
    if len(state) > 6:
        return END      # Kết thúc chương trình.
    return REFLECT      # Nếu chưa đủ 6 tin nhắn, tiếp tục gửi sang node Phê bình.

# 9. THIẾT LẬP CÁC ĐƯỜNG NỐI (EDGES)
# Sau khi GENERATE xong, chạy hàm should_continue để quyết định đi tiếp hay dừng lại.
builder.add_conditional_edges(GENERATE, should_continue)

# Sau khi REFLECT xong, bắt buộc quay lại node GENERATE để sửa bài dựa trên lời chê.
builder.add_edge(REFLECT, GENERATE)

# 10. BIÊN DỊCH VÀ VẼ SƠ ĐỒ
graph = builder.compile() # Tạo thành một ứng dụng hoàn chỉnh.
print(graph.get_graph().draw_mermaid()) # Xuất mã Mermaid (dùng để vẽ biểu đồ online).
# graph.get_graph().print_ascii() # Vẽ sơ đồ bằng chữ trong terminal (cần thư viện grandalf).

# 11. CHẠY CHƯƠNG TRÌNH
if __name__ == "__main__":
    print("Hello LangGraph")
    # Tin nhắn mồi ban đầu
    inputs = HumanMessage(content="""Make this tweet better:
                                    @LangChainAI
                                    — newly Tool Calling feature is seriously underrated.
                                    After a long wait, it's here...""")
    
    # Kích hoạt luồng chạy tự động
    response = graph.invoke(inputs)
    
    # In ra kết quả cuối cùng (tin nhắn cuối trong danh sách lịch sử)
    print("\n--- TWEET CUỐI CÙNG SAU KHI TỐI ƯU ---")
    print(response[-1].content)