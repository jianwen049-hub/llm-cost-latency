# 01 · Token 记账：你以为的成本和真实账单

## 当时我怎么看这个问题

很长一段时间我只看「调用次数」。日活涨了三倍，账单涨了八倍——因为平均 prompt 从 800 token 漂到 3k：系统提示叠罗汉、检索 top-k 盲目加大、对话历史无截断。没有**按 token 维度的记账**，优化就像蒙眼拧阀门：你以为在砍调用量，其实真正的洪水是每调用的输入长度。

还有一次，功能 A 和功能 B 共用一个 API key，财务只给得出总账。不做 feature 标签分账，就无法回答「到底是客服助手贵，还是内部文档问答贵」。

## 试过什么

1. **只看供应商控制台**：滞后、难按功能拆分，也难对齐某次发版。
2. **用字符数 /4 粗估**：英文还行，中文误差大，且忽略 tool schema / 多轮 framing 开销。
3. **每次请求后才记**：排障可以，难做「发请求前」的预算拦截。
4. **只记 cost 不记 tokens**：换价之后历史曲线失真，无法复盘。

## 为什么否决

否决「调用次数当成本」。否决「上线后再看账单」。本地 lab 至少要有：**估算函数 + 单价表 + 一次请求的 in/out 汇总**，并能按 feature 聚合。精确 tokenizer（tiktoken 等）可以后接；先把账本结构立住。

## 最终怎么解

`lab/src/cost_lab/accounting.py`：

- `estimate_tokens(text)`：中英混排启发式（中文按字、英文按空白词×1.3）
- `UsageLedger`：累加多次调用，输出小计与 by_feature
- 单价来自 `pricing.py` 的 cheap/strong 演示价

这不是 tiktoken 级精确，但**排序与相对优化足够**，且零依赖可离线跑。真接供应商时，用返回的 `usage` 覆盖估算即可，ledger 结构不用改。

## 用到的具体 skill / 技巧清单

| Skill | 用法 |
|-------|------|
| **启发式 tokenizer** | `estimate_tokens` |
| **分项单价表** | `pricing.PRICEBOOK` |
| **请求级 Usage** | feature + model_tier + in/out |
| **功能维度分账** | `ledger.summary()["by_feature"]` |
| **打印成本表** | `cli table` |
| **与压缩/路由联动** | demo 里同一 ledger 记账 |

## 代码解析（按文件路径）

### `lab/src/cost_lab/accounting.py`

核心类型：`Usage` / `UsageLedger`。保持纯数据，不打网络。博客讲「为什么要 feature 标签」时，直接指到 `add(..., feature=...)`。

### `lab/src/cost_lab/pricing.py`

`printable_rows()` 给 `cli table` 用：输出 1k in/out 单价与「典型 2k+0.5k 请求」费用，方便和 strong/cheap 路由策略对照。

### `lab/src/cost_lab/cli.py` + `scripts/smoke_check.py`

`table` / `demo` 一键复现；smoke 断言估算函数对中英文都有合理下限，并跑通 ledger。
