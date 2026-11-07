# B站 Toy 上架踩坑看板

一次真实上架的完整复盘：游戏《上下五千年 · 无尽编年》从 **7 轮内容驳回**到 **`status=published`** 的全部踩坑、误判、无效尝试与最终解法。

- 📊 **在线看板（可视化）**：<https://604665656.github.io/toy-publish-playbook/>
- 🗂 **GitHub 原生看板（Projects）**：<https://github.com/users/604665656/projects/12> — 39 张卡片按「处置状态」分列
- 🎮 **线上 Toy**：<https://www.bilibili.com/toy/wqn/index.html>
- 📦 **游戏源码**：<https://github.com/604665656/wqn>

> 所有数字都来自本机实测记录，未做估算或补全。包含**走不通的死路**——这部分通常比成功经验更值钱。

---

## 这个仓库里有什么

| 文件 | 作用 |
| --- | --- |
| `index.html` | 零依赖的单文件交互看板。可直接双击打开（`file://` 也能用），也可由 GitHub Pages 托管 |
| `data/lessons.json` | 全部卡片的结构化源数据（分类 / 严重度 / 状态 / 现象 / 原因 / 解法 / 命令 / 标签） |
| `scripts/build_board.py` | 把 JSON 注入模板重新生成 `index.html`；改完数据跑一次即可 |
| `scripts/gh_project_sync.py` | 把同一份 JSON 同步到 GitHub Projects 原生看板（幂等，可重复运行） |
| `docs/methodology.md` | **审核黑盒下的区间二分定位法**（可迁移到任何「不给理由」的审核） |
| `docs/checklist.md` | 发布前 / 驳回后自检清单 |

看板支持：全文搜索、按 7 个分类筛选、按 4 种状态筛选、严重度过滤、一键「只看已试无效」、点击卡片展开现象/原因/解法/命令、命令一键复制。快捷键 `/` 聚焦搜索、`Esc` 清空。

```bash
python scripts/build_board.py     # 改完 data/lessons.json 后重新生成
```

---

## 一图看懂这次发生了什么

```
7 轮内容驳回（理由恒为「内容审核未通过」）
   ↓  A/B 对照：同账号/封面/图标/水印/分类/标题，只换 1KB 极简页面 → published
锁定：问题 100% 在 data.js 的中文文案
   ↓  模块中性化（CJK→「文」，等长、不改结构）
锁定：只在 civilization / peoples / reading_quiz 三册，其余 20 模块与页面代码清白
   ↓  25 个并行区间探针（P0–P7 / Q0–Q4 / R0–R11），一轮审核读全部结果
锁定：5 个命中区间，共 799 / 4132 条（19%）
   ↓  构建期裁剪，保留 3333 条真实文本（81%）
published @ 2026-11-07 17:06
```

关键判据：**`audit_failures` 里有没有 `type: content`**，而不是 `status`。中性化包虽然仍是 `rejected`，但理由变成「审核未通过」且无 `audit_failures` —— 说明内容关已过，倒在了功能关。这个二元信号让二分成为可能。

---

## 最容易踩的五个坑

1. **局部字段为空 ≠ 上传失败。** `poster_url` / `icon_url` / `watermark_enabled` 只在 `published` 之后回填，`auditing` / `rejected` 一律为空。据此判断「封面没传上去」会白改一整轮。
2. **发布是两段式。** `create` / `update` 带包体不加 `--yes` 只返回 `preview_url`，根本没提交审核；非交互脚本必须同时带 `--yes --json`。
3. **被驳回的 Toy 改任何元信息都要带 Zip 包**（`307034 更新该 toy 需要带上Zip包`），但带包体的 `update` 又不携带 `--watermark` —— 水印只能在 `create` 时开。
4. **关键词替换对内容审核无效。** 40 组等义替换 + 清空 7,568 条外链后依然被拒；是语义/主题级判定，最终靠按条目裁剪解决。
5. **每日 `create` 有上限**（`-509`），并行探针触顶后改用 `update <已有id> <dir>` 复用，不受限制。

---

## 最终上架版做了什么

合规处理**全部放在构建期**（`build_toy.js`），`src/` 与 `data/` 源文件一个字未改，GitHub 上的完整版仍是全量 4132 条：

- 3.3MB 数据外置为 `data.js`，入口 `index.html` 339,778 B（< 1MB 硬上限）
- 7,568 条站外链接 → 0
- 下线 Canvas 自绘的历史舆图页签
- 启动页置顶「虚构历史推演」声明
- 按实测命中区间移除 799 条，并同步放宽运行时数据自检阈值
- 最终 ZIP 509,040 B，只含 `index.html` + `data.js`

上线前四道校验：Node VM 跑数据自检（要补 `document` / `location` 桩）→ `node --check` 校验内联脚本 → 入口字节数 → 真实浏览器打开确认渲染。

> 注意：内置无头浏览器的 DOM 快照可能返回空字符串，是**假阴性**；判断渲染请以真实浏览器为准。

---

## GitHub 原生看板

同一份 `data/lessons.json` 也会同步到 [Projects #12](https://github.com/users/604665656/projects/12)，视图「踩坑看板」为 `BOARD_LAYOUT`，按 `Status` 单选字段分成四列：

| 列 | 张数 | 含义 |
| --- | --- | --- |
| 已解决 | 7 | 曾真实阻断发布，已定位并修好 |
| 已验证有效 | 19 | 实测确认的规律或命令 |
| 长期注意 | 10 | 环境 / 平台行为，换机器仍要留意 |
| 已试无效 | 3 | 走过的死路，明确不要再试 |

卡片正文含现象、原因、处理、可复制命令与标签，标题带 `[R01]` 这类编号，便于和在线看板、JSON 对上。

```bash
python scripts/gh_project_sync.py --report   # 只看当前状态
python scripts/gh_project_sync.py            # 增量同步（幂等，不会重复建卡）
```

凭据取本机 `git credential fill`（需要 `repo` + `project` 权限），脚本不保存也不打印 token；改完 `data/lessons.json` 后先跑 `build_board.py` 再跑 `gh_project_sync.py`，两个看板保持一致。

---

## 复用

- 想看方法论 → [`docs/methodology.md`](docs/methodology.md)
- 想发布前逐项过 → [`docs/checklist.md`](docs/checklist.md)
- 想把卡片导进自己的系统 → `data/lessons.json`

记录日期：2026-11-07 · 平台：B站 Toy · CLI v0.6.4
