from dotenv import load_dotenv
import operator
from typing import Annotated, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# 1. Khởi tạo môi trường
load_dotenv()

# 2. Định nghĩa State với Reducer
class State(TypedDict):
    # Annotated[Kiểu dữ liệu, Hàm gộp]
    # operator.add ở đây giúp list không bị ghi đè mà sẽ được cộng dồn (append)
    aggregate: Annotated[list, operator.add]

# 3. Tạo một Class Node có thể tái sử dụng
class ReturnNodeValue:
    def __init__(self, node_secret: str):
        self._value = node_secret

    def __call__(self, state: State) -> Any:
        import time
        time.sleep(1) # Giả lập tác vụ tốn thời gian (như gọi API)
        print(f"--- Node {self._value} đang chạy ---")
        print(f"Dữ liệu hiện tại trong State: {state['aggregate']}")
        
        # Trả về giá trị mới để Reducer gộp vào State chính
        return {"aggregate": [self._value]}

# 4. Xây dựng sơ đồ (Graph)
builder = StateGraph(State)

# Thêm các nút
builder.add_node("a", ReturnNodeValue("I'm A"))
builder.add_node("b", ReturnNodeValue("I'm B"))
builder.add_node("b2", ReturnNodeValue("I'm B2"))
builder.add_node("c", ReturnNodeValue("I'm C"))
builder.add_node("d", ReturnNodeValue("I'm D"))

# Thiết lập luồng đi
builder.add_edge(START, "a")

# Từ 'a' rẽ ra hai nhánh chạy song song: một hướng đi b, một hướng đi c
builder.add_edge("a", "b")
builder.add_edge("a", "c")

# Nhánh 1 đi tiếp từ b sang b2
builder.add_edge("b", "b2")

# Điểm hội tụ: d chỉ chạy khi b2 và c đã hoàn thành
builder.add_edge(["b2", "c"], "d")

builder.add_edge("d", END)

# 5. Biên dịch và thực thi
graph = builder.compile()

# Xuất sơ đồ ra ảnh để kiểm tra cấu trúc song song
graph.get_graph().draw_mermaid_png(output_file_path="async.png")

if __name__ == "__main__":
    print("--- Bắt đầu chạy Async Graph ---")
    
    # Khởi tạo state ban đầu là một list rỗng
    final_state = graph.invoke(
        {"aggregate": []}, 
        {"configurable": {"thread_id": "foo"}}
    )
    
    print("\nKết quả cuối cùng trong State:")
    print(final_state["aggregate"])