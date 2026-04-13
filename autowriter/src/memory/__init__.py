"""记忆系统模块

提供三层记忆模型：
- L1 索引层 (index_layer): 管理 memory_index.md
- L2 详情层 (detail_layer): 管理 memories/*.md
- L3 状态层 (state_layer): 管理 state.json
- 检索器 (retriever): 组合三层实现统一检索
- 记忆整合器 (memory_integrator): Auto Dream 功能
"""

from .index_layer import IndexLayer, IndexEntry
from .detail_layer import DetailLayer
from .state_layer import StateLayer
from .retriever import MemoryRetriever
from .memory_integrator import MemoryIntegrator, ExtractedEntity

__all__ = [
    "IndexLayer",
    "IndexEntry",
    "DetailLayer",
    "StateLayer",
    "MemoryRetriever",
    "MemoryIntegrator",
    "ExtractedEntity"
]
