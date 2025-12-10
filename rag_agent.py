from typing import List, Dict, Optional, Tuple

from openai import OpenAI

from config import (
    OPENAI_API_KEY,
    OPENAI_API_BASE,
    MODEL_NAME,
    TOP_K,
)
from vector_store import VectorStore
from hybrid_retrieval import HybridRetrieval


class RAGAgent:
    def __init__(
        self,
        model: str = MODEL_NAME,
        use_hybrid_retrieval: bool = False,
    ):
        self.model = model
        self.use_hybrid_retrieval = use_hybrid_retrieval

        self.client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)

        self.vector_store = VectorStore()

        # 初始化混合检索
        if self.use_hybrid_retrieval:
            self.hybrid_retriever = HybridRetrieval(self.vector_store)
            self._build_hybrid_index()

        """
        TODO: 实现并调整系统提示词，使其符合课程助教的角色和回答策略
        """
        self.system_prompt = """You are a teaching assistant for this course. Your role is to help students understand course materials by answering their questions based on the provided course documents. 

Guidelines:
1. Answer questions accurately based on the retrieved course content
2. Cite specific sources (filename and page number) when referencing course materials
3. If the retrieved content doesn't fully answer the question, acknowledge this limitation
4. Use clear and concise language suitable for students
5. Maintain a helpful and professional tone"""

    def _build_hybrid_index(self):
        """构建混合检索索引"""
        try:
            documents = self.vector_store.get_all_documents()
            if documents:
                self.hybrid_retriever.build_bm25_index(documents)
        except Exception:
            pass  # 静默失败，不影响原有功能

    def retrieve_context(
        self, query: str, top_k: int = TOP_K
    ) -> Tuple[str, List[Dict]]:
        """检索相关上下文
        支持混合检索和向量检索
        """
        if self.use_hybrid_retrieval and hasattr(self, 'hybrid_retriever'):
            retrieved_docs = self.hybrid_retriever.hybrid_search(query, top_k=top_k)
        else:
            retrieved_docs = self.vector_store.search(query, top_k=top_k)
        
        context_parts = []
        for idx, doc in enumerate(retrieved_docs, 1):
            metadata = doc.get("metadata", {})
            filename = metadata.get("filename", "unknown")
            page_number = metadata.get("page_number", 0)
            content = doc.get("content", "")
            
            if page_number > 0:
                source_info = f"[来源 {idx}]: {filename} 第 {page_number} 页"
            else:
                source_info = f"[来源 {idx}]: {filename}"
            
            context_parts.append(f"{source_info}\n{content}\n")
        
        context = "\n".join(context_parts)
        return context, retrieved_docs

    def generate_response(
        self,
        query: str,
        context: str,
        chat_history: Optional[List[Dict]] = None,
    ) -> str:
        """生成回答
        
        参数:
            query: 用户问题
            context: 检索到的上下文
            chat_history: 对话历史
        """
        messages = [{"role": "system", "content": self.system_prompt}]

        if chat_history:
            messages.extend(chat_history)

        """
        TODO: 实现用户提示词
        要求：
        1. 包含相关的课程内容
        2. 包含学生问题
        3. 包含来源信息（文件名和页码）
        4. 返回用户提示词
        """
        user_text = f"""Based on the following course materials, please answer the student's question. Make sure to cite the source (filename and page number) when referencing specific content.

Course Materials:
{context}

Student Question: {query}

Please provide a clear and accurate answer based on the course materials above."""

        messages.append({"role": "user", "content": user_text})
        
        # 多模态接口示意（如需添加图片支持，可参考以下格式）：
        # content_parts = [{"type": "text", "text": user_text}]
        # content_parts.append({
        #     "type": "image_url",
        #     "image_url": {"url": f"data:image/png;base64,{base64_image}"}
        # })
        # messages.append({"role": "user", "content": content_parts})

        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.7, max_tokens=1500
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"生成回答时出错: {str(e)}"

    def answer_question(
        self, query: str, chat_history: Optional[List[Dict]] = None, top_k: int = TOP_K
    ) -> Dict[str, any]:
        """回答问题
        
        参数:
            query: 用户问题
            chat_history: 对话历史
            top_k: 检索文档数量
            
        返回:
            生成的回答
        """
        context, retrieved_docs = self.retrieve_context(query, top_k=top_k)

        if not context:
            context = "（未检索到特别相关的课程材料）"

        answer = self.generate_response(query, context, chat_history)

        return answer

    def chat(self) -> None:
        """交互式对话"""
        print("=" * 60)
        print("欢迎使用智能课程助教系统！")
        print("=" * 60)

        chat_history = []

        while True:
            try:
                query = input("\n学生: ").strip()

                if not query:
                    continue

                answer = self.answer_question(query, chat_history=chat_history)

                print(f"\n助教: {answer}")

                chat_history.append({"role": "user", "content": query})
                chat_history.append({"role": "assistant", "content": answer})

            except Exception as e:
                print(f"\n错误: {str(e)}")
