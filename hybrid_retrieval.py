from typing import List, Dict
from rank_bm25 import BM25Okapi
import jieba
from vector_store import VectorStore


class HybridRetrieval:
    """混合检索：结合BM25稀疏检索和向量密集检索"""

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.bm25 = None
        self.documents = []
        self.doc_ids = []

    def build_bm25_index(self, documents: List[Dict[str, str]]):
        """构建BM25索引"""
        self.documents = documents
        self.doc_ids = [doc.get("id", f"doc_{i}") for i, doc in enumerate(documents)]

        # 中文分词处理
        tokenized_docs = []
        for doc in documents:
            content = doc.get("content", "")
            tokens = jieba.lcut(content)
            tokenized_docs.append(tokens)

        self.bm25 = BM25Okapi(tokenized_docs)

    def bm25_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """BM25检索"""
        if not self.bm25:
            return []

        query_tokens = jieba.lcut(query)
        bm25_scores = self.bm25.get_scores(query_tokens)

        # 获取top_k结果
        top_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_k]

        results = []
        for idx in top_indices:
            if bm25_scores[idx] > 0:
                results.append({
                    "content": self.documents[idx].get("content", ""),
                    "metadata": self.documents[idx],
                    "score": float(bm25_scores[idx]),
                    "source": "bm25"
                })

        return results

    def vector_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """向量检索"""
        results = self.vector_store.search(query, top_k=top_k)
        for result in results:
            result["source"] = "vector"
            result["score"] = result.get("distance", 0)  # 距离越小越相似
        return results

    def reciprocal_rank_fusion(self, bm25_results: List[Dict], vector_results: List[Dict], top_k: int = 5, k: int = 60) -> List[Dict]:
        """倒数排名融合(RRF)"""
        rrf_scores = {}

        # 处理BM25结果
        for rank, result in enumerate(bm25_results):
            doc_id = result["metadata"].get("id", result["metadata"].get("filepath", ""))
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = {"doc": result, "score": 0}
            rrf_scores[doc_id]["score"] += 1 / (k + rank + 1)

        # 处理向量结果
        for rank, result in enumerate(vector_results):
            doc_id = result["metadata"].get("id", result["metadata"].get("filepath", ""))
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = {"doc": result, "score": 0}
            rrf_scores[doc_id]["score"] += 1 / (k + rank + 1)

        # 按RRF分数排序
        sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1]["score"], reverse=True)

        return [item[1]["doc"] for item in sorted_docs[:top_k]]

    def hybrid_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """混合检索主函数"""
        if not self.bm25:
            # 如果没有BM25索引，回退到向量检索
            return self.vector_search(query, top_k=top_k)

        # 获取两种检索的结果
        bm25_results = self.bm25_search(query, top_k=top_k*2)
        vector_results = self.vector_search(query, top_k=top_k*2)

        # 使用RRF融合结果
        fused_results = self.reciprocal_rank_fusion(bm25_results, vector_results, top_k=top_k)

        return fused_results