import streamlit as st
import json
from utils.llm_client import analyze_prediction_topic, chat_with_agent
from utils.topic_data import update_topic_knowledge, get_topic_summary, is_knowledge_loaded, load_topic_data, get_field_mapping
from utils.crypto_data import get_prediction_markets
import pandas as pd

st.sidebar.title("W3Intelligence")
st.title("🔮 Prediction Markets & AI Tools")

tab1, tab2, tab3, tab4 = st.tabs(["Prediction Markets", "Topic Analyzer", "Knowledge Management", "AI Chat"])

with tab1:
    st.subheader("Trending Prediction Markets")
    markets = get_prediction_markets()
    if "error" not in markets:
        st.markdown("""
        <style>
        .prediction-table {
            width: 100%;
            border-collapse: collapse;
        }
        .prediction-table th, .prediction-table td {
            border: 1px solid #555;
            padding: 8px 12px;
            text-align: left;
        }
        .prediction-table th {
            background-color: #5a5a5a;
            color: #ffffff;
            font-weight: bold;
        }
        .prediction-table a {
            color: #4CAF50;
            text-decoration: none;
        }
        .prediction-table a:hover {
            text-decoration: underline;
        }
        </style>
        """, unsafe_allow_html=True)
        
        html_table = "<table class='prediction-table'><tr><th>Topic</th><th>Platform</th><th>Yes %</th><th>No %</th><th>Volume</th></tr>"
        for m in markets:
            topic_link = f"<a href='{m['buy_link']}' target='_blank'>{m['topic']}</a>" if m['buy_link'] else m['topic']
            html_table += f"<tr><td>{topic_link}</td><td>{m['platform']}</td><td>{m['yes_prob']}%</td><td>{m['no_prob']}%</td><td>{m['volume']}</td></tr>"
        html_table += "</table>"
        st.markdown(html_table, unsafe_allow_html=True)
    else:
        st.error("Failed to load prediction markets")

with tab2:
    st.subheader("📊 Prediction Topic Analyzer")
    st.markdown("""
    Input prediction materials and let the AI analyze:
    - Sensitivity level (LOW/MEDIUM/HIGH)
    - Market eligibility (YES/NO)
    - Risk assessment
    - Handling suggestions
    
    **Note:** If you have uploaded a knowledge file, the AI will use the classification rules from the file.
    """)

    knowledge_status = "✅" if is_knowledge_loaded() else "❌"
    st.markdown(f"**Knowledge File Status:** {knowledge_status} {'Loaded' if is_knowledge_loaded() else 'Not loaded'}")

    material = st.text_area("Enter prediction material:", height=200)

    if st.button("Analyze"):
        if material:
            with st.spinner("Analyzing..."):
                result = analyze_prediction_topic(material)
                try:
                    if isinstance(result, str):
                        result = json.loads(result)
                    
                    st.markdown("### Analysis Result")
                    
                    sensitivity_color = {
                        "LOW": "green",
                        "MEDIUM": "yellow",
                        "HIGH": "red"
                    }
                    
                    eligibility_icon = "✅" if result["market_eligibility"] == "YES" else "❌"
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Sensitivity Level:** <span style='color:{sensitivity_color.get(result['sensitivity_level'], 'gray')}'>{result['sensitivity_level']}</span>", unsafe_allow_html=True)
                        st.markdown(f"**Market Eligibility:** {eligibility_icon} {result['market_eligibility']}")
                    
                    with col2:
                        st.markdown(f"**Sensitivity Reason:** {result['sensitivity_reason']}")
                    
                    st.markdown(f"**Eligibility Reason:** {result['eligibility_reason']}")
                    st.markdown(f"**Risk Assessment:** {result['risk_assessment']}")
                    st.markdown(f"**Suggestion:** {result['suggestion']}")
                
                except json.JSONDecodeError:
                    st.error("Error parsing analysis result")
                    st.text(result)
                except KeyError as e:
                    st.error(f"Missing field in result: {e}")
                    st.text(result)
        else:
            st.warning("Please enter prediction material")

with tab3:
    st.subheader("📚 Knowledge Management")
    st.markdown("""
    Upload an Excel file with **2 sheets**:
    - **Sheet 1**: Topic Classification Tree
    - **Sheet 2**: Keyword Bank
    
    The AI will automatically detect column names (supports Chinese/English):
    - Topic/话题/主题: Main content to classify
    - Category/类别/分类: Category label
    - Risk Level/风险等级/级别: Risk assessment (LOW/MEDIUM/HIGH or custom)
    - Remark/备注/说明: Additional notes for understanding
    
    After uploading, the AI will learn from this knowledge to provide more accurate analysis.
    """)

    uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type="xlsx")

    if uploaded_file is not None:
        if st.button("Load Knowledge"):
            with st.spinner("Loading and processing knowledge..."):
                result = update_topic_knowledge(uploaded_file)
                if result["success"]:
                    st.success(result["message"])
                    st.info(f"Loaded {result['topic_count']} topics and {result['keyword_count']} keywords")
                    
                    if "field_mapping" in result:
                        st.subheader("Auto-detected Field Mapping")
                        mapping = result["field_mapping"]
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Sheet 1: {mapping['sheet1']['name']}**")
                            for field, col_name in mapping['sheet1']['mapping'].items():
                                st.markdown(f"- {field}: `{col_name}`")
                        with col2:
                            st.markdown(f"**Sheet 2: {mapping['sheet2']['name']}**")
                            for field, col_name in mapping['sheet2']['mapping'].items():
                                st.markdown(f"- {field}: `{col_name}`")
                else:
                    st.error(result["message"])

    st.markdown("---")

    st.subheader("Knowledge Summary")
    if is_knowledge_loaded():
        summary = get_topic_summary()
        st.markdown(summary)
        
        classification_tree, word_bank = load_topic_data()
        
        if classification_tree:
            st.subheader("Topic Classification Tree")
            df_class = pd.DataFrame(classification_tree)
            st.dataframe(df_class, use_container_width=True)
        
        if word_bank:
            st.subheader("Keyword Bank")
            df_words = pd.DataFrame(word_bank)
            st.dataframe(df_words, use_container_width=True)
        
        mapping = get_field_mapping()
        if mapping:
            st.subheader("Field Mapping")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Sheet 1: {mapping['sheet1']['name']}**")
                st.markdown(f"Columns: {', '.join(mapping['sheet1']['columns'])}")
            with col2:
                st.markdown(f"**Sheet 2: {mapping['sheet2']['name']}**")
                st.markdown(f"Columns: {', '.join(mapping['sheet2']['columns'])}")
    else:
        st.info("No knowledge file loaded. Upload an Excel file to get started.")
    
    st.markdown("---")

    st.subheader("Sample Excel Template")
    st.markdown("""
    **Sheet 1 (Topic Classification):**
    
    | 话题 | 类别 | 风险等级 | 备注 |
    |------|------|----------|------|
    | Bitcoin ETF Approval | Crypto | LOW | General market trend |
    | Company X Insider Trading | Finance | HIGH | Involves illegal activities |
    | US Presidential Election | Politics | MEDIUM | Public but sensitive |
    
    **Sheet 2 (Keyword Bank):**
    
    | 关键词 | 类别 | 风险等级 | 备注 |
    |--------|------|----------|------|
    | insider trading | Finance | HIGH | Illegal activity |
    | SEC investigation | Regulation | MEDIUM | Regulatory concern |
    | bankruptcy | Finance | HIGH | High impact |
    
    **Supported column names (auto-detection):**
    - Topic: topic, 话题, 主题, subject, question, title
    - Category: category, 类别, 分类, 类型, class, tag
    - Risk: risk, 风险, 级别, level, score, 危险
    - Remark: remark, 备注, 说明, 描述, note, comment
    """)

with tab4:
    st.subheader("🤖 Web3 AI Assistant")
    st.markdown("""
    Chat with our AI assistant about:
    - Cryptocurrency market analysis
    - Traditional finance insights
    - RWA trends
    - Prediction markets
    - Blockchain technology
    """)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask about Web3...")
    
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                history = [{"user": m["content"], "assistant": st.session_state.chat_history[i+1]["content"]} 
                          for i, m in enumerate(st.session_state.chat_history) 
                          if m["role"] == "user" and i+1 < len(st.session_state.chat_history)]
                response = chat_with_agent(user_input, history)
                st.markdown(response)
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})

    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()
