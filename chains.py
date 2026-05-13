from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. THIẾT LẬP PROMPT CHO AGENT PHÊ BÌNH (REFLECTION)
reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            # Định nghĩa "vai diễn" cho AI: một influencer chuyên đi soi lỗi và tối ưu bài đăng.
            "You are a viral twitter influencer grading a tweet. Generate critique and recommendations for the user's tweet."
            "Always provide detailed recommendations, including requests for length, virality, style, etc.",
        ),
        # Chỗ trống để bơm toàn bộ lịch sử hội thoại (tweet cũ) vào để nó đọc rồi mới chê được.
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# 2. THIẾT LẬP PROMPT CHO AGENT VIẾT (GENERATION)
generation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            # Định nghĩa vai diễn: một trợ lý viết lách chuyên nghiệp.
            "You are a twitter techie influencer assistant tasked with writing excellent twitter posts."
            " Generate the best twitter post possible for the user's request."
            # Câu quan trọng nhất: "Nếu có lời chê (critique), hãy dựa vào đó mà sửa bản cũ".
            " If the user provides critique, respond with a revised version of your previous attempts.",
        ),
        # Chỗ này để nhận yêu cầu ban đầu HOẶC các bản nháp kèm lời chê từ vòng trước.
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# 3. KHỞI TẠO "BỘ NÃO" (LLM)
# Mặc định nó sẽ tìm API Key trong biến môi trường (file .env bạn vừa cài python-dotenv đấy).
llm = ChatGoogleGenerativeAI(model="models/gemini-3.1-flash-lite", temperature=0)

# 4. TẠO CÁC CHUỖI XỬ LÝ (CHAINS) DÙNG CÚ PHÁP LCEL (|)
# generate_chain: Lấy Prompt viết bài đổ vào AI.
generate_chain = generation_prompt | llm

# reflect_chain: Lấy Prompt phê bình đổ vào AI.
reflect_chain = reflection_prompt | llm