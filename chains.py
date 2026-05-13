import datetime
from dotenv import load_dotenv

# 1. Tải các biến môi trường từ file .env (thường là OPENAI_API_KEY)
load_dotenv()

from langchain_core.messages import HumanMessage
from langchain_core.output_parsers.openai_tools import (
    JsonOutputToolsParser,
    PydanticToolsParser,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

# Import các cấu trúc dữ liệu đã định nghĩa ở script trước
from schemas import AnswerQuestion, ReviseAnswer

# 2. Khởi tạo mô hình ngôn ngữ (LLM) - ở đây dùng o4-mini
llm = ChatGoogleGenerativeAI(model="models/gemini-3.1-flash-lite", temperature=0)

# 3. Định nghĩa các bộ lọc đầu ra (Parsers)
# Parser trả về định dạng JSON thuần túy
parser = JsonOutputToolsParser(return_id=True)
# Parser chuyển đổi đầu ra trực tiếp thành đối tượng Pydantic (AnswerQuestion)
parser_pydantic = PydanticToolsParser(tools=[AnswerQuestion])

# 4. Xây dựng Template cho lời nhắc (Prompt Template)
actor_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are expert researcher.
Current time: {time}

1. {first_instruction}
2. Reflect and critique your answer. Be severe to maximize improvement.
3. Recommend search queries to research information and improve your answer.""",
        ),
        # Nơi chứa lịch sử các tin nhắn hội thoại
        MessagesPlaceholder(variable_name="messages"),
        # Ép buộc AI phải trả về đúng định dạng yêu cầu (Tools call)
        ("system", "Answer the user's question above using the required format."),
    ]
).partial(
    # Tự động điền thời gian hiện tại mỗi khi prompt được gọi
    time=lambda: datetime.datetime.now().isoformat(),
)

# 5. Cấu hình cho "Người trả lời đầu tiên" (First Responder)
first_responder_prompt_template = actor_prompt_template.partial(
    first_instruction="Provide a detailed ~250 word answer."
)

# Ràng buộc LLM phải sử dụng công cụ "AnswerQuestion" ngay lần đầu
first_responder = first_responder_prompt_template | llm.bind_tools(
    tools=[AnswerQuestion], tool_choice="AnswerQuestion"
)

# 6. Định nghĩa hướng dẫn cho việc "Hiệu chỉnh" (Revision)
revise_instructions = """Revise your previous answer using the new information.
    - You should use the previous critique to add important information to your answer.
    - You MUST include numerical citations in your revised answer to ensure it can be verified.
    - Add a "References" section to the bottom of your answer...
    - You should use the previous critique to remove superfluous information...
"""

# Cấu hình cho "Người hiệu chỉnh" (Revisor)
revisor = actor_prompt_template.partial(
    first_instruction=revise_instructions
) | llm.bind_tools(tools=[ReviseAnswer], tool_choice="ReviseAnswer")

# 7. Thực thi chương trình (Main)
if __name__ == "__main__":
    # Câu hỏi của người dùng về lĩnh vực Autonomous SOC và các startup
    human_message = HumanMessage(
        content="Write about AI-Powered SOC / autonomous soc problem domain,"
        " list startups that do that and raised capital."
    )
    
    # Tạo chuỗi xử lý (Chain): Prompt -> Gọi LLM kèm Tool -> Trích xuất dữ liệu Pydantic
    chain = (
        first_responder_prompt_template
        | llm.bind_tools(tools=[AnswerQuestion], tool_choice="AnswerQuestion")
        | parser_pydantic
    )

    # Chạy chuỗi và in kết quả
    res = chain.invoke(input={"messages": [human_message]})
    print(res)