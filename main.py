import os
from dotenv import load_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
# Lưu ý: Import từ thư viện checkpoint riêng nếu bạn đã cài đặt nó
from langgraph.checkpoint.sqlite import SqliteSaver

# 1. Cấu hình môi trường
load_dotenv()

# 2. Định nghĩa cấu trúc dữ liệu (State)
class State(TypedDict):
    input: str
    user_feedback: str

# 3. Định nghĩa các Node
def step_1(state: State) -> None:
    print("\n--- Đang thực hiện Bước 1 ---")

def human_feedback(state: State) -> None:
    print("\n--- Đang ở node Chờ Phản Hồi (Xử lý sau khi nhận input) ---")

def step_3(state: State) -> None:
    print("\n--- Đang thực hiện Bước 3 ---")
    print(f"Dữ liệu nhận được từ người dùng: {state.get('user_feedback')}")

# 4. Xây dựng luồng công việc (Graph Construction)
builder = StateGraph(State)

builder.add_node("step_1", step_1)
builder.add_node("human_feedback", human_feedback)
builder.add_node("step_3", step_3)

builder.add_edge(START, "step_1")
builder.add_edge("step_1", "human_feedback")
builder.add_edge("human_feedback", "step_3")
builder.add_edge("step_3", END)

# 5 & 6. Sử dụng Context Manager để quản lý SQLite và Biên dịch Graph
# Việc sử dụng 'with' đảm bảo file sqlite được mở và đóng chính xác, tránh lỗi 'Invalid checkpointer'
with SqliteSaver.from_conn_string("checkpoints.sqlite") as memory:
    
    # Biên dịch graph bên trong khối with
    graph = builder.compile(checkpointer=memory, interrupt_before=["human_feedback"])

    # 7. Chạy chương trình
    if __name__ == "__main__":
        # thread_id giúp lưu trữ và khôi phục đúng phiên làm việc này
        thread = {"configurable": {"thread_id": "unique_session_001"}}

        initial_input = {"input": "Khởi tạo hệ thống"}

        print(">>> GIAI ĐOẠN 1: Chạy tự động cho đến khi gặp điểm ngắt")
        # Chạy graph, nó sẽ dừng lại TRƯỚC node 'human_feedback'
        for event in graph.stream(initial_input, thread, stream_mode="values"):
            print(f"Trạng thái hiện tại: {event}")

        # Kiểm tra bước tiếp theo
        state_info = graph.get_state(thread)
        print(f"\n[Hệ thống]: Đang tạm dừng. Bước tiếp theo dự kiến là: {state_info.next}")

        # 8. Mô phỏng hành động của con người
        user_input = input("\n[Người dùng]: Nhập ý kiến của bạn: ")

        # Cập nhật dữ liệu vào State
        # 'as_node' thông báo cho hệ thống rằng dữ liệu này được coi là đầu ra của node human_feedback
        graph.update_state(thread, {"user_feedback": user_input}, as_node="human_feedback")

        print("\n--- State đã được cập nhật thủ công. Đang tiếp tục... ---")
        
        # 9. TIẾP TỤC CHẠY
        # Truyền 'None' để Graph lấy dữ liệu từ checkpoint đã lưu trong file sqlite
        for event in graph.stream(None, thread, stream_mode="values"):
            print(event)

        print("\n--- Hoàn thành luồng công việc ---")