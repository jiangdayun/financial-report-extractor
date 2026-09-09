# README

# 我做了一个财报信息提取工具，记录一下我做的全过程

## 前置问题

**1\.为什么做？**

痛点：分析师读一份年报要花几小时，提取的基本都是固定的那十几个字段

**2\.拆解整个需求，每一步如何落地**

先把范围缩到单份A股PDF，1\.0版本提取字段（营业收入、归母净利润、归母扣非净利润、总资产、归母净资产、净利率、毛利率、资产负债率，前五个字段都在一张表，后面两个需要计算），需要附带原文页码，因为可以快速溯源检查，这个页码我选择的是在PDF阅读器里面的页码。

之后再考虑批量上传、更多字段、图表可视化、横向纵向比较等等。

用Trea来辅助我编程（我比较习惯用这个\~）\+python（用来算净利率=净利润 / 营业收入，算术这个部分交给python，不用大模型来算数）\+Streamlit 做界面

用白酒行业做测试



## 完整过程复盘

### 1\.准备环境、装依赖、让页面运行起来

要使用到python进行计算，所以先安装python（我用的版本是3\.12，不用最新版，因为太新的有些库可能还没做好），装的第一屏底部那个 "Add python\.exe to PATH" 记得要打勾。验证python是否下好了：按 Win \+ R，输入 cmd，回车。黑框出来后敲：”python \-\-version“。能够看到python的版本。再敲一条确认包管理器在：”pip \-\-version“

AI辅助编程，我用的是trea。新建一个文件夹，命名为fin\-extract（最好是用英文，怕之后有些地方会报错），在这里面建一个名为data的文件夹

下载一些年报进行测试，可以去企业官网或者巨潮资讯网进行下载（我选择的是贵州茅台、五粮液、泸州老窖、洋河股份、山西汾酒这五家企业的2023年年报，存入data中。选择同行业的，是因为格式高度相似，命中率会高一些。策略就是：控制变量，先在最规整的样本上跑通端到端）

去deepseek开放平台充个10块钱就够了，获取API Key。注意这个API Key它只会给我们复制一次，所以要自己记录好。为什么选deepseek？中文财报语料上表现好、价格便宜、而且API 完全兼容 OpenAI 的 SDK，所以将来想换模型改两行就行，没有绑定成本，可以避免供应商锁定。



打开AI IDE，打开名为fin\-extract的文件夹，输入下面的提示词：

```Markdown
我在做一个 Python + Streamlit 的项目，我是新手。请帮我：

1.建一个 requirements.txt，包含 streamlit、pdfplumber、openai、pandas、openpyxl、python-dotenv，都写明确的版本号不要用最新版
2.建一个 .gitignore，忽略 .env、data/、pycache/
3.建一个 app.py，用 Streamlit 显示一个标题"A股年报关键财务数据提取"，下面一行说明文字
4.一步一步告诉我在终端里敲什么命令来安装依赖和启动这个页面，我完全没用过终端
```

等它运行完之后，点开左边的文件列表去检查上面要求的文件是否都存在了。

打开requirements\.txt，查看里面的内容，确保能够互相兼容。这是之后部署时理解并安装项目所有依赖的依据，云服务器就是按照这个清单装环境的。

```Markdown
streamlit==1.40.2
pdfplumber==0.11.4
openai==1.57.0
pandas==2.2.3
openpyxl==3.1.5
python-dotenv==1.0.1
```

\.gitignore 里必须有这三行

\.gitignore 是一张"不要上传"的名单，其中\.env 里面有 API key，我们的API key是充值获得的，泄露的话会被盗刷。data/里面存放了下载的年报PDF，没必要上传，而且会拖慢部署。pycache/ 是Python 自动生成的缓存垃圾，机器产物不需要版本管理

```Markdown
.env
data/
__pycache__/
```

app\.py 大概 5 行左右，有 import streamlit as st 和 st\.title\(\.\.\.\)

然后我们要建一个虚拟环境，它就像一个隔离的独立盒子，可以为不同的项目准备不同的工具箱和运行环境。如果没有这个虚拟环境，假设项目 A 需要 pandas==1\.5\.0，而项目 B 需要 pandas==2\.2\.3，后安装的会把前一个覆盖掉，导致某个项目直接报错崩溃。

用“ctrl\+\~”打开trea的终端，输入“python \-m venv \.venv”

左侧会多出一个 \.venv 文件夹。然后激活它：“\.venv\\Scripts\\activate”，就可以看到命令行最前面多了一个绿色的\(\.venv\)。这行命令每次打开终端的时候，都要记得重新激活一次，不然就像上面说的会混乱。

在windows上如果报错说"无法加载文件 \.\.\. 因为在此系统上禁止运行脚本，是PowerShell 的安全策略拦的。用“Set\-ExecutionPolicy \-Scope Process \-ExecutionPolicy Bypass”可以解除（只对当前窗口，不改系统设置），然后在激活一次虚拟环境。

装库：“pip install \-r requirements\.txt”。这句话的意思是，阅读这个文件，按照上面的内容都装上，每个库后面都锁了版本（==1\.40\.2），这样可以复现，避免自动装新版本的时候报错。

等待进行安装\.\.\.\.

如果有红色报错，记得将一整段报错复制给大模型，问它怎么办。ERROR / Traceback / Failed是需要解决，notice / warning / deprecated 可以先放放。

验收一下，确认关键库是否存在：“pip show streamlit pdfplumber openai pandas openpyxl python\-dotenv”

看到每个库后面都显示了 Name、Version、Location 等信息，就确认安装成功。

然后我们把这个页面运行起来：“streamlit run app\.py”第一次运行它会问你邮箱，直接回车跳过，就可以看到在浏览器打开了一个本地网页，这就是我们刚刚做的东西。

我的开发日志\~

```Markdown
【Day 1】环境搭建与素材准备

今天目标：装好 Python 环境和 6 个依赖库，让 Streamlit 空白页面在浏览器跑起来，
         下载 5 份白酒行业 2023 年报，申请 DeepSeek API key。

实际完成：全部达成。浏览器 localhost:8501 成功显示标题
         "A股年报关键财务数据提取"。

关键决策：
- Python 选 3.11/3.12 而非 3.13：新版本缺少预编译包，Windows 上易编译失败
- 用 .venv 虚拟环境隔离依赖，避免与其他项目版本冲突
- requirements.txt 锁定精确版本号，保证环境可复现（Day 5 云端部署依赖这一点）
- 模型选 DeepSeek：中文财报表现好、便宜、API 兼容 OpenAI SDK 便于后续替换
- API key 存入 .env 并加入 .gitignore，data/ 和 __pycache__/ 同时排除

卡点 1：pip install 结束后未出现 "Successfully installed"，只显示
       [notice] A new release of pip is available，误判为安装失败。
解决：理解到 notice 属于提示而非错误，出现在安装流程结束之后。
     用 pip show 逐个验证 6 个库均已正确安装。
教训：要能分辨 ERROR / Traceback / Failed（真故障）与
     notice / warning（可忽略提示）。安装完成后应主动用 pip show 验收，
     而不是靠"看起来没报错"来判断。

新教训：
【为什么用终端跑而不是让 AI 跑】
之前开发的时候我总是习惯让AI跑，这次跳出来是否在沙箱外运行，我问了大模型后点击跳过
Trae Agent 执行命令时用的是它自己的隔离沙箱，那里没有我建的 .venv。
它跑通不代表我跑得通，反之亦然，两边环境不一致会让排错变成猜谜。
规则：代码让 AI 写，命令自己在终端跑。
Agent 弹"在沙箱外运行"对话框时，一律点"跳过"。

其他记录：
- 下载年报时需避开"摘要版""英文版"，若有修订版则取最新
- 记录了 5 份年报中"主要会计数据和财务指标"表的真实页码，
  作为 Day 2 定位函数的验收基准（人工真值先行，再验证程序输出）

明天第一件事：写 pdf_to_pages 函数，把 PDF 变成 [(页码, 该页文字)] 的列表。
```

### 2\.把 PDF 变成"每页文字，两个函数

打开trea，点到对应的文件夹，打开终端，激活虚拟环境。

输入以下提示词：

```Markdown
在 extractor.py 里写一个函数 pdf_to_pages(file)，用 pdfplumber 读取 PDF，返回 list[tuple[int, str]]，即 [(页码, 该页文本), ...]，页码从 1 开始。如果某页 extract_text() 返回 None，用空字符串代替。不要写其他函数，不要写 main。
```

这个函数是把 PDF 拆成 \[\(1, 第1页文字\), \(2, 第2页文字\), \.\.\.\] 这样一张清单。带上页码是关键——后面要能回答"这个数字是从第几页取的"，这样就能够溯源。

完成之后再输入：

```Markdown
改 app.py：加一个 st.file_uploader 只接受 pdf 格式。上传后调用 pdf_to_pages，用 st.write 显示"共 N 页"，再用 st.text_area 显示第 1 页的文字。另外在 pdf_to_pages 定义的上面加 @st.cache_data 装饰器。
```

1\.0版本只做上传pdf格式的

@st\.cache\_data 是缓存，因为Streamlit 有个特性：页面上任何一次点击，都会从头到尾重跑整个python脚本。不加缓存，每点一下就重新解析 143 页 PDF，等好几秒。加了之后同一份文件只解析一次，之后直接取上次结果。**验收方法**：extractor\.py 里找 def pdf\_to\_pages。

终端运行“streamlit run app\.py”，**验收标准**：上传一份PDF年报，看页数跟 PDF 阅读器显示的总页数一致；文本框里能看到中文。

然后再写第二个函数：

```Markdown
在 extractor.py 里再写一个函数 locate_page(pages, keywords, window=1)，用来找出最可能包含财务数据表的那一页。
打分规则：每命中一个关键词加 3 分；用正则统计这一页有多少个 6 位以上的连续数字（可能带千分位逗号），有几个就加几分，但这一项最多加 10 分。
取总分最高的那一页，返回两个值：这一页加上它前后各 window 页的文字拼接结果，以及命中的页码。
```

这个函数是用来定位候选页的

第一个打分规则是关键词，第二个打分规则是看数字密度。因为如果只看关键词的话，可能会命中其他的（有些字词会在财报里面反复出现），而我们所需要提取的字段数据在会计报表中，有很多数字，加上数字密度这一项能够更精准的命中。命中这个候选页之后，再加上他的前后页（window=1，因为报表常常跨页），把这3页塞给大模型，而不是全文，这样可以节省token，减少卡顿，也没有那么长的上下文。

关于定位候选页的思考？我之前有想过根据目录去定位，我自己在阅读财报的时候也是这样做的。但目录页的页码是印刷页码，而在PDF阅读器里面是物理页码，这俩并不总是一致的，或多或少有所偏移。而且目录里面是章节，所需要的数据在表里面，在那一个章节里面继续找表的话，内容更多了。所以还是先用上面粗召回 \+ 精提取的两段式。

改一下界面：

```Markdown
改 app.py：用关键词列表 ["主要会计数据和财务指标", "扣除非经常性损益", "营业收入"] 调用 locate_page，用 st.write 显示"命中页码：X"，并把返回的文字显示在 st.text_area 里。
```

然后关闭之前的那个终端（我是点那个小垃圾桶，终止终端）然后再用“ctrl\+\~”打开trea的终端，输入"streamlit run app\.py"回车。依次上传5份年报，**验收标准：**命中页码要跟真值对得上，文本框里能看到"营业收入"后面跟着一串大数字。如果命中错误了，先看看哪一页错了，那一页是什么。诊断一下是关键词的问题还是window需要调整。（但是我开发的时候程序都命中对了）

我的开发日志\~

```Markdown
【Day 2】PDF 解析与财务表定位

今天目标：写 pdf_to_pages 把 PDF 变成"每页文字"，写 locate_page 找出财务表所在页，
         用 5 份年报的真值页码验收。

实际完成：pdf_to_pages 解析成功（茅台 143 页，首文字正常）；locate_page 5 份全部
         命中真实页码，总页码与"营业收入"所在页均验证正确。Day 2 完成。

关键决策：
- 定位用"关键词命中 + 数字密度打分"而非目录/书签：目录页也含关键词会误命中，
  数字密度能让真表格页分数甩开目录页；且书签格式不统一、印刷页码存在偏移。
  这是"粗召回 + 精提取"两段式的前半段。
- window=1 拼接前后页：保证表格跨页断裂时字段完整，且给模型多列上下文。

卡点 1：终端输入混乱——上一条命令未跑完就敲下一条，多行挤在一起。
解决：等命令提示符回到 PS D:\... 再敲下一条；activate 等 (.venv) 出现。
教训：终端是"有状态的"，一条命令执行完才轮到下一条。

卡点 2：Trae Agent 弹出"在沙箱外运行"对话框，Sandbox 无本地环境。
解决：一律点"跳过"，命令在本地终端手动执行。
教训：代码让 AI 写、命令自己在终端跑。Agent 沙箱 ≠ 本地 .venv，环境不一致
     会导致"它跑得通我跑不通"的假象。这是典型的 vibe coding 边界教训。

其他发现：
- pdfplumber 存在单元格数字被拆断现象（"33,126,277,5 / 51.51"），
  Day 3 需靠"返回原文整行 + 人工核对"兜底。

明天第一件事：写 llm.py，用 DeepSeek 提取 5 个字段。
```

### 大模型提取财务字段

依旧打开终端激活虚拟环境，然后确认\.env 里面有APIkey

```Markdown
新建 llm.py，写一个函数 extract_fields(text: str) -> dict。
功能：调用 DeepSeek API，从财务报表原文里提取 5 个字段，返回一个字典。

要求：

1.用 openai 库，base_url 设为 "https://api.deepseek.com"，api_key 从环境变量 DEEPSEEK_API_KEY 读取（用 python-dotenv 的 load_dotenv()）。
2.model 用 "deepseek-chat"，**temperature=0**，**要求模型以 JSON 格式返回**。
3.system prompt：你是一个专业的财务数据提取助手，只从用户提供的年报原文中提取数据，不做任何推断或计算，找不到的字段返回 null。
4.user prompt 模板（{text} 替换为传入的原文）：
从以下年报原文中提取 2023 年度的数据，严格只取"2023年"列的数字，不要取"上年同期"或"调整前"列：
营业收入（元）
归属于上市公司股东的净利润（元）
归属于上市公司股东的扣除非经常性损益的净利润（元）
总资产（元）
归属于上市公司股东的净资产（元）
对每个字段，同时返回你在原文里找到的那一整行原始文字（**raw_line**），方便人工核对。
以 JSON 格式返回，结构如下：
{"营业收入": {"value": "33,126,277,551.51", "raw_line": "营业收入（元）33,126,277,551.51 10.04%"}, ...}
{text}
5.用 response_format={"type": "json_object"} 开启 JSON 模式。
6.**用 try/except 包住 JSON 解析，解析失败时返回 {"error": "JSON 解析失败", "raw": 原始返回文字}**。
只写这一个函数，不写 main，不写测试。
```

**temperature=0**：让模型每次给同一份文件返回相同结果。它会让模型直接无视概率高低，每次得到的结果都是一模一样的。

**要求模型以 JSON 格式返回**：如果没有这一项命令，大模型可能会先回复“好的，以下是你要提取的结果。”or“我将用最直白、最不绕弯子的话\.\.\.”。但是Python 的 json\.loads\(\) 函数极其严格，它只认以 \{ 或 \[ 开头的纯 JSON 字符串，不然的话会报错的。

**每字段带 raw\_line**：对于输出中的每个提取字段（例如，金额、日期、名称），包含提取该数据所用的一行（或几行）原始文本。目的是溯源，可以看原文行进行比对

**用 try/except 包住 JSON 解析：**即便说了返回json语法，大模型也有可能出错，一旦让python执行，报错，程序就会终止运行。执行过程，运行try，格式对的话返回，格式不对跳到except（而不是直接报错），然后解析返回。

然后接入界面：

```Markdown
改 app.py：在文件顶部加 from llm import extract_fields。
在 locate_page 成功返回后，加一个按钮"提取财务数据"。点击后调用 extract_fields 把定位文字传进去，用 st.json 显示返回的字典，并在下方加一个手动核对表：用 st.table 展示字段名、提取值、原文行三列，每行一个字段。
按钮下方加一行小字：st.caption("本次 API 调用约消耗 0.01 元")
```

然后运行。打开网页之后，上传年报，点"提取财务数据"按钮，一一验收五个字段是否一致。

day3的开发日志\~

```SQL
【Day 3】大模型提取财务字段

■ 今天目标
调用 DeepSeek API，从定位好的年报页面里提取 5 个字段，
人工核对每份数字与 PDF 原文一致。

■ 实际完成
- llm.py 写好 extract_fields 函数，temperature=0，JSON 模式
- 5 份年报全部提取成功，字段准确率 25/25（5 份 × 5 字段）
- 含洋河（最复杂多列表格）无误
- 总 API 费用：0.05 CNY

■ 准确率结果100%
无卡点

记录一个设计决策：
洋河"数字被 pdfplumber 拆成两行"的问题（昨天发现），
今天靠 raw_line 返回原文整行 + 人工核对兜住了，没有漏数字。
根本原因是 PDF 两栏排版，不是 bug，是已知局限。

■ 明天第一件事
写两个计算函数：
1. 毛利率=(营业收入 - 营业成本) / 营业收入
2. 资产负债率=（ 总负债 / 总资产）
然后在页面上展示一张 5 家公司的对比表。
```

### 4\.跨报表取数、指标计算与对比表

毛利率=\(营业收入 \- 营业成本\) / 营业收入

资产负债率=（ 总负债 / 总资产）

要二次定位

输入关键词：

```Markdown
改 app.py：在现有的 locate_page 调用之后，再加两次 locate_page 调用，复用同一个 pages 列表。
第一次用关键词 ["营业总成本", "营业成本", "营业利润", "利润表"]，window=1，结果存为 income_text 和 income_page。
第二次用关键词 ["负债合计", "负债和所有者权益总计", "流动负债合计"]，window=1，结果存为 balance_text 和 balance_page。
用 st.write 显示这两个命中页码，并用两个 st.expander 分别包住这两段文字（默认折叠）。
只改 app.py，不改 extractor.py。
```

前三天的 5 个字段都在第 5 页"主要会计数据和财务指标"里，​但毛利率需要营业成本、资产负债率需要负债合计，这两个字段那一页没有，它们在报告后半部分的合并利润表和合并资产负债表里。所以要用不同关键词再定位两次——同一个 locate\_page 函数，换一组关键词就能复用。

**验收标准：**执行之后运行，上传年报之后提取，能看到"营业成本"和"负债合计"字样后面跟着大数字

然后在执行：

```Markdown
改 llm.py：给 extract_fields 加第二个参数 fields_type，默认 "main"。

当 fields_type == "income" 时，user prompt 改为：
从以下合并利润表原文中提取数据。严格遵守以下规则：

只取"合并利润表"的数据，如果文中同时出现"母公司利润表"或"母公司资产负债表"，一律忽略。
只取 2023 年度那一列，不要取 2022 年度。
提取"其中：营业收入"这一行的数字作为营业收入，不要提取"一、营业总收入"。
提取"其中：营业成本"这一行的数字作为营业成本，不要提取"二、营业总成本"。
同时把"营业总收入"的数字单独返回，字段名 营业总收入，用于交叉核对。
当 fields_type == "balance" 时，user prompt 改为：
从以下合并资产负债表原文中提取数据。严格遵守以下规则：

只取"合并资产负债表"的数据，如果文中出现"母公司资产负债表"，一律忽略。
只取 2023年12月31日 那一列（期末余额），不要取 2022年12月31日（期初余额）。
提取"资产总计"和"负债合计"两个字段。
三种类型都保持：temperature=0、json_object 模式、每个字段返回 raw_line 原文行、try/except 包住 JSON 解析。

改 app.py：点"提取财务数据"按钮后依次调用三次 extract_fields，main 用原来的定位文字，income 用 income_text，balance 用 balance_text，三个结果合并显示。
```

1\.0版本为了提取数据的准确性\+我用的都是23年年报，我选择先只做2023年的提取。

计算口径我用的是营业收入，而不是营业总收入

```Markdown
新建 metrics.py，写一个函数 calc_metrics(data: dict) -> dict。
输入是提取出的字段字典，输出计算指标。
要求：
1. 先写一个辅助函数 to_float(s)，把 "33,126,277,551.51" 这种带千分位逗号的字符串转成 float，输入为 None 或转换失败时返回 None。
2. 毛利率 = (营业收入 - 营业成本) / 营业收入，结果保留两位小数的百分数。
3. 资产负债率 = 负债合计 / 资产总计，同样保留两位小数的百分数。
4. 任一输入为 None 时，该指标返回 None，不要抛异常。
5. 每个指标同时返回计算用到的分子分母原始值，字段名 formula，例如 "(150,560,803,167.00 - 11,946,180,000.00) / 150,560,803,167.00"。
只写这一个文件。
```

```Markdown
改 app.py：用 st.session_state 存一个列表 results，每次成功提取后把 {公司名, 5个字段, 毛利率, 资产负债率, 命中页码} 追加进去。
公司名用 st.text_input 让用户手填，默认值为上传文件名去掉 .pdf。
在页面底部用 st.dataframe 展示 results 全部记录，并加一个 st.download_button 导出 CSV，文件名 financial_summary.csv。
```

**st\.session\_state**：我希望能够让不同企业进行对比，但是streamlit没交互一次会重新从头跑。st\.session\_state就保证了这个不会被清空，可以把数据积累起来

然后就是运行\~

这是我最后的scv：

<img width="2748" height="380" alt="csv" src="https://github.com/user-attachments/assets/bd28e3f6-a09a-49f2-932a-2b7daf2aeb74" />


day4开发日志\~

```Markdown
【Day 4】跨报表取数、指标计算与对比表

■ 今天目标
从利润表和资产负债表取数，用 Python 计算毛利率和资产负债率，
生成 5 家公司对比表并支持 CSV 导出。

■ 实际完成
- 二次定位成功：合并利润表命中第 63 页，合并资产负债表命中第 60 页
- 人工核查表格实际边界：合并利润表 63-65 页，合并资产负债表 58末-61初
- extract_fields 扩展为三种模式（main / income / balance）
- metrics.py 完成毛利率、资产负债率计算，带 formula 算式回显
- st.session_state 实现多份累积，st.dataframe 对比表 + CSV 导出
- 准确率：100%
- 累计 API 费用：0.13（多次调用测试）

已记录的判断点：
1. 一度怀疑 window=1 覆盖不够，实际逐页核查后确认够用，且加宽会引入母公司报表的同名干扰数据。所以保持不动。上下文不是越多越好，无关内容会稀释注意力、制造歧义。

2. 提示词必须显式排除母公司报表和上期数据。合并 vs 母公司、本期 vs 上期、总收入 vs 收入——这三组都是字段名几乎相同、数值完全不同的陷阱，模型没有规则约束时会随机命中其中之一。

■ 明天
微调+部署到公网
```

### 5\.微调\+部署到公网

```Markdown
改 app.py 的两个展示细节：

公司名输入框的默认值，把文件名里的"2023年年度报告""：""年度报告"等字样去掉，只保留公司简称。例如"贵州茅台酒股份有限公司2023年年度报告"处理成"贵州茅台"，"泸州老窖：2023年年度报告"处理成"泸州老窖"。用简单的字符串替换实现即可。
现在的"命中页码"列只记录了主要指标页。改成三列：主表页、利润表页、资产负债表页，分别对应三次定位的结果。
在对比表上方加一行说明文字：st.caption("营业收入取合并利润表'其中：营业收入'口径；毛利率=(营业收入-营业成本)/营业收入；资产负债率=负债合计/资产总计")
```

然后我还觉得每次返回的json有点影响观感，于是让trea改成默认折叠可展开的了。

再检查一下项目能否正常运行，然后我们需要**把代码上传到GitHub**上面。

打开GitHub，右上角绿色图标新建仓库New repository，仓库名写英文。不要勾选Add \.gitignore ，因为我们本地已建好。创建之后二维码区域有一个命令，一会会用

打开终端，确认git已经装好了：“git \-\-version”

第一次用 Git 的话，先告诉它你是谁

```Markdown
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

依次输入：

git init

git add \.

git commit \-m "Day 5: 财务年报数据提取与指标计算"

git branch \-M main

git remote add origin \<这里粘贴你仓库页面那行命令\>

git push \-u origin main

最后一行出现 main \-\> main就是成功了（有时候可能因为网络连接的问题不成功，多试几次or问问大模型）授权登录GitHub之后可以看到自己仓库的内容，注意看一下不能上传的文件有没有在这儿。

推到GitHub上之后，要部署，服务器拉下来。因为我们之前写的代码是本地运行的，别人访问不到。使用服务器，可以让网站一直在线。

然后就是部署到公网，我之前想走hugging face spaces，但是连不上；又试了render，但是发现免费额度的运行不了；于是选择**买服务器，**使用腾讯云轻量服务器，一开始点进去感觉好多内容，我还以为我点进广告里了。轻量应用服务器2核 2G Ubuntu 22\.04的一个月也要40，还蛮贵的，不过我看到新用户可以首月免费，我就选了这个（因为这个操作系统比较主流，2G是因为pandas/numpy 安装时很吃内存），刚刚看好像还有学生优惠3个月的，也蛮划算的。地域选择一个离自己近的，访问速度快一些。

买完之后，点进服务台，那个服务器登录选择密码登录（一开始会给你设置一个密码的，可以在站内回信里面查看。更改密码，一定要设置一个自己记得住的密码，因为之后连接的时候要输密码，而且电脑上出于隐私保护吧还没有任何显示），再往下看网络与域名可以看到自己的公网IP，这个可以记录一下子。然后点到防火墙，新增一个规则：”协议：TCP，端口：8501，来源：0\.0\.0\.0/0“保存一下（端口8501因为在我本地运行的时候开的端口就是8501）

然后我们**让电脑连上服务器**。在终端里输入“ssh ubuntu@你的公网IP”（SSH 是"安全远程登录"的意思），第一次连接会问确认连接嘛，回答yes就行。然后会问你password，输入刚刚设置的密码就好，屏幕上没有任何显示是很正常的，打完之后回车。提示符变成ubuntu@VM\-0\-13\-ubuntu:\~$，就是连上了，之后的操作就是在服务器上进行的了。

**进tmux**。如果纯用ssh跑的话，当网络断了，上面的命令会被杀掉。而tmux 是一个"不会随连接消失的工作台"。在 tmux 里跑的东西，就算 SSH 断了，它也继续跑。重新连上再 tmux attach 就能回到原处。

输入：“tmux new \-s deploy”，这个的意思是创建一个新的工作台名叫deploy，\-s是session（会话）的意思。之后再接入的时候输：“tmux attach \-t deploy”，\-t是target（目标）的意思，目标是直接进入deploy的工作台。看到屏幕底部出现一条绿条就成功了

然后**更新软件源、装基础工具**。

```Markdown
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
```

sudo是以管理员的方式运行，apt是Ubuntu 的包管理器，相当于Ubuntu系统里的“应用商店”管理工具（挑战说apt不被发现：apt）。这条命令的意思是：刷新"软件目录"，让服务器知道现在有哪些软件的最新版。

\-y就是自动回答yes，因为前面install是在安装软件。

为什么执行这两条命令？因为刚拿到的是全新的、空白的服务器，需要装我们需要的工具。先清点一下目录再进行安装。

**装swap**（硬盘），因为内存只有2G，装东西的时候可能会把桌面撑爆，就killed了。输入：“free \-h”看看内存有多少（free：显示内存使用情况，\-h就是\-human，以 KB/MB/GB 显示大小，而不是原始字节），swap哪一行应该是0b，说明没有交换空间，需要加。内存就像你的书桌桌面，你要同时摊开的书越多，桌面就越挤。硬盘则像旁边的书架，容量大但拿取慢

```Markdown
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

sudo fallocate \-l 2G /swapfile：fallocate是预分配空间，在根目录下创建一个叫 swapfile 的文件，大小 2G（\-l 是 length，长度）。

sudo chmod 600 /swapfile：上锁，只允许管理员读写（600 是 Linux 的权限数字写法）

sudo mkswap /swapfile：把这个空位格式化成“Swap专用格式”

sudo swapon /swapfile：swapon=swap on，就是把这个空间打开激活

echo '/swapfile none swap sw 0 0' \| sudo tee \-a /etc/fstab：写进开机启动表，确保服务器下次重启时，这个书架自动挂上，不用再手动敲一遍。

然后再检查一下内存。

**把 GitHub 上的代码拉下来**

```Markdown
cd ~
git clone https://github.com/你的用户名/你的仓库名.git  #去 自己的仓库页面，点绿色的 Code 按钮 → 选 HTTPS 标签 → 复制网址，这个报错的话可以多试几次
cd 你的仓库名
ls -l #看关键文件在不在（主程序文件和依赖清单（requirements.txt）
```

\#号后面的是我的标注哦

**建虚拟环境 \+ 装依赖**

```Markdown
python3 -m venv .venv
source .venv/bin/activate #source 是"执行这个脚本，并让它的效果作用于当前终端"。activate 脚本会修改你当前终端的环境变量，让 python 和 pip 指向虚拟环境里的那份
pip install --upgrade pip -i https://mirrors.cloud.tencent.com/pypi/simple #
pip install -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple
```

\-i https://mirrors\.cloud\.tencent\.com/pypi/simple = 从腾讯云的镜像源下载

**配置密钥**

```Markdown
head -40 llm.py #看代码读的是哪个变量名
nano .env #创建 .env，内容DEEPSEEK_API_KEY=sk-你的真实密钥，保存退出：Ctrl+O → Enter → Ctrl+X
chmod 600 .env #锁权限
```

**手动跑一次**

运行这个：streamlit run app\.py \-\-server\.address 0\.0\.0\.0 \-\-server\.port 8501

0\.0\.0\.0 意思是"接受来自任何地址的访问"。第一次跑可能问 Email:，直接回车跳过。

用浏览器打开：http://你的公网IP:8501（会显示不安全，因为不是https，没配证书）

**systemd 后台化**

systemd 是 Linux 自带的"服务管家"，把程序交给它之后：

- 跟你的 SSH 连接彻底脱钩，你关电脑它照跑

- 程序崩了自动重启

- 服务器重启后自动拉起

- 日志统一收集，随时可查

先按 Ctrl\+C 停掉当前正在跑的 streamlit

```Markdown
**先**输入：
sudo nano /etc/systemd/system/finreport.service
**再**存入：
[Unit]
Description=Financial Report Extractor (Streamlit)
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/financial-report-extractor
EnvironmentFile=/home/ubuntu/financial-report-extractor/.env
ExecStart=/home/ubuntu/financial-report-extractor/.venv/bin/streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
**保存**退出：Ctrl+O → Enter → Ctrl+X
```

启动并设置开机自启

```Markdown
sudo systemctl daemon-reload
sudo systemctl enable finreport
sudo systemctl start finreport
```

检查是否真的活着：“sudo systemctl status finreport”，看到绿色的 active \(running\) = 成功。

看日志：“sudo journalctl \-u finreport \-n 50 \-\-no\-pager”直接输出这个服务器最近50行的日志，想要实时看日志：“sudo journalctl \-u finreport \-f”

最终再关掉所有东西，打开http://你的公网IP:8501，看能不能访问。能访问就成了！

邀请大家使用一下：http://1\.12\.218\.202:8501

后续呢还打算配 Nginx 做反向代理去掉链接里面的8501，再申请一个域名获得https，这样就不会显示不安全了。

**如果改代码了**

在自己电脑的终端：

```Markdown
git add .
git commit -m "改了什么"
git push
```

在服务器上

```Markdown
cd ~/financial-report-extractor
git pull
sudo systemctl restart finreport
```

**如果改动涉及新增了库**

在自己电脑终端

```Markdown
pip freeze > requirements.txt
git add requirements.txt
git commit -m "add new dependency"
git push
```

在服务器上：

```Markdown
cd ~/financial-report-extractor
git pull
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart finreport
```

这就是我做这个1\.0版本的全过程分享哦，之后还会继续改进，做更多年份、批量上床、更多字段、更多方向对比的！

