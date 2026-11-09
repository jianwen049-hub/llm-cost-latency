# 02 · Cache Key 与便宜/强模型路由

## 当时我怎么看这个问题

同一份系统提示 + 同一批检索结果，被不同用户问「意思差不多」的问题时，我曾每次都打大模型。延迟和成本双炸。另一个极端是：所有请求都走小模型，复杂推理题正确率塌掉——客服侧表现为「简单问题很快，稍要比较就胡言」。

还有一次缓存「看起来命中了」却答非所问：cache key 只哈希了原始 query 字符串，用户加了「请」「谢谢」就 miss；反过来，有人把 retrieved_ids 顺序不同当成不同 key，命中率被自己打穿。

## 试过什么

1. **HTTP 全响应缓存按 URL**：LLM 是 POST body，URL 没用。
2. **只缓存最终答案字符串、key=原始 query**：改写与礼貌词导致命中率极低；也没法表达「同一检索上下文」。
3. **一律强模型**：质量相对稳，钱包不稳，且把简单题的延迟一并拉高。
4. **一律弱模型 + 人工升级**：运营成本转到人，晚上无人值守就挂。

## 为什么否决

否决「无 cache key 设计的缓存」。否决「单模型走天下」。要用**规范化后的 cache key** + **风险感知路由**：简单题走 cheap，显式复杂信号走 strong，命中缓存则跳过调用。key 必须包含：system、检索文档 id 集合（排序后）、规范化 query。

## 最终怎么解

- `cache.py`：`normalize_query` 去礼貌词与多余空白；`make_cache_key(system, retrieved_ids, query)` → sha256；`InMemoryPromptCache` 统计 hit/miss
- `router.py`：规则路由——长度、是否含「比较/为什么/一步步」、语言线索 → `cheap|strong`，并返回 `reasons` 便于观测
- `cli demo` 把 route → cache → 记账串起来

生产可把规则路由升级成轻量分类器，但**reasons 可解释**这一点建议保留。

## 用到的具体 skill / 技巧清单

| Skill | 用法 |
|-------|------|
| **cache key 规范化** | 小写、去多余空白、retrieved id 排序 |
| **语义无关噪声剔除** | 去掉「请/谢谢/麻烦」再哈希 |
| **路由特征** | 长度、关键词、工具需求 |
| **缓存旁路指标** | hit/miss 计数 |
| **与观测联动** | attrs.route / attrs.cache = hit 或 miss |
| **幂等演示** | smoke 断言礼貌词差异仍命中 |

## 代码解析（按文件路径）

### `lab/src/cost_lab/cache.py`

`normalize_query` + `make_cache_key` + `InMemoryPromptCache.get/set`。注意 retrieved_ids **排序后再拼接**，避免同集合不同顺序变不同 key。

### `lab/src/cost_lab/router.py`

`route(prompt) -> RouteDecision(tier, reasons)`。把 reasons 留下来，后面接 tracer 时极有价值：你会看到「到底是哪条规则把流量打到 strong」。

### `lab/src/cost_lab/cli.py`

demo 里对同一语义 query 加「麻烦…谢谢」再算 key，断言相等，然后走 ledger 记账。
