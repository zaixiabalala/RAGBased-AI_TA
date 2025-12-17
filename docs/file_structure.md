# 项目文件结构

## 目录树结构

```
RAGBased-AI_TA/
│
├── data/                          # 课程文档数据目录
│   └── (PDF, PPTX, DOCX, TXT等课程材料)
│
├── vector_db/                     # 向量数据库存储目录
│   └── (ChromaDB持久化数据)
│
├── uis/                           # 用户界面模块
│   ├── __init__.py
│   ├── app.py                     # Streamlit Web界面主程序
│   └── utils.py                   # 界面工具函数（知识库重建、习题生成等）
│
├── docs/                          # 项目文档目录
│   ├── file_structure.md          # 文件结构说明（本文件）
│   └── function_diagram.md        # 主要函数示意图
│
├── config.py                      # 配置文件（API密钥、模型参数等）
├── document_loader.py             # 文档加载器（支持PDF、PPTX、DOCX、TXT、图片）
├── text_splitter.py               # 文本切分器（将长文档切分为块）
├── vector_store.py                # 向量数据库管理（ChromaDB + OpenAI Embedding）
├── hybrid_retrieval.py            # 混合检索（BM25 + 向量检索）
├── rag_agent.py                   # RAG代理核心逻辑（检索、生成回答）
├── process_data.py                # 数据处理脚本（构建知识库）
├── main.py                        # 命令行交互入口
├── requirements.txt               # Python依赖包
└── README.md                      # 项目说明文档
```

## 核心模块说明

### 1. 配置模块 (config.py)
存储项目的全局配置参数：
- **API配置**：OpenAI API密钥、Base URL、模型名称
- **数据目录**：数据存放路径、向量数据库路径
- **文本处理参数**：分块大小、重叠长度
- **RAG参数**：检索top-k数量

### 2. 文档处理模块

#### document_loader.py
负责加载各种格式的课程文档：
- **支持格式**：PDF、PPTX、DOCX、TXT、JPG/PNG（OCR）
- **核心功能**：
  - `load_pdf()`: 加载PDF文件，按页提取内容
  - `load_pptx()`: 加载PPT文件，按幻灯片提取内容
  - `load_docx()`: 加载Word文档
  - `load_txt()`: 加载纯文本文件
  - `load_image()`: 使用EasyOCR提取图片中的文字
  - `load_document()`: 统一文档加载接口
  - `load_all_documents()`: 批量加载数据目录下所有文档

#### text_splitter.py
将长文档切分为适合处理的文本块：
- **核心功能**：
  - `split_text()`: 按指定大小切分文本，保持上下文重叠
  - `split_documents()`: 批量处理文档切分
- **切分策略**：
  - PDF/PPTX：按页/幻灯片切分（不再二次切分）
  - DOCX/TXT：按chunk_size切分，在句子边界处断开

### 3. 向量存储模块 (vector_store.py)
管理文档的向量化存储和检索：
- **数据库**：ChromaDB（持久化向量数据库）
- **Embedding模型**：OpenAI text-embedding-v3
- **核心功能**：
  - `get_embedding()`: 获取文本的向量表示
  - `add_documents()`: 将文档块添加到向量数据库
  - `search()`: 向量相似度搜索
  - `get_all_documents()`: 获取所有文档（用于构建BM25索引）
  - `clear_collection()`: 清空数据库

### 4. 混合检索模块 (hybrid_retrieval.py)
结合BM25稀疏检索和向量密集检索：
- **检索方法**：
  - BM25检索：基于关键词匹配的传统检索
  - 向量检索：基于语义相似度的深度学习检索
- **融合算法**：倒数排名融合（Reciprocal Rank Fusion, RRF）
- **核心功能**：
  - `build_bm25_index()`: 构建BM25索引（使用jieba分词）
  - `bm25_search()`: BM25检索
  - `vector_search()`: 向量检索
  - `reciprocal_rank_fusion()`: RRF融合排序
  - `hybrid_search()`: 混合检索主函数

### 5. RAG代理模块 (rag_agent.py)
系统的核心智能代理：
- **LLM模型**：Qwen3-max（通过OpenAI兼容接口）
- **核心功能**：
  - `retrieve_context()`: 检索相关上下文（支持混合检索）
  - `generate_response()`: 基于上下文生成回答
  - `answer_question()`: 完整的问答流程（检索+生成）
  - `chat()`: 命令行交互式对话
- **提示词设计**：
  - System Prompt：定义助教角色和回答策略
  - User Prompt：包含课程材料、学生问题、引用要求

### 6. 数据处理脚本 (process_data.py)
一键构建知识库的脚本：
- **处理流程**：
  1. 加载data目录下的所有文档
  2. 切分文档为合适的块
  3. 生成向量并存储到ChromaDB
- **使用方式**：`python process_data.py`

### 7. 命令行接口 (main.py)
提供命令行交互式对话：
- **功能**：初始化RAG Agent并启动对话循环
- **使用方式**：`python main.py`

### 8. Web界面模块 (uis/)

#### app.py
基于Streamlit的图形化界面：
- **功能模块**：
  - 侧边栏控制面板（检索设置、知识库管理）
  - 聊天界面（问答交互）
  - 功能按钮（生成习题、检索模式）
  - 消息历史管理
- **使用方式**：`streamlit run uis/app.py`

#### utils.py
界面辅助工具函数：
- `get_agent()`: 初始化并缓存RAG Agent（支持混合检索开关）
- `rebuild_knowledge_base()`: 重建知识库
- `generate_quiz()`: 自动生成习题
- `get_weighted_random_content()`: 加权随机选择内容（用于出题）

## 数据流向

```
1. 文档加载流程：
   data/ (原始文档) 
   → DocumentLoader (加载) 
   → TextSplitter (切分) 
   → VectorStore (向量化+存储) 
   → vector_db/ (持久化)

2. 问答流程：
   用户问题 
   → RAGAgent.retrieve_context() (检索)
   → HybridRetrieval/VectorStore (混合检索/向量检索)
   → RAGAgent.generate_response() (LLM生成)
   → 返回答案

3. 习题生成流程：
   随机/指定主题 
   → 检索相关内容 
   → LLM生成习题（JSON格式）
   → 展示给用户
```

## 依赖关系

```
main.py / uis/app.py (入口)
    ↓
rag_agent.py (核心代理)
    ↓
├── vector_store.py (向量检索)
├── hybrid_retrieval.py (混合检索，可选)
└── config.py (配置)

process_data.py (数据处理)
    ↓
├── document_loader.py (文档加载)
├── text_splitter.py (文本切分)
├── vector_store.py (向量存储)
└── config.py (配置)
```

## 配置文件说明

### requirements.txt
项目所需的Python包：
- `streamlit`: Web界面框架
- `openai`: OpenAI API客户端
- `chromadb`: 向量数据库
- `PyPDF2`: PDF文件处理
- `python-pptx`: PPTX文件处理
- `docx2txt`: DOCX文件处理
- `easyocr`: OCR文字识别
- `rank-bm25`: BM25检索算法
- `jieba`: 中文分词
- `tqdm`: 进度条显示

### .vscode/settings.json
VS Code编辑器配置文件（可选）

## 扩展说明

### 如何添加新的文档格式支持？
1. 在 `document_loader.py` 中添加新的加载方法（如 `load_markdown()`）
2. 在 `supported_formats` 列表中添加新格式扩展名
3. 在 `load_document()` 方法中添加对应的处理分支

### 如何切换不同的LLM模型？
1. 修改 `config.py` 中的 `MODEL_NAME` 参数
2. 如需使用非OpenAI兼容的模型，需修改 `rag_agent.py` 中的客户端初始化代码

### 如何调整检索效果？
1. 调整 `config.py` 中的 `TOP_K` 参数（检索文档数量）
2. 启用混合检索（在界面中勾选或设置 `use_hybrid_retrieval=True`）
3. 调整 `CHUNK_SIZE` 和 `CHUNK_OVERLAP` 参数优化分块策略
4. 修改 `hybrid_retrieval.py` 中的RRF融合权重

## 注意事项

1. **API密钥安全**：`config.py` 中的API密钥不应提交到公开仓库
2. **数据隐私**：`data/` 目录下的课程材料受版权保护
3. **向量数据库**：`vector_db/` 目录包含索引数据，首次使用需运行 `process_data.py` 构建
4. **依赖安装**：首次运行前需执行 `pip install -r requirements.txt`
5. **内存占用**：处理大量文档时注意内存使用，可调整批处理大小
