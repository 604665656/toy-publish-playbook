# B站 Toy 发布前 / 驳回后自检清单

来自一次真实上架（2026-11-07）。**粗体项**是本次实际踩过的。

## A. 包体

- [ ] ZIP 根目录（或恰好一个一级子目录）下有 `index.html`
- [ ] **入口 `index.html` 解压后 ≤ 1MB**（超限报 `307000`，压得再小也没用）
- [ ] 内联脚本/样式/大 JSON 已外置为同层文件，**`url(` 出现 0 次**
- [ ] 外置脚本用**相对路径** `./data.js`，且加载顺序在主逻辑之前
- [ ] 资源路径全部相对；无 `/assets/...` 这类根绝对路径、无根绝对跳转
- [ ] 包内图片任一边 < 10000px
- [ ] 没打进 `.git` / `node_modules` / `__MACOSX` / `.DS_Store` / `toy.yaml`
- [ ] 运行 `toy_doctor.py`；**它报的「朝代长河 · / 真实血脉 ·」两条 ERROR 是误报**，确认 `url(` 为 0 后放行

## B. 素材与元数据

- [ ] 封面 `--poster`：4:3，建议 1200×900，本地图，无人物/旗帜/军阵/地图/乱码文字
- [ ] 图标 `--icon`：1:1，512×512，PNG/JPEG，≤512KB，边长 ≤1024px；**与封面是两个独立字段**
- [ ] `--category` 选对（`GAME` / `INTERACTIVE_PLAY` / `TOOL` / ...）
- [ ] `--slug` 符合 `[A-Za-z0-9_-]` 且 ≤64 字节 —— **发布后不可改**
- [ ] `--visibility` 确认（`public` / `link-only` / `password`）
- [ ] **含自由绘制能力（Canvas 自绘、自由文本输入）→ `create` 时带 `--watermark`**
- [ ] 对外分享地址写成 `https://www.bilibili.com/toy/<slug>/index.html`（带 `index.html`）

## C. 提交

- [ ] `toy whoami --json` 登录态有效
- [ ] **所有写操作带 `--json`；`create` / `update` 带包体必须带 `--yes` 才真正提交审核**
- [ ] 不带 `--yes` 只返回 `preview_url` = 没提交，别以为完事了
- [ ] 提交后 `toy mylist --json` 查 `status`（`auditing` / `published` / `rejected` / timeout）
- [ ] 审核约 100–170 秒，别承诺「发完立即可见」

## D. 本地四道校验（改过数据或页签后必跑）

- [ ] **Node VM 跑数据自检**，桩要补全：`{window:{}, console, location:{search:''}, document:{getElementById:()=>null}}` → `{ok:true}`
- [ ] 抽出内联 `<script>` 后 `node --check`
- [ ] 入口字节数复核
- [ ] **真实浏览器**（扩展连接的 Edge）打开确认首页渲染 —— 内置无头浏览器的空 DOM 快照是假阴性
- [ ] 数组被裁空时，grep 一遍引用点，确认只有 `forEach` / `length` / `find`

## E. 被驳回后

- [ ] **先看完整 `reject_reason` 与 `audit_failures`**，别只截前半句；偶尔会有 `（违法违规）：data.js` + `risk_category`
- [ ] **不要用 `poster_url` / `icon_url` / `watermark_enabled` 为空判断素材上传失败** —— 只在 `published` 后回填
- [ ] 先做 A/B 对照（极简页面 + 完全相同元数据）排除非内容变量 → 见 `methodology.md`
- [ ] 纯元信息更新报 `307034` → **把 Zip 包路径一起传给 `update`**
- [ ] 建立二元判据后并行提交区间探针，别串行盲改
- [ ] 每日 `create` 触顶 `-509` → 改用 `update <已有id>` 复用
- [ ] 结论：词面敏感词替换对语义级审核**无效**，别耗轮次

## F. GitHub 同步

- [ ] 推送前确认 `.git/config` 里没有明文 token
- [ ] 凭据用 `git credential fill` 取，拼进一次性 URL
- [ ] 固定加 `-c http.version=HTTP/1.1 -c http.postBuffer=524288000` 并重试（`502` / `SSL unexpected eof` 是常态）
- [ ] 重试循环里**不要用管道吞掉 git 退出码**，用 `if git push > log 2>&1; then ...`
- [ ] 推完 `git ls-remote origin refs/heads/main` 核对 SHA
- [ ] 再 `grep -c 'ghp_' .git/config` 确认为 0
