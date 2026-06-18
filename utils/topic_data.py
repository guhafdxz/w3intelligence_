import pandas as pd
import os
import re
from typing import List, Dict, Optional

DATA_DIR = "data"

topic_classification_tree = []
topic_word_bank = []
field_mapping = {}


def filter_chinese(text: str) -> str:
    """过滤掉中文字符，只保留英文内容"""
    if not text:
        return ""
    # 匹配中文字符（包括中文标点）
    chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]+')
    # 移除中文内容
    filtered = chinese_pattern.sub('', text)
    # 清理多余的空格和换行
    filtered = re.sub(r'\n\s*\n', '\n', filtered)
    filtered = filtered.strip()
    return filtered


def translate_chinese_to_english(text: str) -> str:
    """将常见的中文敏感词翻译成英文"""
    if not text:
        return ""
    
    # 常见中文敏感词翻译映射
    translations = {
        "内幕交易": "insider trading",
        "欺诈": "fraud",
        "破产": "bankruptcy",
        "洗钱": "money laundering",
        "腐败": "corruption",
        "非法": "illegal",
        "犯罪": "crime",
        "恐怖主义": "terrorism",
        "毒品": "drugs",
        "色情": "pornography",
        "赌博": "gambling",
        "高": "HIGH",
        "中": "MEDIUM",
        "低": "LOW",
        "金融": "Finance",
        "政治": "Politics",
        "法律": "Legal",
        "监管": "Regulation"
    }
    
    result = text
    for cn, en in translations.items():
        result = result.replace(cn, en)
    
    return result


def init_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_topic_data() -> tuple:
    return topic_classification_tree, topic_word_bank


def detect_field_type(column_name: str) -> str:
    name_lower = column_name.lower().strip()
    
    topic_keywords = ['topic', '话题', '主题', 'subject', 'question', 'query', 'title']
    category_keywords = ['category', '类别', '分类', '类型', 'class', 'tag', 'group']
    risk_keywords = ['risk', '风险', '级别', 'level', 'score', '危险']
    remark_keywords = ['remark', '备注', '说明', '描述', 'note', 'comment', 'detail']
    
    for kw in topic_keywords:
        if kw in name_lower:
            return 'topic'
    for kw in category_keywords:
        if kw in name_lower:
            return 'category'
    for kw in risk_keywords:
        if kw in name_lower:
            return 'risk_level'
    for kw in remark_keywords:
        if kw in name_lower:
            return 'remark'
    
    return 'unknown'


def map_columns(df: pd.DataFrame) -> Dict:
    mapping = {
        'topic': None,
        'category': None,
        'risk_level': None,
        'remark': None
    }
    
    for col in df.columns:
        field_type = detect_field_type(str(col))
        if field_type in mapping and mapping[field_type] is None:
            mapping[field_type] = col
    
    if mapping['topic'] is None and len(df.columns) > 0:
        mapping['topic'] = df.columns[0]
    
    return mapping


def parse_excel(file_path: str) -> tuple:
    try:
        xls = pd.ExcelFile(file_path)
        sheets = xls.sheet_names
        
        if len(sheets) < 2:
            return None, None, None, "Excel file must contain at least 2 sheets"
        
        classification_df = pd.read_excel(xls, sheet_name=0)
        word_bank_df = pd.read_excel(xls, sheet_name=1)
        
        sheet1_mapping = map_columns(classification_df)
        sheet2_mapping = map_columns(word_bank_df)
        
        global field_mapping
        field_mapping = {
            'sheet1': {
                'name': sheets[0],
                'columns': list(classification_df.columns),
                'mapping': sheet1_mapping
            },
            'sheet2': {
                'name': sheets[1],
                'columns': list(word_bank_df.columns),
                'mapping': sheet2_mapping
            }
        }
        
        classification_data = []
        for _, row in classification_df.iterrows():
            topic_col = sheet1_mapping['topic']
            cat_col = sheet1_mapping['category']
            risk_col = sheet1_mapping['risk_level']
            remark_col = sheet1_mapping['remark']
            
            record = {
                "topic": str(row.get(topic_col, "")) if topic_col else "",
                "category": str(row.get(cat_col, "")) if cat_col else "",
                "risk_level": str(row.get(risk_col, "")) if risk_col else "",
                "remark": str(row.get(remark_col, "")) if remark_col else ""
            }
            
            if record["topic"] and record["topic"] != "nan":
                classification_data.append(record)
        
        word_bank_data = []
        for _, row in word_bank_df.iterrows():
            topic_col = sheet2_mapping['topic']
            cat_col = sheet2_mapping['category']
            risk_col = sheet2_mapping['risk_level']
            remark_col = sheet2_mapping['remark']
            
            record = {
                "keyword": str(row.get(topic_col, "")) if topic_col else "",
                "category": str(row.get(cat_col, "")) if cat_col else "",
                "risk_level": str(row.get(risk_col, "")) if risk_col else "",
                "remark": str(row.get(remark_col, "")) if remark_col else ""
            }
            
            if record["keyword"] and record["keyword"] != "nan":
                word_bank_data.append(record)
        
        return classification_data, word_bank_data, field_mapping, None
    
    except Exception as e:
        return None, None, None, str(e)


def update_topic_knowledge(file_path: str) -> Dict:
    init_data_dir()
    
    classification_data, word_bank_data, mapping_info, error = parse_excel(file_path)
    
    if error:
        return {"success": False, "message": error}
    
    global topic_classification_tree, topic_word_bank
    topic_classification_tree = classification_data
    topic_word_bank = word_bank_data
    
    result = {
        "success": True,
        "message": f"Successfully loaded {len(classification_data)} topics and {len(word_bank_data)} keywords",
        "topic_count": len(classification_data),
        "keyword_count": len(word_bank_data)
    }
    
    if mapping_info:
        result["field_mapping"] = mapping_info
    
    return result


def get_field_mapping() -> Dict:
    return field_mapping


def get_topic_summary() -> str:
    categories = {}
    risk_levels = {}
    
    for item in topic_classification_tree:
        cat = item.get("category", "Uncategorized")
        risk = item.get("risk_level", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1
        risk_levels[risk] = risk_levels.get(risk, 0) + 1
    
    for item in topic_word_bank:
        cat = item.get("category", "Uncategorized")
        risk = item.get("risk_level", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1
        risk_levels[risk] = risk_levels.get(risk, 0) + 1
    
    summary = "**Topic Classification Knowledge:**\n\n"
    
    if categories:
        summary += "Categories:\n"
        for cat, count in categories.items():
            summary += f"- {cat}: {count} items\n"
    
    if risk_levels:
        summary += "\nRisk Levels:\n"
        for risk, count in risk_levels.items():
            summary += f"- {risk}: {count} items\n"
    
    return summary


def get_knowledge_prompt() -> str:
    if not topic_classification_tree and not topic_word_bank:
        return ""
    
    prompt_parts = []
    
    if topic_classification_tree:
        prompt_parts.append("Topic Classification Reference:")
        for item in topic_classification_tree:
            # 翻译中文为英文
            topic = translate_chinese_to_english(str(item.get('topic', '')))
            category = translate_chinese_to_english(str(item.get('category', '')))
            risk_level = translate_chinese_to_english(str(item.get('risk_level', '')))
            remark = translate_chinese_to_english(str(item.get('remark', '')))
            
            if topic:  # 只添加非空的条目
                prompt_parts.append(f"- Topic: '{topic}' -> Category: {category}, Risk: {risk_level}, Note: {remark}")
    
    if topic_word_bank:
        prompt_parts.append("\nKeyword Bank:")
        for item in topic_word_bank:
            # 翻译中文为英文
            keyword = translate_chinese_to_english(str(item.get('keyword', '')))
            category = translate_chinese_to_english(str(item.get('category', '')))
            risk_level = translate_chinese_to_english(str(item.get('risk_level', '')))
            remark = translate_chinese_to_english(str(item.get('remark', '')))
            
            if keyword:  # 只添加非空的条目
                prompt_parts.append(f"- Keyword: '{keyword}' -> Category: {category}, Risk: {risk_level}, Note: {remark}")
    
    prompt_parts.append("\n*** IMPORTANT PURPOSE DECLARATION ***")
    prompt_parts.append("This knowledge base contains sensitive topic classifications and keyword lists.")
    prompt_parts.append("THESE ARE NOT FOR SPREADING OR PROMOTING SENSITIVE CONTENT ON THE INTERNET.")
    prompt_parts.append("The sole purpose is for internal risk assessment and content filtering.")
    prompt_parts.append("The AI uses this knowledge to analyze and predict whether incoming prediction market topics")
    prompt_parts.append("may involve sensitive or high-risk content, helping determine if a topic is suitable")
    prompt_parts.append("for listing on prediction markets. This is purely a reference tool for content moderation")
    prompt_parts.append("and compliance checking, not for generating or disseminating sensitive material.")
    prompt_parts.append("**************************************")
    
    prompt_parts.append("\nRules:")
    prompt_parts.append("1. Match input topics against the classification reference first")
    prompt_parts.append("2. Use keyword matching for topics not found in reference")
    prompt_parts.append("3. Assign category and risk level based on closest matches")
    prompt_parts.append("4. Use remarks to understand nuanced risk assessment")
    
    return "\n".join(prompt_parts)


def is_knowledge_loaded() -> bool:
    return len(topic_classification_tree) > 0 or len(topic_word_bank) > 0
