from typing import Literal
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import END, START, StateGraph, MessagesState

# Import các thành phần đã định nghĩa ở các file trước
from chains import revisor, first_responder
from tool_executor import execute_tools

# Giới hạn số lần lặp (số lần đi tìm kiếm thêm thông tin) để tránh tốn phí hoặc lặp vô tận
MAX_ITERATIONS = 2

# 1. Node viết nháp (Draft Node)
def draft_node(state: MessagesState):
    """Tạo ra câu trả lời ban đầu."""
    # Lấy lịch sử tin nhắn từ state và gửi tới first_responder
    response = first_responder.invoke({"messages": state["messages"]})
    # Trả về kết quả dưới dạng danh sách tin nhắn để cập nhật vào State
    return {"messages": [response]}

# 2. Node hiệu chỉnh (Revise Node)
def revise_node(state: MessagesState):
    """Viết lại câu trả lời dựa trên kết quả tìm kiếm được."""
    response = revisor.invoke({"messages": state["messages"]})
    return {"messages": [response]}

# 3. Logic điều hướng (Event Loop / Conditional Edge)
def event_loop(state: MessagesState) -> Literal["execute_tools", END]:
    """Quyết định tiếp tục đi tìm kiếm thông tin hay kết thúc quy trình."""
    # Đếm xem đã có bao nhiêu ToolMessage (kết quả tìm kiếm) trong lịch sử
    count_tool_visits = sum(
        isinstance(item, ToolMessage) for item in state["messages"]
    )
    
    # Nếu số lần tìm kiếm vượt quá giới hạn, kết thúc và trả ra kết quả cuối
    if count_tool_visits > MAX_ITERATIONS:
        return END
    # Nếu chưa, quay lại bước thực thi công cụ tìm kiếm
    return "execute_tools"

# 4. Xây dựng cấu trúc đồ thị (StateGraph)
builder = StateGraph(MessagesState)

# Thêm các Node vào đồ thị
builder.add_node("draft", draft_node)            # Bước 1: Viết nháp
builder.add_node("execute_tools", execute_tools) # Bước 2: Đi tìm kiếm web
builder.add_node("revise", revise_node)          # Bước 3: Sửa bài

# Thiết lập luồng di chuyển (Edges)
builder.add_edge(START, "draft")                 # Bắt đầu -> Viết nháp
builder.add_edge("draft", "execute_tools")       # Viết nháp xong -> Đi tìm kiếm
builder.add_edge("execute_tools", "revise")      # Tìm xong -> Giao cho Revisor

# Thiết lập cạnh điều kiện (Vòng lặp)
# Sau khi sửa bài, kiểm tra xem có cần tìm kiếm tiếp không hay dừng lại
builder.add_conditional_edges("revise", event_loop, ["execute_tools", END])

# Biên dịch đồ thị thành một ứng dụng có thể chạy được
graph = builder.compile()

# In sơ đồ đồ thị dưới dạng mã Mermaid (có thể dán vào trình xem biểu đồ)
print(graph.get_graph().draw_mermaid())

# 5. Thực thi ứng dụng với câu hỏi cụ thể
res = graph.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Write about AI-Powered SOC / autonomous soc problem domain, list startups that do that and raised capital.",
            }
        ]
    }
)

# 6. Trích xuất kết quả cuối cùng
last_message = res["messages"][-1]
# Lấy nội dung trường "answer" nằm trong lần gọi Tool cuối cùng của AI
if isinstance(last_message, AIMessage) and last_message.tool_calls:
    print(last_message.tool_calls[0]["args"]["answer"])