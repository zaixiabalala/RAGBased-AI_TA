import sys
import os

# 添加父目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from rag_agent import RAGAgent
from document_loader import DocumentLoader
from vector_store import VectorStore


@st.cache_resource
def get_agent(use_hybrid: bool = False):
    """初始化并缓存RAG Agent"""
    return RAGAgent(use_hybrid_retrieval=use_hybrid)


def rebuild_knowledge_base():
    """重建知识库"""
    try:
        vs = VectorStore()
        vs.clear_collection()

        loader = DocumentLoader()
        documents = loader.load_all_documents()

        if not documents:
            return False, "未找到可加载的文档"

        vs.add_documents(documents)
        return True, f"成功重建知识库，共 {len(documents)} 个文档片段"
    except Exception as e:
        return False, f"重建失败: {str(e)}"


def generate_quiz(agent, topic="", difficulty="中等"):
    """生成习题"""
    try:
        if not topic:
            # 随机从知识库中选择内容
            context = agent.retrieve_context("随机选择一个知识点", top_k=1)[0]
        else:
            # 根据指定主题检索
            context = agent.retrieve_context(topic, top_k=2)[0]

        prompt = f"""根据以下课程内容，生成一道{difficulty}难度的单选题。

课程内容：
{context}

请以JSON格式返回：
{{
    "question": "题目内容",
    "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
    "correct_answer": "A",
    "explanation": "答案解析"
}}

确保题目具有挑战性，选项合理，答案唯一正确。"""

        messages = [
            {"role": "system", "content": "你是一个专业的出题专家，擅长根据课程内容生成高质量的习题。"},
            {"role": "user", "content": prompt}
        ]

        response = agent.client.chat.completions.create(
            model=agent.model,
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"生成习题失败: {str(e)}"