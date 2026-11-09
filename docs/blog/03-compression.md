# 03 · 上下文压缩：少送字，不少送信息

## 当时我怎么看这个问题

上下文窗口越开越大，并不等于该把历史全塞进去。我见过对话第 20 轮时把前 19 轮原文全送——其中一半是客套与重复检索。成本线性涨，关键事实反而被噪声淹没，模型开始「忘记」最早的约束（例如「必须引用政策原文」），开始凭印象编。

另一个极端是只留最近两轮：用户说「还按刚才那个方案」，模型一脸茫然。压缩的目标不是「最短」，而是**在预算内保住约束与事实**。

## 试过什么

1. **硬截断尾部（保留开头）**：简单，但多轮对话里开头常常是寒暄，尾部才是当前问题——于是你留了废话、丢了问题。
2. **只留最近 k 轮**：中期结论与工具结果丢失，Agent 重复搜同一文档。
3. **每次用大模型摘要全文**：又贵，且摘要可能丢掉数字与否定约束；离线 lab 也难跑。
4. **按固定百分比砍每条消息**：均匀变糊，信息密度一起下降。

## 为什么否决

否决「窗口有多大就塞多大」。否决「无 pin 的滑动窗口」。压缩策略必须**可离线演示、可测**：至少保留系统约束 + 最近轮 + 中间摘要槽位，并能用 token 估算打印压缩前后费用差。

## 最终怎么解

`compress.py` 实现最小 **pin + sliding window + extractive summary**：

- pin：系统消息、含「必须/不要」的约束句（在更完整的 context-engineering 仓里由 packer 优先级表达）
- recent：最近 N 轮原文
- middle：被挤出的轮次做成一条 `[summary]` 伪消息；demo 用抽取式——保留含数字/实体/约束词的句子

`cli demo` 打印压缩前后 token 估算，并与 router/cache/ledger 一起给出对照。要上「真摘要模型」时，只替换 middle 的生成器，外层结构不动。

## 用到的具体 skill / 技巧清单

| Skill | 用法 |
|-------|------|
| **pin 约束** | system 不被当普通历史切掉 |
| **滑动窗口** | recent N |
| **抽取式摘要** | 规则抽含数字/专名/约束句 |
| **压缩前后记账** | `accounting.estimate_tokens` |
| **与 routing 协同** | 压缩后再 route，避免「因废话变长」误判 strong |
| **姊妹仓** | 更完整优先级装箱见 `context-engineering` |

## 代码解析（按文件路径）

### `lab/src/cost_lab/compress.py`

`compress_messages(messages, max_tokens, recent)` → `CompressResult`。先算 before；若已小于预算则原样返回；否则拆 pin / head / tail，head 进抽取摘要。

### `lab/src/cost_lab/accounting.py` + `cli.py`

压缩不是文案美化，而是**成本动作**：demo 里会把 compressed / uncompressed 各记一笔，数字差就是你要不要上压缩的论据。

### `lab/scripts/smoke_check.py`

构造超长 history，断言 `tokens_after <= tokens_before`，防止有人「压缩」写成恒等函数还浑然不觉。
