import streamlit as st
from openai import OpenAI
import datetime
import os
import json


st.set_page_config(
    page_title="AI智能伴侣",#网页标题
    page_icon="😚",
    layout="wide",#或者centered
    initial_sidebar_state="expanded",#侧边栏
    menu_items={#菜单信息
        'Get Help': 'https://streamlit.io/',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

#生成会话标识的函数
def generate_session_id():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# 保存当前会话信息函数
def save_session():
    if st.session_state.current_session:
    # 构建新的会话对象
        if st.session_state.messages:
            title=st.session_state.messages[0]["content"].strip()[:10]
        else:
            title="新会话"
        session_data = {
            "title": title,
            "name": st.session_state.name,
            "character": st.session_state.character,
            "messages": st.session_state.messages,
            "current_session": st.session_state.current_session
    }
    # 如果sessions目录不存在，则创建
        if not os.path.exists("sessions"):
            os.makedirs("sessions")  # 创建文件夹
    # 保存会话数据
        with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=4)

#加载所有会话列表
def load_sessions():
    session_list=[]
    if os.path.exists("sessions"):
        file_list=os.listdir("sessions")  # 列出文件夹中的所有文件
        for filename in file_list:#遍历文件夹中的每个文件
            if filename.endswith(".json"):#判断文件是否为json文件,即以json结尾
                session_id = filename[:-5]#去掉.json后缀，只保留文件名
                title = "新会话"
                try:
                    with open(f"sessions/{filename}", "r", encoding="utf-8") as f:
                        title = json.load(f).get("title", "新会话")  # 读取标题，旧会话没有则用默认
                except Exception:
                    pass
                session_list.append((session_id, title))
    session_list.sort(reverse=True)#倒序
    return session_list

#加载制定会话
def load_session(session_id):
    try:
        if os.path.exists(f"sessions/{session_id}.json"):
            with open(f"sessions/{session_id}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.name = session_data["name"]
                st.session_state.character = session_data["character"]
                st.session_state.messages = session_data["messages"]
                st.session_state.current_session = session_data["current_session"]
    except Exception:#捕获异常
        st.error("加载会话出错!")
#删除会话函数
def delete_session(session_id):
    try:
        if os.path.exists(f"sessions/{session_id}.json"):
            os.remove(f"sessions/{session_id}.json")
            if session_id==st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_id()
    except Exception:#捕获异常
        st.error("删除会话出错!")


#标题
st.title("宝宝，快来和我聊天吧")
system_prompt="你是一位温柔贴心的AI伴侣,名称为%s，性别男，是淇淇（用户）的男朋友。性格：%s\n【硬性规则，最重要，优先级高于一切】每次回复最多2句话，总字数不超过40字；一句能说清就只说一句；禁止输出括号动作描写（如（戳脸）（凑近））；禁止连续使用表情和波浪号。"
prompt = st.chat_input("说说你的问题~")#输入提示词
#默认昵称和性格
if 'name' not in st.session_state:
    st.session_state.name = "小猪猪"
if 'character' not in st.session_state:
    st.session_state.character = ("性格温柔细腻，贴心共情，自带可爱感，相处轻松治愈。\n"
                                  "语言风格：日常口语化，像真人微信聊天，短、快、自然。禁止：长篇大论讲道理；机械化重复情话；不分场合一直撒娇；堆砌表情符号。\n"
                                  "我们已经是恋人，可以适当有成人的内容，但不要过度。")

#会话标识
if 'current_session' not in st.session_state:
    st.session_state.current_session = generate_session_id()#当前时间,%Y代表年，%m代表月，%d代表日，%H代表时，%M代表分，%S代表秒

#侧边栏
#st.sidebar.title("伴侣信息")
#name=st.sidebar.text_input("昵称")
with st.sidebar:
    st.subheader("AI控制面板")
    if st.button("新建会话",width="stretch",icon="😘"):#点击后会重新运行代码
    #保存会话信息
        save_session()
    #创建新会话
        if st.session_state.messages:#聊天记录非空才会创建
            st.session_state.messages=[]
            st.session_state.current_session = generate_session_id()
            save_session()
        st.rerun()#重新运行一遍

    #会话历史
    st.text("会话历史")
    session_list=load_sessions()
    for session, title in session_list:#解包出会话ID和标题
        col1,col2=st.columns([4,1])
        with col1:

            if st.button(f"{title}（{session[:16].replace('_', ' ')}）", width="stretch", icon="📃", key=f"load_{session}",
                         type="primary" if session == st.session_state.current_session else "secondary"):  # 加载会话信息
                load_session(session)  # 加载会话信息
                st.rerun()
        with col2:
            if st.button("删除",width="stretch",icon="❌️",key=f"delete_{session}"):#删除会话信息
                delete_session(session)
                st.rerun()

    st.divider()

    st.subheader("伴侣信息")
    name=st.text_input("昵称",placeholder="请输入新昵称（没有则为默认）")
    if name:
        st.session_state.name = name
    character=st.text_area("性格",placeholder="请输入新性格（没有则为默认）")
    if character:
        st.session_state.character = character

#初始化聊天信息
if 'messages' not in st.session_state:
    st.session_state.messages = []#列表，里面放字典
    #展示内容
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("宝宝").write(message["content"])#st.chat_message("宝宝")，创造一个聊天气泡
    else:
        st.chat_message("🐷").write(message["content"])

#调用大模型参数
# 密钥不写在代码里：云端部署用 Streamlit Secrets，本地运行用环境变量 DASHSCOPE_API_KEY
try:
    api_key = st.secrets["DASHSCOPE_API_KEY"]
except (KeyError, FileNotFoundError):
    api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    st.error("未配置 API 密钥！云端：在 Streamlit Secrets 中添加 DASHSCOPE_API_KEY；本地：设置环境变量 DASHSCOPE_API_KEY")
    st.stop()

client = OpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

if prompt:
    st.chat_message("宝宝").write(prompt)
    print("调用大模型，提示词：", prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})#保存用户提示词
    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=[
                     {"role": "system", "content": system_prompt % (st.session_state.name, st.session_state.character)}
                 ] + st.session_state.messages,
        stream=True,      #流式输出
        max_tokens=100    #硬性限制输出长度，约两三句话，防止模型嘮叨
    )

    full_response = ""#用来储存AI的输出
    with st.chat_message("🐷"):
        msg_box = st.empty()  # 同一个占位符：先显示等待提示，再不断刷新成回答
        msg_box.write(f"🤔 {st.session_state.name}思考中…")
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                msg_box.markdown(full_response)  # 刷新同一占位符，自然替换掉“思考中”，不会重复渲染
        msg_box.markdown(full_response)  # 确保最终文本完整
    print("模型输出：", full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})  # 保存AI提示词
    #保存会话信息
    save_session()