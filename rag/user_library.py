"""
Pleadly v2 — 用户信息库
管理用户专属的文档索引: 上传 → 分块 → 向量化 → 检索
"""

import os
import math
import hashlib
from typing import List, Dict, Optional, Set
from collections import defaultdict
from dataclasses import dataclass, field

import chromadb
from chromadb import Collection
from sentence_transformers import SentenceTransformer

from .chunker import (
    Chunk, auto_chunk, read_text_from_file, QueryRouter,
)
from .vector_store import get_chroma_client, embed_texts, embed_query


# ═══════════════════════════════════════════════════════════
# USER LIBRARY COLLECTION NAME
# ═══════════════════════════════════════════════════════════

USER_COLLECTION = "user_library"

# In-memory BM25 index — maps chunk_id → token-frequency map
_bm25_global: dict = {}


# ═══════════════════════════════════════════════════════════
# SIMPLE BM25 — 轻量级关键词检索，零额外依赖
# ═══════════════════════════════════════════════════════════

def _tokenize(text: str) -> List[str]:
    """简单中文+英文分词。中文逐字切，英文按空格切。"""
    tokens = []
    # 拆分中英文混合
    import re
    # 英文单词
    en_words = re.findall(r'[a-zA-Z0-9_+#.]+', text.lower())
    tokens.extend(en_words)
    # 中文单字 + 双字
    cn_chars = re.findall(r'[一-鿿]', text)
    tokens.extend(cn_chars)
    # 中文双字组合
    for i in range(len(cn_chars) - 1):
        tokens.append(cn_chars[i] + cn_chars[i + 1])
    return tokens


class SimpleBM25:
    """
    轻量级 BM25 关键词检索。
    用于跟向量检索引擎互补 —— 精确关键词匹配。
    """

    k1: float = 1.5
    b: float = 0.75

    def __init__(self):
        self.doc_tokens: Dict[str, List[str]] = {}   # doc_id → tokens
        self.doc_lengths: Dict[str, int] = {}         # doc_id → token count
        self.avgdl: float = 0
        self.idf: Dict[str, float] = {}               # token → idf
        self.N: int = 0                                # total docs

    def add_document(self, doc_id: str, text: str):
        tokens = _tokenize(text)
        self.doc_tokens[doc_id] = tokens
        self.doc_lengths[doc_id] = len(tokens)
        self.N += 1
        self.avgdl = sum(self.doc_lengths.values()) / self.N

        # 更新 IDF
        unique_tokens = set(tokens)
        for t in unique_tokens:
            self.idf[t] = self.idf.get(t, 0) + 1

    def remove_document(self, doc_id: str):
        if doc_id not in self.doc_tokens:
            return
        tokens = self.doc_tokens.pop(doc_id, [])
        del self.doc_lengths[doc_id]
        self.N -= 1
        if self.N > 0:
            self.avgdl = sum(self.doc_lengths.values()) / self.N

        # 更新 IDF
        unique_tokens = set(tokens)
        for t in unique_tokens:
            if t in self.idf:
                self.idf[t] -= 1
                if self.idf[t] <= 0:
                    del self.idf[t]

    def _score(self, query: str, doc_id: str) -> float:
        query_tokens = _tokenize(query)
        if doc_id not in self.doc_tokens:
            return 0.0

        doc_tokens = self.doc_tokens[doc_id]
        dl = self.doc_lengths[doc_id]
        tf = defaultdict(int)
        for t in doc_tokens:
            tf[t] += 1

        score = 0.0
        for qt in query_tokens:
            idf = math.log((self.N - self.idf.get(qt, 0) + 0.5) / (self.idf.get(qt, 0) + 0.5) + 1.0)
            f = tf.get(qt, 0)
            numerator = f * (self.k1 + 1)
            denominator = f + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
            score += idf * numerator / denominator if denominator > 0 else 0
        return score

    def search(self, query: str, k: int = 10) -> List[tuple]:
        """返回 [(doc_id, score), ...] 按分数降序。"""
        scores = [(doc_id, self._score(query, doc_id)) for doc_id in self.doc_tokens]
        scores.sort(key=lambda x: x[1], reverse=True)
        return [(did, s) for did, s in scores[:k] if s > 0]


# ═══════════════════════════════════════════════════════════
# USER LIBRARY
# ═══════════════════════════════════════════════════════════

@dataclass
class LibraryStats:
    """用户信息库状态。"""
    total_documents: int = 0
    total_chunks: int = 0
    total_chars: int = 0
    sources: List[Dict] = field(default_factory=list)  # [{source, chunks, chars, doc_type}]


class UserLibrary:
    """
    用户专属信息库。
    每个用户一个实例。数据存 ChromaDB collection `user_library`。
    """

    def __init__(self, persist_path: str = None, embedding_model: str = "shibing624/text2vec-base-chinese"):
        self.client = get_chroma_client()
        self.collection: Optional[Collection] = None
        self.router = QueryRouter()
        self.bm25 = SimpleBM25()
        self._init_collection()

    def _init_collection(self):
        """初始化或加载 ChromaDB collection。"""
        try:
            self.collection = self.client.get_collection(USER_COLLECTION)
        except Exception:
            self.collection = self.client.create_collection(
                name=USER_COLLECTION,
                metadata={"description": "用户专属信息库 — 简历/项目/作品/证书"}
            )

        # 重建 BM25 索引
        self._rebuild_bm25()

    def _rebuild_bm25(self):
        """从 ChromaDB 重建 BM25 索引。"""
        self.bm25 = SimpleBM25()
        if self.collection is None:
            return
        try:
            result = self.collection.get(include=["documents", "metadatas"])
            if result["ids"]:
                for i, chunk_id in enumerate(result["ids"]):
                    doc = result["documents"][i] or ""
                    self.bm25.add_document(chunk_id, doc)
        except Exception:
            pass

    # ── INGEST ──────────────────────────────────────

    def add_file(
        self,
        file_path: str,
        label: str = "",
        doc_type_override: str = "",
    ) -> List[str]:
        """
        上传文件 → 自动识别类型 → 智能分块 → 嵌入 → 存入索引。

        Args:
            file_path: 文件路径
            label: 自定义标签（如"简历-校招版"）
            doc_type_override: 强制指定文档类型（"resume"/"project"/"certificate"/"other"）

        Returns:
            新增的 chunk_id 列表
        """
        text, filename = read_text_from_file(file_path)
        if text.startswith("[") and "失败" in text:
            raise ValueError(f"文件解析失败: {text}")

        return self.add_text(text, filename, label, doc_type_override)

    def add_text(
        self,
        text: str,
        source_name: str = "untitled",
        label: str = "",
        doc_type_override: str = "",
    ) -> List[str]:
        """
        直接摄入文本 → 智能分块 → 嵌入 → 存入索引。
        """
        if not text.strip():
            return []

        # 1. 分块
        if doc_type_override:
            from .chunker import resume_chunker, semantic_chunker, identity_chunker
            if doc_type_override == "resume":
                chunks = resume_chunker(text, source_file=source_name, resume_version=label or "default")
            elif doc_type_override == "project":
                chunks = semantic_chunker(text, doc_type="project", source_file=source_name, project_name=label or source_name)
            else:
                chunks = identity_chunker(text, doc_type=doc_type_override, source_file=source_name, label=label)
        else:
            chunks = auto_chunk(text, source_file=source_name, label=label)

        if not chunks:
            return []

        # 2. 生成唯一 ID（基于内容哈希 + 源文件名 + 分块序号）
        chunk_ids = []
        texts = []
        metadatas = []
        for i, chunk in enumerate(chunks):
            content_hash = hashlib.md5(chunk.content.encode()).hexdigest()[:12]
            cid = f"ul_{source_name}_{content_hash}_{i}"
            chunk_ids.append(cid)
            texts.append(chunk.content)
            chunk.metadata["source_file"] = source_name
            chunk.metadata["chunk_id"] = cid
            if label:
                chunk.metadata["label"] = label
            metadatas.append(chunk.metadata)

        # 3. 嵌入
        embeddings = embed_texts(texts)

        # 4. 存入 ChromaDB（先删旧数据再插入，避免重复）
        try:
            # 删除来自同一源文件的所有旧 chunks
            existing = self.collection.get(
                where={"source_file": source_name},
                include=["metadatas"]
            )
            if existing["ids"]:
                self.collection.delete(ids=existing["ids"])
                # 同步 BM25
                for old_id in existing["ids"]:
                    self.bm25.remove_document(old_id)
        except Exception:
            pass

        # 插入新数据
        self.collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        # 更新 BM25
        for cid, txt in zip(chunk_ids, texts):
            self.bm25.add_document(cid, txt)

        return chunk_ids

    # ── DELETE ─────────────────────────────────────

    def remove_by_source(self, source_name: str) -> int:
        """删除指定源文件的所有 chunks。返回删除数。"""
        try:
            existing = self.collection.get(
                where={"source_file": source_name},
                include=["metadatas"]
            )
            if existing["ids"]:
                self.collection.delete(ids=existing["ids"])
                for old_id in existing["ids"]:
                    self.bm25.remove_document(old_id)
                return len(existing["ids"])
        except Exception:
            pass
        return 0

    def clear(self) -> int:
        """清空整个用户信息库。返回删除数。"""
        try:
            result = self.collection.get(include=["metadatas"])
            count = len(result["ids"]) if result["ids"] else 0
            if result["ids"]:
                self.collection.delete(ids=result["ids"])
            self.bm25 = SimpleBM25()
            return count
        except Exception:
            return 0

    # ── LIST ───────────────────────────────────────

    def get_stats(self) -> LibraryStats:
        """获取信息库统计。"""
        try:
            result = self.collection.get(include=["documents", "metadatas"])
            if not result["ids"]:
                return LibraryStats()

            total_chars = sum(len(d) for d in (result["documents"] or []))
            sources_map: Dict[str, Dict] = {}
            for i, mid in enumerate(result["ids"]):
                meta = result["metadatas"][i] or {}
                src = meta.get("source_file", "unknown")
                if src not in sources_map:
                    sources_map[src] = {
                        "source": src,
                        "chunks": 0,
                        "chars": 0,
                        "doc_type": meta.get("doc_type", ""),
                        "label": meta.get("label", "") or meta.get("resume_version", ""),
                    }
                sources_map[src]["chunks"] += 1
                sources_map[src]["chars"] += len(result["documents"][i] or "")

            return LibraryStats(
                total_documents=len(sources_map),
                total_chunks=len(result["ids"]),
                total_chars=total_chars,
                sources=list(sources_map.values()),
            )
        except Exception:
            return LibraryStats()

    # ── SEARCH ─────────────────────────────────────

    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Dict = None,
        use_bm25: bool = True,
    ) -> List[Dict]:
        """
        增强检索 — 向量相似度 + 可选 BM25 关键词 → 融合排序。

        Args:
            query: 检索查询
            n_results: 返回数量
            filters: 额外的 ChromaDB where 过滤条件
            use_bm25: 是否启用 BM25 关键词检索

        Returns:
            [{content, metadata, distance, bm25_score, combined_score}, ...]
        """
        if self.collection is None:
            return []

        # 1. 查询路由 → 自动生成过滤条件
        route_filters = self.router.route(query)
        merged_filters = dict(filters or {})
        if route_filters:
            # ChromaDB 的 where 用 $or 处理多个值
            for key, values in route_filters.items():
                if len(values) == 1:
                    merged_filters[key] = values[0]
                elif len(values) > 1:
                    merged_filters["$or"] = [
                        {key: v} for v in values
                    ]

        # 2. 向量检索
        try:
            query_emb = embed_query(query)
            vec_kwargs = {
                "query_embeddings": [query_emb],
                "n_results": n_results * 2,  # 多取，为融合留余量
            }
            if merged_filters:
                vec_kwargs["where"] = merged_filters

            vec_results = self.collection.query(**vec_kwargs)
        except Exception:
            return []

        if not vec_results["ids"] or not vec_results["ids"][0]:
            return []

        # 3. 组装向量结果
        docs = []
        seen_ids = set()
        for i in range(len(vec_results["ids"][0])):
            cid = vec_results["ids"][0][i]
            dist = vec_results["distances"][0][i] if vec_results["distances"] else 0
            docs.append({
                "content": vec_results["documents"][0][i],
                "metadata": vec_results["metadatas"][0][i] if vec_results["metadatas"] else {},
                "distance": round(dist, 4),
                "bm25_score": 0,
                "combined_score": 0,
                "chunk_id": cid,
            })
            seen_ids.add(cid)

        # 4. BM25 关键词检索
        if use_bm25:
            bm25_results = self.bm25.search(query, k=n_results * 2)
            for bm_id, bm_score in bm25_results:
                if bm_id in seen_ids:
                    # 已有，加分
                    for d in docs:
                        if d["chunk_id"] == bm_id:
                            d["bm25_score"] = round(bm_score, 4)
                            break
                else:
                    # BM25 找到了向量没找到的
                    try:
                        bm_data = self.collection.get(
                            ids=[bm_id],
                            include=["documents", "metadatas"]
                        )
                        if bm_data["ids"]:
                            docs.append({
                                "content": bm_data["documents"][0],
                                "metadata": bm_data["metadatas"][0] if bm_data["metadatas"] else {},
                                "distance": 1.0,
                                "bm25_score": round(bm_score, 4),
                                "combined_score": 0,
                                "chunk_id": bm_id,
                            })
                    except Exception:
                        pass

        # 5. 融合排序 — Reciprocal Rank Fusion
        vec_ranked = sorted(docs, key=lambda d: d["distance"])
        bm25_ranked = sorted(docs, key=lambda d: d["bm25_score"], reverse=True)

        K = 60  # RRF constant
        for i, d in enumerate(vec_ranked):
            d["combined_score"] += 1.0 / (K + i + 1)
        for i, d in enumerate(bm25_ranked):
            d["combined_score"] += 1.0 / (K + i + 1)

        docs.sort(key=lambda d: d["combined_score"], reverse=True)
        return docs[:n_results]

    # ── STEP-SPECIFIC SEARCH ───────────────────────

    def search_for_step(self, step: str, n_results: int = 5) -> Dict:
        """
        根据工作流步骤，自动选择最优检索策略。

        返回完整的用户上下文，供 Prompt 注入。
        """
        step_queries = {
            "ats_check":       ("技能 技术栈 经验", {"doc_type": "resume"}),
            "match_score":     ("技能 项目 经验 成就", {"$or": [{"doc_type": "resume"}, {"doc_type": "project"}]}),
            "jd_analysis":     ("", {}),  # 不需要用户信息
            "resume_diagnosis": ("", {}),  # 全局检索
            "learning_plan":   ("技能 短板 缺失", {"doc_type": "resume"}),
            "interview_prep":  ("项目经历 成就 经验", {"doc_type": "project"}),
            "mock_interview":  ("经验 弱项", {"doc_type": "resume"}),
            "offer_eval":      ("技能 成就 竞争力", {"doc_type": "project"}),
        }

        query_template, default_filters = step_queries.get(step, ("", {}))
        if not query_template:
            return {"query": "", "results": []}

        results = self.search(query_template, n_results=n_results, filters=default_filters)
        return {
            "query": query_template,
            "results": results,
        }

    def assemble_context(self, step: str, n_results: int = 5) -> str:
        """
        为指定步骤组装「用户上下文」——可直接注入 Prompt 的文本块。

        返回格式化的字符串，包含检索到的用户信息摘要。
        """
        search_result = self.search_for_step(step, n_results)
        results = search_result.get("results", [])

        if not results:
            return ""

        parts = [f"## 📂 用户信息库（自动检索，共 {len(results)} 条相关记录）\n"]
        for i, r in enumerate(results, 1):
            meta = r["metadata"]
            source = meta.get("source_file", "")
            section = meta.get("section", "")
            doc_type = meta.get("doc_type", "")
            label_parts = [p for p in [source, section, doc_type] if p]
            label = " › ".join(label_parts) if label_parts else "未知"
            parts.append(f"### [{i}] {label}")
            parts.append(r["content"])
            parts.append("")

        return "\n".join(parts)
