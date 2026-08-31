# Debug Session: render-slow-timeout
- **Status**: [OPEN]
- **Issue**: Render 部署后页面打开和提取明显慢于本地，最终可能长时间无结果。
- **Debug Server**: Pending
- **Log File**: .dbg/trae-debug-log-render-slow-timeout.ndjson

## Reproduction Steps
1. 打开 Render 部署地址。
2. 上传 PDF。
3. 点击“开始解析 PDF”或“提取财务数据”。
4. 观察页面长时间等待，最终无结果或明显慢于本地。

## Hypotheses & Verification
| ID | Hypothesis | Likelihood | Effort | Evidence |
|----|------------|------------|--------|----------|
| A | Render 免费实例冷启动和单核性能导致 PDF 解析时间过长 | High | Low | Confirmed by Render free-instance banner and repeated startup logs |
| B | 线上调用 DeepSeek API 超时或卡住，前端没有把错误展示出来 | High | Low | Inconclusive, current evidence stops before extraction stage |
| C | 上传文件在云端重复读取或会话状态导致重复耗时 | Medium | Low | Inconclusive, no direct parse-stage logs yet |
| D | Streamlit 按钮交互触发整页重复执行，导致解析/提取步骤被重复运行 | Medium | Medium | Inconclusive, reconnect log exists but no proof of duplicate parse |
| E | Render 实例内存或请求时长受限，长 PDF 在处理中被中断 | Medium | Medium | Inconclusive, no OOM/timeout traceback in current logs |

## Log Evidence
- Render UI banner: "Your free instance will spin down with inactivity, which can delay requests by 50 seconds or more."
- 10:27:23 service start log: `Running 'streamlit run app.py --server.address 0.0.0.0 --server.port $PORT'`
- 10:30:05 service start log repeats, indicating app/container restarted or woke up again.
- 10:30:59 Streamlit log: `Session with id ... is already connected! Connecting to a new session.`
- No traceback, no explicit Python error, no OOM message, no DeepSeek request failure shown in current evidence.

## Verification Conclusion
- Current strongest confirmed factor is Render free-instance cold start / weak runtime performance.
- The current evidence does not show a code exception; it shows startup/reconnect behavior instead.
- The symptom appears before any visible extraction result, so the bottleneck is more likely PDF parsing / Streamlit session responsiveness than DeepSeek extraction.
