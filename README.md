# changyelian skill

`changyelian` 是一个中文产业链核验、深度拆解和内容生产 Codex skill。

它适合处理中文产业链选题、公司、新闻、传闻、研报观点、财报问题或市场热点，并输出公开资料核验、产业链分析、合规解读、短视频口播文案、分镜脚本、素材建议和标题封面方向。

## 能做什么

- 中文产业链事实核验
- 深度产业链拆解
- 行业状态、路线变化、价值迁移和反证条件分析
- 成本价值量、利润价值量、瓶颈价值量三层判断
- 材料端、设备端、技术/工艺端拆解
- 合规降级表达，避免荐股和名单感
- 抖音/YouTube 公开视频学习
- 中文短视频口播文案、分镜脚本和素材清单

## 使用边界

这个 skill 只做公开资料学习、产业链科普和内容创作。

它不会提供：

- 荐股
- 股票池
- 买卖建议
- 目标价
- 涨跌预测
- 收益承诺
- 引流话术

涉及公司名称、财务数据、行业数字、公开来源、平台合规和版权素材时，发布前仍需人工复核。

## 安装

把 `changyelian` 文件夹复制到本机 Codex skills 目录：

```powershell
Copy-Item -Recurse .\changyelian C:\Users\$env:USERNAME\.codex\skills\
```

然后重新打开 Codex 会话，或等待 skills 刷新。

## 示例

```text
changyelian 玻璃基板产业链
changyelian 帮我把这篇研报逻辑改成合规口播
changyelian 做一期 AI 服务器 PCB 的五分钟稿
```

## 目录

```text
changyelian/
  SKILL.md
  references/
  examples/
  scripts/
  templates/
```
