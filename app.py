from pathlib import Path

import pandas as pd
import streamlit as st

from extractor import locate_page, pdf_to_pages
from llm import extract_fields
from metrics import calc_metrics


st.set_page_config(page_title="A股年报关键财务数据提取", page_icon=":bar_chart:")

if "results" not in st.session_state:
    st.session_state.results = []
if "parsed_files" not in st.session_state:
    st.session_state.parsed_files = {}
if "extracted_files" not in st.session_state:
    st.session_state.extracted_files = {}

st.title("A股年报关键财务数据提取")
st.write("上传上市公司年报 PDF 后，这个页面将帮助你提取关键财务数据。")
st.info("Render 免费实例启动和 PDF 解析都会比本地慢，建议上传后先点击“开始解析 PDF”，不要连续重复点击。")

uploaded_file = st.file_uploader("上传 PDF 年报", type=["pdf"])

if uploaded_file is not None:
    default_company_name = Path(uploaded_file.name).stem
    company_name = st.text_input("公司名", value=default_company_name)
    file_bytes = uploaded_file.getvalue()
    file_key = f"{uploaded_file.name}:{len(file_bytes)}"

    if st.button("开始解析 PDF"):
        with st.spinner("正在解析 PDF，云端免费实例可能需要几十秒到几分钟，请耐心等待..."):
            pages = pdf_to_pages(file_bytes)
            keywords = ["主要会计数据和财务指标", "扣除非经常性损益", "营业收入"]
            matched_text, matched_page = locate_page(pages, keywords)
            income_keywords = ["营业总成本", "营业成本", "营业利润", "利润表"]
            income_text, income_page = locate_page(pages, income_keywords, window=1)
            balance_keywords = ["负债合计", "负债和所有者权益总计", "流动负债合计"]
            balance_text, balance_page = locate_page(pages, balance_keywords, window=1)

            st.session_state.parsed_files[file_key] = {
                "pages_count": len(pages),
                "matched_text": matched_text,
                "matched_page": matched_page,
                "income_text": income_text,
                "income_page": income_page,
                "balance_text": balance_text,
                "balance_page": balance_page,
            }

    parsed_result = st.session_state.parsed_files.get(file_key)

    if parsed_result:
        st.write(f"共 {parsed_result['pages_count']} 页")
        st.write(f"命中页码：{parsed_result['matched_page']}")
        st.text_area("命中文字", parsed_result["matched_text"], height=400)
        st.write(f"利润表命中页码：{parsed_result['income_page']}")
        with st.expander("查看利润表命中文字", expanded=False):
            st.write(parsed_result["income_text"])

        st.write(f"资产负债表命中页码：{parsed_result['balance_page']}")
        with st.expander("查看资产负债表命中文字", expanded=False):
            st.write(parsed_result["balance_text"])
    else:
        st.caption("文件已上传，点击“开始解析 PDF”后再查看命中结果。")

    if parsed_result and parsed_result["matched_page"] is not None:
        st.caption("本次 API 调用约消耗 0.01 元")

        if st.button("提取财务数据"):
            with st.spinner("正在调用模型提取财务数据，这一步在云端通常也会比本地慢一些..."):
                main_result = extract_fields(parsed_result["matched_text"])
                income_result = extract_fields(parsed_result["income_text"], "income")
                balance_result = extract_fields(parsed_result["balance_text"], "balance")

                merged_result = {
                    "main": main_result,
                    "income": income_result,
                    "balance": balance_result,
                }
                metrics_result = calc_metrics(merged_result)
                st.session_state.extracted_files[file_key] = {
                    "merged_result": merged_result,
                    "metrics_result": metrics_result,
                }

                record = {
                    "公司名": company_name,
                    "营业收入": main_result.get("营业收入", {}).get("value") if isinstance(main_result.get("营业收入"), dict) else None,
                    "归属于上市公司股东的净利润": main_result.get("归属于上市公司股东的净利润", {}).get("value")
                    if isinstance(main_result.get("归属于上市公司股东的净利润"), dict)
                    else None,
                    "归属于上市公司股东的扣除非经常性损益的净利润": main_result.get(
                        "归属于上市公司股东的扣除非经常性损益的净利润", {}
                    ).get("value")
                    if isinstance(main_result.get("归属于上市公司股东的扣除非经常性损益的净利润"), dict)
                    else None,
                    "总资产": main_result.get("总资产", {}).get("value") if isinstance(main_result.get("总资产"), dict) else None,
                    "归属于上市公司股东的净资产": main_result.get("归属于上市公司股东的净资产", {}).get("value")
                    if isinstance(main_result.get("归属于上市公司股东的净资产"), dict)
                    else None,
                    "毛利率": metrics_result.get("毛利率", {}).get("value")
                    if isinstance(metrics_result.get("毛利率"), dict)
                    else None,
                    "资产负债率": metrics_result.get("资产负债率", {}).get("value")
                    if isinstance(metrics_result.get("资产负债率"), dict)
                    else None,
                    "命中页码": parsed_result["matched_page"],
                }
                st.session_state.results.append(record)

    extracted_result = st.session_state.extracted_files.get(file_key)

    if extracted_result:
        merged_result = extracted_result["merged_result"]
        metrics_result = extracted_result["metrics_result"]

        st.json(merged_result)
        st.json(metrics_result)

        field_groups = [
                (
                    "main",
                    merged_result["main"],
                    [
                        "营业收入",
                        "归属于上市公司股东的净利润",
                        "归属于上市公司股东的扣除非经常性损益的净利润",
                        "总资产",
                        "归属于上市公司股东的净资产",
                    ],
                ),
                (
                    "income",
                    merged_result["income"],
                    ["营业收入", "营业成本", "营业总收入"],
                ),
                (
                    "balance",
                    merged_result["balance"],
                    ["资产总计", "负债合计"],
                ),
        ]

        table_rows = []
        for group_name, group_result, field_names in field_groups:
            for field_name in field_names:
                field_data = group_result.get(field_name, {}) if isinstance(group_result, dict) else {}
                if isinstance(field_data, dict):
                    value = field_data.get("value")
                    raw_line = field_data.get("raw_line")
                else:
                    value = None
                    raw_line = None

                table_rows.append(
                    {
                        "类型": group_name,
                        "字段名": field_name,
                        "提取值": value,
                        "原文行": raw_line,
                    }
                )

        st.table(table_rows)

if st.session_state.results:
    st.subheader("提取结果汇总")
    results_df = pd.DataFrame(st.session_state.results)
    st.dataframe(results_df, use_container_width=True)
    csv_data = results_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        "导出 CSV",
        data=csv_data.encode("utf-8-sig"),
        file_name="financial_summary.csv",
        mime="text/csv",
    )
