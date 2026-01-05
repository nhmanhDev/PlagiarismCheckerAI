"""
AI Chatbot Service using Gemini API

Provides explanations for plagiarism detection results
"""
import os
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

logger = logging.getLogger(__name__)


class ChatbotService:
    """AI Chatbot for explaining detection results"""
    
    def __init__(self):
        """Initialize Gemini API"""
        if not GEMINI_AVAILABLE:
            logger.warning("google-generativeai not installed. Chatbot disabled.")
            self.model = None
            return
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not set. Chatbot disabled.")
            self.model = None
            return
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
            logger.info("Gemini chatbot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if chatbot is available"""
        return self.model is not None
    
    async def explain_result(
        self,
        query_text: str,
        detection_results: List[Dict],
        user_question: Optional[str] = None
    ) -> str:
        """
        Generate explanation for detection results
        
        Args:
            query_text: Original text that was checked
            detection_results: List of detection results
            user_question: Optional specific question from user
            
        Returns:
            AI-generated explanation in Vietnamese
        """
        if not self.is_available():
            return "Xin lỗi, chatbot AI hiện không khả dụng. Vui lòng kiểm tra cấu hình GEMINI_API_KEY."
        
        # Build context
        context = self._build_context(query_text, detection_results)
        
        # Build prompt
        if user_question:
            prompt = f"""Bạn là chuyên gia phân tích văn bản, đang hỗ trợ người dùng hiểu kết quả kiểm tra đạo văn.

NGỮ CẢNH:
{context}

CÂU HỎI: {user_question}

Hãy trả lời ngắn gọn (100-150 từ), tự nhiên như đang trao đổi trực tiếp:
- Giọng văn thân thiện, chuyên nghiệp
- Giải thích rõ ràng, dễ hiểu
- Không dùng markdown (**, *, bullet points)
- Viết thành đoạn văn liền mạch
- Nếu cần liệt kê, dùng số (1, 2, 3) đơn giản"""
        else:
            prompt = f"""Bạn là chuyên gia phân tích văn bản, đang hỗ trợ người dùng hiểu kết quả kiểm tra đạo văn.

NGỮ CẢNH:
{context}

Hãy viết phân tích ngắn gọn (200-250 từ) với giọng văn tự nhiên, mạch lạc:

Viết thành 3-4 đoạn văn:
- Đoạn 1: Kết luận tổng quan (có đạo văn hay không?)
- Đoạn 2: Giải thích ngắn gọn các điểm số quan trọng nhất
- Đoạn 3: Phân tích điểm đáng chú ý (nếu có)
- Đoạn 4: Gợi ý cải thiện (nếu cần, 2-3 câu ngắn)

YÊU CẦU:
- Viết thành đoạn văn, KHÔNG dùng markdown syntax (**, *, bullet •, ##)
- Giọng văn tự nhiên, chuyên nghiệp nhưng thân thiện
- Nếu cần nhấn mạnh, dùng chữ HOA hoặc để trong ngoặc đơn
- Nếu liệt kê, dùng số (1, 2, 3) hoặc viết liền mạch
- Tập trung insight, không lặp lại dữ liệu"""
        
        try:
            # Call Gemini API
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return f"Xin lỗi, có lỗi xảy ra khi xử lý câu hỏi của bạn: {str(e)}"
    
    def _build_context(
        self,
        query_text: str,
        detection_results: List[Dict]
    ) -> str:
        """Build context string from detection results"""
        
        context = f"VĂN BẢN KIỂM TRA:\n\"{query_text[:200]}{'...' if len(query_text) > 200 else ''}\"\n\n"
        
        if not detection_results or len(detection_results) == 0:
            context += "KẾT QUẢ: Không phát hiện đạo văn.\n"
            return context
        
        # Count suspected
        suspected_count = sum(1 for r in detection_results if r.get('is_suspected', False))
        
        context += f"TỔNG QUAN:\n"
        context += f"- Tổng số kết quả: {len(detection_results)}\n"
        context += f"- Số đoạn nghi đạo văn (≥75%): {suspected_count}\n"
        context += f"- Phương pháp: Multi-stage retrieval\n\n"
        
        # Top 3 results only
        for idx, result in enumerate(detection_results[:3], 1):
            is_suspected = result.get('is_suspected', False)
            status = "NGHI ĐẠO VĂN" if is_suspected else "KHÔNG ĐẠO VĂN"
            
            context += f"--- KẾT QUẢ #{idx} [{status}] ---\n"
            context += f"Văn bản tìm thấy: \"{result['text'][:100]}...\"\n"
            context += f"Điểm cuối: {result['score_final']:.1%}\n"
            
            if 'score_lexical_raw' in result:
                context += f"  - BM25: {result['score_lexical_raw']:.1%}\n"
            if 'score_semantic_raw' in result:
                context += f"  - Semantic: {result['score_semantic_raw']:.1%}\n"
            if 'score_reranker' in result:
                context += f"  - Re-ranker: {result['score_reranker']:.1%}\n"
            context += "\n"
        
        if len(detection_results) > 3:
            context += f"(+{len(detection_results) - 3} kết quả khác)\n"
        
        return context


# Singleton instance
_chatbot_service = None

def get_chatbot_service() -> ChatbotService:
    """Get chatbot service singleton"""
    global _chatbot_service
    if _chatbot_service is None:
        _chatbot_service = ChatbotService()
    return _chatbot_service
