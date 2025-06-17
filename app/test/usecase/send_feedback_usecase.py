from app.utils.email_helper import send_feedback_email
from app.test.dto.request.feedback_request_dto import FeedbackRequestDTO
from app.utils.dto.success import created, ok, no_content

async def send_feedback_usecase(dto: FeedbackRequestDTO):
    subject = f"[AI 해설 피드백] test_id={dto.test_id}, question_id={dto.question_id}"
    body = f"""
🚨 AI 해설 피드백 도착

📌 시험 ID: {dto.test_id}
📌 문제 ID: {dto.question_id}
🧠 AI 해설:
{chr(10).join(dto.ai_explanation)}

🗣️ 사용자 피드백:
{dto.feedback}
    """
    send_feedback_email(subject, body)
    return ok(message="피드백이 성공적으로 제출되었습니다.")
