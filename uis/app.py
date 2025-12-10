import streamlit as st
import json
from utils import get_agent, rebuild_knowledge_base, generate_quiz

# 页面配置
st.set_page_config(
    page_title="智能课程助教",
    page_icon="🎓",
    layout="wide"
)

# 侧边栏控制面板
with st.sidebar:
    st.title("控制面板")

    st.subheader("检索设置")
    use_hybrid = st.checkbox("启用混合检索", value=False,
                            help="结合BM25和向量检索提升准确率")

    st.subheader("知识库管理")
    if st.button("重建知识库", type="primary"):
        with st.status("处理中...", expanded=True) as status:
            st.write("正在读取文档...")
            success, msg = rebuild_knowledge_base()
            if success:
                status.update(label="完成", state="complete", expanded=False)
                st.success(msg)
                st.cache_resource.clear()
            else:
                status.update(label="失败", state="error")
                st.error(msg)

    st.subheader("功能")
    st.info("支持问答和自动出题")

# 主界面
st.title("🎓 智能课程助教系统")
st.caption("基于RAG的课程问答助手")

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好！我是你的课程助教。可以问我问题或点击下方按钮生成习题。"}
    ]

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 功能按钮区域
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🤖 生成习题", use_container_width=True):
        with st.spinner("正在生成习题..."):
            try:
                agent = get_agent(use_hybrid=use_hybrid)
                quiz_content = generate_quiz(agent)

                # 尝试解析JSON
                try:
                    quiz_data = json.loads(quiz_content)
                    quiz_text = f"""
### 📝 练习题

**{quiz_data['question']}**

{quiz_data['options'][0]}  
{quiz_data['options'][1]}  
{quiz_data['options'][2]}  
{quiz_data['options'][3]}

**正确答案：{quiz_data['correct_answer']}**  
**解析：{quiz_data['explanation']}**
"""
                except json.JSONDecodeError:
                    quiz_text = f"### 📝 生成的习题\n\n{quiz_content}"

                with st.chat_message("assistant"):
                    st.markdown(quiz_text)

                st.session_state.messages.append({"role": "assistant", "content": quiz_text})

            except Exception as e:
                st.error(f"生成习题失败: {str(e)}")

with col2:
    if st.button("🔍 检索模式", use_container_width=True):
        st.info("请在下方输入框提问，系统将基于课程文档回答")

# 用户输入
if prompt := st.chat_input("请输入你的问题..."):
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 获取回答
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        try:
            agent = get_agent(use_hybrid=use_hybrid)

            with st.spinner("正在查阅资料..."):
                response = agent.answer_question(prompt, chat_history=st.session_state.messages[:-1])

            message_placeholder.markdown(response)

        except Exception as e:
            error_msg = f"发生错误: {str(e)}"
            st.error(error_msg)
            response = error_msg

    # 保存助手消息
    st.session_state.messages.append({"role": "assistant", "content": response})