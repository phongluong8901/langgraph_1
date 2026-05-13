import operator
import asyncio
from typing import Annotated, Any, Sequence
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# 1. Định nghĩa State
class State(TypedDict):
    # Reducer gộp kết quả
    aggregate: Annotated[list, operator.add]
    # Biến dùng để điều hướng luồng đi
    which: str

# 2. Node xử lý
class ReturnNodeValue:
    def __init__(self, node_secret: str):
        self._value = node_secret

    async def __call__(self, state: State) -> Any:
        await asyncio.sleep(1) # Giả lập tác vụ xử lý
        print(f"--- Node {self._value} đang chạy ---")
        return {"aggregate": [self._value]}

# 3. Hàm điều hướng (Conditional Routing)
def route_bc_or_cd(state: State) -> Sequence[str]:
    # Trả về danh sách các node cần kích hoạt tiếp theo
    if state["which"] == "cd":
        return ["c", "d"] # Kích hoạt c và d song song
    return ["b", "c"]     # Kích hoạt b và c song song

builder = StateGraph(State)

# Đăng ký các node
builder.add_node("a", ReturnNodeValue("I'm A"))
builder.add_node("b", ReturnNodeValue("I'm B"))
builder.add_node("c", ReturnNodeValue("I'm C"))
builder.add_node("d", ReturnNodeValue("I'm D"))
builder.add_node("e", ReturnNodeValue("I'm E"))

# Thiết lập luồng
builder.add_edge(START, "a")

# Thêm cạnh có điều kiện từ 'a'
intermediates = ["b", "c", "d"]
builder.add_conditional_edges(
    "a",                  # Node bắt đầu
    route_bc_or_cd,       # Hàm quyết định hướng đi
    intermediates,        # Danh sách các node mục tiêu có thể hướng tới
)

# Tất cả các node trung gian b, c, d đều phải trỏ về e
for node in intermediates:
    builder.add_edge(node, "e")

builder.add_edge("e", END)

graph = builder.compile()

# 4. Chạy thực tế
async def main():
    print(">>> CHẠY LẦN 1: with which='' (Mặc định chạy b và c)")
    # Luồng: a -> [b, c] -> e
    res1 = await graph.ainvoke({"aggregate": [], "which": ""})
    print("Kết quả 1:", res1["aggregate"])

    print("\n>>> CHẠY LẦN 2: with which='cd' (Chạy c và d)")
    # Luồng: a -> [c, d] -> e
    res2 = await graph.ainvoke({"aggregate": [], "which": "cd"})
    print("Kết quả 2:", res2["aggregate"])

if __name__ == "__main__":
    asyncio.run(main())