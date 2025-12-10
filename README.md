# 智能课程助教系统

本仓库基于RAG的课程问答和习题生成系统。数据库构建所用资料全部来自于SJTU CS499课程，版权归属Prof.Long @SJTU 

## 功能特性

- 文档问答：基于课程文档进行智能问答
- 自动习题生成：根据课程内容自动生成练习题
- 混合检索：结合BM25和向量检索提升准确率
- 图形化界面：使用Streamlit构建的用户界面

## 安装和运行

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 准备数据
将课程文档（PDF、PPT、DOCX、TXT）放入data目录。

### 3. 构建知识库
```bash
python main.py  # 或使用界面中的重建知识库按钮
```

### 4. 启动界面
```bash
streamlit run uis/app.py
```

## 使用说明

1. 在浏览器中打开界面
2. 点击"重建知识库"加载文档
3. 在对话框中提问或点击"生成习题"
4. 可在侧边栏启用混合检索以提升准确率

## 项目结构

- `uis/`: 图形化界面模块
- `hybrid_retrieval.py`: 混合检索实现
- `rag_agent.py`: RAG代理核心逻辑
- `vector_store.py`: 向量数据库管理
- `document_loader.py`: 文档加载和处理
- `data/`: 课程文档存放目录

## 配置

在config.py中修改API密钥和其他参数。