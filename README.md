---
title: 辩析 · Debate Lens
emoji: 🎤
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# 辩析 · Debate Lens

**粘贴一个辩论视频链接，三分钟看清论证骨架。追问任何你好奇的问题。**

[![Hugging Face](https://img.shields.io/badge/HuggingFace-Spaces-blue)](https://huggingface.co/spaces/Mariazhu/debate-agent)
[![Streamlit](https://img.shields.io/badge/Streamlit-Cloud-red)](https://debate-agent-khsvnchexjctge4e3kwb8z.streamlit.app)

---

## 这个产品解决什么问题

我妹妹陈琳大一加入校辩论队，每周至少看三场辩论赛视频学技术。看完一个小时，反方核心论点是什么？她想不起来。信息太多，正反方反方交替太快，脑子里是一团线。

她想把视频链接丢进一个工具里，自动提取双方论证结构，然后直接追问自己好奇的问题。搜了一圈，没有这样的东西。

**辩论爱好者看视频学辩论，投入时间不少，收获却很薄。** 这是 Debate Lens 要解决的问题。

---

## 核心能力

| 功能 | 说明 |
|------|------|
| 🔗 **视频链接输入** | 粘贴 B站链接，自动获取字幕 → AI 结构化分析 |
| ⚡ **3 分钟速览** | 辩题、双方 Top 3 论点、最激烈交锋、关键未回应问题 |
| 💬 **AI 深度追问** | 多轮对话，搜索原文、追踪攻防链、对比立场 |
| 🧠 **知识库 RAG** | 录入多场辩论 → 跨视频对比分析 → "这几场里谁论证最大胆？" |
| 📋 **报告导出** | Markdown 完整分析报告 + 原始 JSON |

---

## 迭代历程

| 版本 | 核心改进 | 综合评分 |
|------|---------|:---:|
| v0.1 | MVP：粘贴链接 → 结构化分析 | — |
| v0.2 | 导出功能 | — |
| v0.3 | 修复 chunk 截断 + quick_view | 3.52 |
| v0.3.1 | 修复空白 + 评委过滤 | **4.24** |
| v0.4.2 | 逐字稿清洗 + 赛制自适应（支持 哲理辩/政策辩 等多种赛制） | 3.8 |
| v0.5 | ChromaDB + sentence-transformers RAG 知识库，跨视频对比 | 3.4 |

每版评估详见 [`docs/`](docs/)：
- [结构化分析评估](docs/eval-report-v0.3.1.md)
- [paste-URL 流水线评估](docs/eval-paste-url.md)
- [知识库 RAG 评估](docs/eval-knowledge-base.md)（10 查询 × 5 维度）

---

## 技术架构

```
用户粘贴 B站链接
     │
     ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ video_fetcher │ → │ transcript   │ → │  compressor │
│ 字幕获取      │   │ cleaner 清洗  │   │ LLM 结构化   │
└─────────────┘    └──────────────┘    └──────┬──────┘
                                              │
              ┌───────────────────────────────┤
              ▼                               ▼
     ┌────────────────┐              ┌───────────────┐
     │  思维导图 +     │              │  深度追问      │
     │  3分钟速览      │              │  多轮追问      │
     └────────────────┘              └───────┬───────┘
                                             │
                                    ┌────────┴────────┐
                                    ▼                 ▼
                            ┌───────────┐    ┌──────────────┐
                            │ ChromaDB   │    │ RAG context  │
                            │ 向量检索    │    │ 跨视频对比    │
                            └───────────┘    └──────────────┘
```

- **LLM**：DeepSeek Chat API（Anthropic 兼容协议）
- **向量库**：ChromaDB + paraphrase-multilingual-MiniLM-L12-v2（384维）
- **前端**：Streamlit
- **部署**：HuggingFace Spaces（Docker, Python 3.12）+ Streamlit Cloud

---

## 关键产品决策

| 决策 | 选择 | 为什么 |
|------|------|--------|
| 输入方式 | 视频链接而非文字稿粘贴 | 目标用户看的是 B站视频，多一步就多一层流失 |
| 首发用户 | 入门辩手而非教练/研究者 | 人数最多、使用频率最高、反馈最积极 |
| 向量库 | ChromaDB 本地而非 Pinecone 云服务 | 零成本、零延迟、数据不出用户机器 |
| 知识库切分 | ~500 字/块，段间 100 字重叠 | 平衡检索精度与语义完整性 |
| 不做 AI 辩论陪练 | 聚焦分析而非对战 | 竞品扎堆陪练方向，差异化在分析 |
| 不做社区功能 | 单人工具 | 先让一个人能用爽，再考虑多人 |

详见 [PRD](docs/prd.md) · [竞品分析](docs/competitive-analysis.md) · [用户画像](docs/user-personas.md)

---

## 下一步规划

| 优先级 | 方向 | 说明 |
|--------|------|------|
| P0 | 知识库检索多样性 | 跨视频对比目前偏斜严重，需要按 debate_id 分散采样 |
| P1 | 用户反馈闭环 | 产品内收集反馈，目前靠朋友人工测试 |
| P1 | embedding 升级 | MiniLM-384 → multilingual-e5-large-1024，提升细节检索 |
| P2 | 历史分析记录 | 保存用户过往分析，支持回顾和对比 |
| P2 | 论点可视化图 | 正反方论点 + 反驳关系图 |

---

## 关于这个项目

这是 Maria Zhu 的 AI 产品经理作品集项目，完整展示了：

1. **发现机会**：从真实用户痛点出发（[用户画像](docs/user-personas.md)）
2. **定义产品**：PRD + 竞品分析 + 用户流程
3. **迭代交付**：5 个版本，每版有评估驱动
4. **度量效果**：自建评估框架（检索命中率、段落完整性、跨视频对比等）
5. **部署上线**：双平台部署，处理平台兼容性问题

> 实习求职中，欢迎联系。📧 zhumaria111@gmail.com
