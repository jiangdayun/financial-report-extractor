import json
import os

from dotenv import load_dotenv
from openai import OpenAI


def extract_fields(text: str, fields_type="main") -> dict:
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return {"error": "未找到 DEEPSEEK_API_KEY"}

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    system_prompt = (
        "你是一个专业的财务数据提取助手，只从用户提供的年报原文中提取数据，"
        "不做任何推断或计算，找不到的字段返回 null。"
    )

    if fields_type == "main":
        user_prompt = f"""从以下年报原文中提取 2023 年度的数据，严格只取"2023年"列的数字，不要取"上年同期"或"调整前"列：
营业收入（元）
归属于上市公司股东的净利润（元）
归属于上市公司股东的扣除非经常性损益的净利润（元）
总资产（元）
归属于上市公司股东的净资产（元）
对每个字段，同时返回你在原文里找到的那一整行原始文字（raw_line），方便人工核对。
以 JSON 格式返回，结构如下：
{{"营业收入": {{"value": "33,126,277,551.51", "raw_line": "营业收入（元）33,126,277,551.51 10.04%"}}, ...}}
{text}"""
    elif fields_type == "income":
        user_prompt = f"""从以下合并利润表原文中提取数据。严格遵守以下规则：

只取"合并利润表"的数据，如果文中同时出现"母公司利润表"或"母公司资产负债表"，一律忽略。
只取 2023 年度那一列，不要取 2022 年度。
提取"其中：营业收入"这一行的数字作为营业收入，不要提取"一、营业总收入"。
提取"其中：营业成本"这一行的数字作为营业成本，不要提取"二、营业总成本"。
同时把"营业总收入"的数字单独返回，字段名 营业总收入，用于交叉核对。
对每个字段，同时返回你在原文里找到的那一整行原始文字（raw_line），方便人工核对。
以 JSON 格式返回，字段包括：
营业收入
营业成本
营业总收入
{text}"""
    elif fields_type == "balance":
        user_prompt = f"""从以下合并资产负债表原文中提取数据。严格遵守以下规则：

只取"合并资产负债表"的数据，如果文中出现"母公司资产负债表"，一律忽略。
只取 2023年12月31日 那一列（期末余额），不要取 2022年12月31日（期初余额）。
提取"资产总计"和"负债合计"两个字段。
对每个字段，同时返回你在原文里找到的那一整行原始文字（raw_line），方便人工核对。
以 JSON 格式返回，字段包括：
资产总计
负债合计
{text}"""
    else:
        return {"error": "不支持的 fields_type", "fields_type": fields_type}

    response = client.chat.completions.create(
        model="deepseek-chat",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    raw_content = response.choices[0].message.content or ""

    try:
        return json.loads(raw_content)
    except Exception:
        return {"error": "JSON 解析失败", "raw": raw_content}
