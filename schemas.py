from typing import List
from pydantic import BaseModel, Field

# 1. Định nghĩa lớp Phản biện (Reflection)
class Reflection(BaseModel):
    # Critique về những thông tin còn thiếu trong câu trả lời ban đầu
    missing: str = Field(description="Critique of what is missing.")
    # Critique về những thông tin thừa thãi, không cần thiết
    superfluous: str = Field(description="Critique of what is superfluous")

# 2. Định nghĩa lớp Trả lời câu hỏi (AnswerQuestion)
class AnswerQuestion(BaseModel):
    """Lớp dùng để tạo câu trả lời ban đầu kèm theo sự tự đánh giá."""

    # Nội dung câu trả lời chi tiết (khoảng 250 từ)
    answer: str = Field(description="~250 word detailed answer to the question.")
    
    # Gắn lớp Reflection vào để AI tự soi xét lại câu trả lời vừa viết ở trên
    reflection: Reflection = Field(description="Your reflection on the initial answer.")
    
    # Danh sách các từ khóa tìm kiếm (1-3 câu) để bổ sung kiến thức cho phần critique
    search_queries: List[str] = Field(
        description="1-3 search queries for researching improvements to address the critique of your current answer."
    )

# 3. Định nghĩa lớp Chỉnh sửa câu trả lời (ReviseAnswer) kế thừa từ AnswerQuestion
class ReviseAnswer(AnswerQuestion):
    """Lớp dùng để hiệu chỉnh câu trả lời dựa trên phản biện và tìm kiếm."""

    # Bổ sung thêm danh sách các nguồn tham khảo hoặc trích dẫn cho câu trả lời mới
    references: List[str] = Field(
        description="Citations motivating your updated answer."
    )