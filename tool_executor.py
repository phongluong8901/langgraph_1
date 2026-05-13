from dotenv import load_dotenv

# 1. Tải các biến môi trường (cần TAVILY_API_KEY để công cụ tìm kiếm hoạt động)
load_dotenv()

from langchain_core.tools import StructuredTool
from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode

from schemas import AnswerQuestion, ReviseAnswer

# 2. Khởi tạo công cụ tìm kiếm Tavily
# max_results=5: Giới hạn mỗi truy vấn tìm kiếm sẽ trả về tối đa 5 kết quả hàng đầu.
tavily_tool = TavilySearch(max_results=5)


# 3. Định nghĩa hàm chạy các câu truy vấn tìm kiếm
def run_queries(search_queries: list[str], **kwargs):
    """Thực thi các câu truy vấn tìm kiếm được tạo ra bởi AI."""
    # .batch: Cho phép chạy song song nhiều câu truy vấn cùng lúc để tiết kiệm thời gian.
    # Mỗi query trong list sẽ được đóng gói thành một dictionary để Tavily xử lý.
    return tavily_tool.batch([{"query": query} for query in search_queries])


# 4. Thiết lập Node thực thi công cụ cho LangGraph
# ToolNode là một thành phần đặc biệt của LangGraph dùng để tự động kích hoạt công cụ.
execute_tools = ToolNode(
    [
        # Biến hàm 'run_queries' thành một StructuredTool.
        # name=AnswerQuestion.__name__: Đặt tên công cụ trùng với tên class trong schema.
        # Điều này giúp LangGraph biết khi AI gọi tool 'AnswerQuestion', 
        # nó sẽ chạy hàm 'run_queries' với các 'search_queries' bên trong.
        StructuredTool.from_function(run_queries, name=AnswerQuestion.__name__),
        
        # Tương tự, gán hàm tìm kiếm cho hành động hiệu chỉnh (ReviseAnswer).
        StructuredTool.from_function(run_queries, name=ReviseAnswer.__name__),
    ]
)