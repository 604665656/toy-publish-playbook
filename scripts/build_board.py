#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 data/lessons.json 注入零依赖的单文件看板 index.html。
用法：python scripts/build_board.py
产物：index.html（自包含，file:// 与 GitHub Pages 均可打开）
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "lessons.json").read_text(encoding="utf-8"))

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<meta name="description" content="B站 Toy 上架踩坑实测看板：平台规则、CLI、内容审核、二分定位、构建与推送">
<style>
:root{
  --bg:#f6f8fa; --panel:#ffffff; --line:#d8dee4; --line2:#eaeef2;
  --ink:#1f2328; --dim:#59636e; --faint:#8b949e;
  --brand:#0969da; --brand-soft:#ddf4ff;
  --ok:#1a7f37; --warn:#9a6700; --dead:#6e7781;
  --shadow:0 1px 0 rgba(31,35,40,.04),0 3px 12px rgba(31,35,40,.06);
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:var(--bg); color:var(--ink);
  font:14px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei","PingFang SC",Hiragino Sans GB,sans-serif;
  -webkit-font-smoothing:antialiased;
}
a{color:var(--brand);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1240px;margin:0 auto;padding:0 24px 72px}

/* ---------- header ---------- */
header{background:#fff;border-bottom:1px solid var(--line)}
.hd{max-width:1240px;margin:0 auto;padding:28px 24px 22px}
.kicker{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:10px}
.pill{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--line);background:var(--bg);
  border-radius:999px;padding:3px 11px;font-size:12px;color:var(--dim)}
.pill b{color:var(--ink);font-weight:600}
.pill.live{background:#dafbe1;border-color:#a6e9b9;color:#0f5323}
h1{font-size:27px;line-height:1.3;margin:0 0 6px;letter-spacing:-.4px;font-weight:700}
.sub{color:var(--dim);font-size:14px;margin:0 0 18px}
.links{display:flex;gap:16px;flex-wrap:wrap;font-size:13px}

/* ---------- stats ---------- */
.stats{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin:22px 0 18px}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:13px 14px;box-shadow:var(--shadow)}
.stat .v{font-size:19px;font-weight:700;letter-spacing:-.3px;line-height:1.3}
.stat .l{font-size:11.5px;color:var(--dim);margin-top:3px}

/* ---------- flow ---------- */
.flow{background:var(--panel);border:1px solid var(--line);border-radius:10px;
  padding:13px 16px;margin-bottom:20px;display:flex;align-items:center;gap:8px;flex-wrap:wrap;box-shadow:var(--shadow)}
.flow .step{font-size:12.5px;background:var(--bg);border:1px solid var(--line2);border-radius:7px;padding:5px 10px;color:var(--dim)}
.flow .step b{color:var(--ink)}
.flow .step.hit{background:#fff1e5;border-color:#f0c48a;color:#8a4b00}
.flow .step.pass{background:#dafbe1;border-color:#a6e9b9;color:#0f5323}
.flow .arw{color:var(--faint);font-size:13px}

/* ---------- toolbar ---------- */
.toolbar{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-bottom:16px;box-shadow:var(--shadow)}
.trow{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.trow + .trow{margin-top:11px;padding-top:11px;border-top:1px solid var(--line2)}
.tlabel{font-size:12px;color:var(--faint);min-width:52px;letter-spacing:.4px}
#q{flex:1;min-width:220px;border:1px solid var(--line);border-radius:7px;padding:8px 11px;
  font:inherit;font-size:13px;color:var(--ink);background:#fff;outline:none}
#q:focus{border-color:var(--brand);box-shadow:0 0 0 3px var(--brand-soft)}
select{border:1px solid var(--line);border-radius:7px;padding:7px 9px;font:inherit;font-size:13px;background:#fff;color:var(--ink)}
.chip{border:1px solid var(--line);background:#fff;border-radius:999px;padding:5px 11px;
  font-size:12.5px;color:var(--dim);cursor:pointer;user-select:none;transition:.12s;white-space:nowrap}
.chip:hover{border-color:var(--faint)}
.chip.on{background:var(--brand);border-color:var(--brand);color:#fff;font-weight:600}
.chip .n{opacity:.65;margin-left:4px;font-size:11px}
.chip.dot::before{content:"";display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:6px;vertical-align:1px}
.toggle{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;color:var(--dim);cursor:pointer;user-select:none}
.toggle input{accent-color:var(--brand)}
#count{margin-left:auto;font-size:12.5px;color:var(--faint);white-space:nowrap}

/* ---------- cards ---------- */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:12px;align-items:start}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;box-shadow:var(--shadow);
  overflow:hidden;cursor:pointer;transition:border-color .14s,box-shadow .14s}
.card:hover{border-color:#b6c2cf;box-shadow:0 4px 16px rgba(31,35,40,.09)}
.card.open{border-color:var(--brand);box-shadow:0 4px 18px rgba(9,105,218,.13)}
.card.dead{background:#fbfcfd}
.card.dead .ttl{color:#57606a}
.chead{padding:13px 15px}
.meta{display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin-bottom:9px}
.id{font:600 11px/1 ui-monospace,SFMono-Regular,Consolas,monospace;color:var(--faint);letter-spacing:.5px}
.cat{font-size:11.5px;font-weight:600;padding:2px 8px;border-radius:5px}
.sev{font-size:11px;padding:2px 7px;border-radius:5px;border:1px solid}
.sev.blocker{color:#a40e26;background:#ffebe9;border-color:#ffcecb}
.sev.high{color:#9a6700;background:#fff8c5;border-color:#f2d97a}
.sev.mid{color:#0969da;background:#ddf4ff;border-color:#b6e3ff}
.sev.low{color:#57606a;background:#f6f8fa;border-color:#d8dee4}
.st{font-size:11px;margin-left:auto;padding:2px 8px;border-radius:999px;font-weight:600}
.st.solved{background:#dafbe1;color:#116329}
.st.verified{background:#ddf4ff;color:#0550ae}
.st.note{background:#f3eefe;color:#6639ba}
.st.deadend{background:#eaeef2;color:#57606a;text-decoration:line-through}
.ttl{font-size:14.5px;font-weight:650;line-height:1.5;margin:0 0 9px}
.tags{display:flex;gap:5px;flex-wrap:wrap}
.tag{font-size:10.5px;color:var(--dim);background:var(--bg);border:1px solid var(--line2);border-radius:4px;padding:1px 6px}
.detail{display:none;border-top:1px solid var(--line2);background:#fbfcfd;padding:14px 15px 16px}
.card.open .detail{display:block}
.fld{margin-bottom:12px}
.fld:last-child{margin-bottom:0}
.fld .k{font-size:11px;font-weight:700;color:var(--faint);letter-spacing:.6px;margin-bottom:4px}
.fld .v{font-size:13px;color:#30363d;white-space:pre-wrap;word-break:break-word}
.fld.fix .v{border-left:3px solid var(--ok);padding-left:10px}
pre.cmd{margin:0;background:#1f2328;color:#e6edf3;border-radius:7px;padding:10px 12px;
  font:12px/1.6 ui-monospace,SFMono-Regular,Consolas,monospace;overflow-x:auto;white-space:pre-wrap;word-break:break-all;position:relative}
.cp{position:absolute;top:6px;right:6px;background:#30363d;color:#c9d1d9;border:0;border-radius:5px;
  font-size:10.5px;padding:3px 7px;cursor:pointer;opacity:.75}
.cp:hover{opacity:1}
.empty{grid-column:1/-1;text-align:center;padding:48px 0;color:var(--faint);font-size:14px}
footer{margin-top:34px;padding-top:18px;border-top:1px solid var(--line);color:var(--faint);font-size:12px;
  display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
@media (max-width:900px){.stats{grid-template-columns:repeat(3,1fr)}}
@media (max-width:560px){.stats{grid-template-columns:repeat(2,1fr)}.wrap,.hd{padding-left:14px;padding-right:14px}h1{font-size:22px}}
</style>
</head>
<body>
<header>
  <div class="hd">
    <div class="kicker">
      <span class="pill">实测记录 · <b>__DATE__</b></span>
      <span class="pill">项目 <b>__PROJECT__</b></span>
      <span class="pill live">● 已过审发布</span>
    </div>
    <h1>__TITLE__</h1>
    <p class="sub">__SUBTITLE__</p>
    <div class="links">
      <a href="__LIVE__" target="_blank" rel="noopener">→ 线上 Toy</a>
      <a href="__REPO__" target="_blank" rel="noopener">→ 游戏源码仓库</a>
      <a href="docs/methodology.md">→ 二分定位方法论</a>
      <a href="docs/checklist.md">→ 发布前自检清单</a>
      <a href="data/lessons.json">→ 结构化数据 JSON</a>
    </div>
  </div>
</header>

<div class="wrap">
  <div class="stats" id="stats"></div>

  <div class="flow">
    <span class="step"><b>7 轮</b>内容驳回</span><span class="arw">→</span>
    <span class="step"><b>A/B 对照</b>锁定 data.js 文案</span><span class="arw">→</span>
    <span class="step"><b>25 个</b>并行区间探针</span><span class="arw">→</span>
    <span class="step hit"><b>5 段 / 799 条</b>命中</span><span class="arw">→</span>
    <span class="step pass"><b>published</b> 17:06</span>
  </div>

  <div class="toolbar">
    <div class="trow">
      <span class="tlabel">搜索</span>
      <input id="q" type="search" placeholder="搜标题 / 现象 / 解法 / 标签 / 命令，按 / 快速聚焦" autocomplete="off">
      <select id="sev">
        <option value="">全部严重度</option>
        <option value="blocker">阻断</option>
        <option value="high">高</option>
        <option value="mid">中</option>
        <option value="low">提示</option>
      </select>
      <label class="toggle"><input type="checkbox" id="onlyDead"> 只看「已试无效」死路</label>
      <span id="count"></span>
    </div>
    <div class="trow"><span class="tlabel">分类</span><span id="cats"></span></div>
    <div class="trow"><span class="tlabel">状态</span><span id="sts"></span></div>
  </div>

  <div class="grid" id="grid"></div>

  <footer>
    <span>数据来源：本机实测 + 官方 CLI <code>--help</code> + 平台发布后台。所有数字保留原始观测值。</span>
    <span>按 <b>/</b> 聚焦搜索 · <b>Esc</b> 清空 · 点击卡片展开详情</span>
  </footer>
</div>

<script>
"use strict";
const D = __DATA_JSON__;
const CATS = Object.fromEntries(D.categories.map(c => [c.id, c]));
const STS  = Object.fromEntries(D.statuses.map(s => [s.id, s]));
const SEV  = Object.fromEntries(D.severities.map(s => [s.id, s]));

let state = { q:"", cat:"", st:"", sev:"", onlyDead:false };

const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c =>
  ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));

/* stats */
document.getElementById("stats").innerHTML = D.meta.stats.map(s =>
  '<div class="stat"><div class="v">' + esc(s.value) + '</div><div class="l">' + esc(s.label) + '</div></div>'
).join("");

/* chips */
function chips(el, items, key, field){
  const counts = {};
  D.lessons.forEach(l => { counts[l[field]] = (counts[l[field]] || 0) + 1; });
  let html = '<span class="chip' + (state[key] === "" ? " on" : "") + '" data-k="' + key + '" data-v="">全部<span class="n">' + D.lessons.length + '</span></span>';
  items.forEach(it => {
    html += '<span class="chip' + (state[key] === it.id ? " on" : "") + '" data-k="' + key + '" data-v="' + it.id + '">'
          + (it.color ? '<span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:' + it.color + ';margin-right:6px"></span>' : '')
          + esc(it.name) + '<span class="n">' + (counts[it.id] || 0) + '</span></span>';
  });
  el.innerHTML = html;
}
chips(document.getElementById("cats"), D.categories, "cat", "cat");
chips(document.getElementById("sts"), D.statuses, "st", "status");

function matches(l){
  if (state.cat && l.cat !== state.cat) return false;
  if (state.st && l.status !== state.st) return false;
  if (state.sev && l.severity !== state.sev) return false;
  if (state.onlyDead && l.status !== "deadend") return false;
  if (state.q) {
    const hay = [l.id, l.title, l.symptom, l.cause, l.fix, l.cmd, (l.tags || []).join(" "), CATS[l.cat].name].join(" ").toLowerCase();
    if (!hay.includes(state.q.toLowerCase().trim())) return false;
  }
  return true;
}

function cardHTML(l){
  const c = CATS[l.cat], s = STS[l.status], v = SEV[l.severity];
  const tags = (l.tags || []).map(t => '<span class="tag">' + esc(t) + '</span>').join("");
  const fld = (k, val, cls) => val ? '<div class="fld ' + (cls||"") + '"><div class="k">' + k + '</div><div class="v">' + esc(val) + '</div></div>' : "";
  const cmd = l.cmd ? '<div class="fld"><div class="k">命令 / 证据</div><pre class="cmd">' + esc(l.cmd)
    + '<button class="cp" type="button">复制</button></pre></div>' : "";
  return '<article class="card' + (l.status === "deadend" ? " dead" : "") + '" data-id="' + l.id + '">'
    + '<div class="chead"><div class="meta">'
    +   '<span class="id">' + l.id + '</span>'
    +   '<span class="cat" style="color:' + c.color + ';background:' + c.color + '18">' + esc(c.name) + '</span>'
    +   '<span class="sev ' + l.severity + '">' + v.name + '</span>'
    +   '<span class="st ' + l.status + '">' + s.name + '</span>'
    + '</div><h3 class="ttl">' + esc(l.title) + '</h3><div class="tags">' + tags + '</div></div>'
    + '<div class="detail">'
    +   fld("现象", l.symptom) + fld("原因", l.cause) + fld("解法", l.fix, "fix") + cmd
    + '</div></article>';
}

function render(){
  const list = D.lessons.filter(matches).sort((a,b) =>
    (SEV[b.severity].rank - SEV[a.severity].rank) || a.id.localeCompare(b.id));
  document.getElementById("grid").innerHTML = list.length
    ? list.map(cardHTML).join("")
    : '<div class="empty">没有匹配的卡片，换个筛选条件试试。</div>';
  document.getElementById("count").textContent = "显示 " + list.length + " / " + D.lessons.length + " 条";
}

document.addEventListener("click", e => {
  const chip = e.target.closest(".chip");
  if (chip) {
    state[chip.dataset.k] = chip.dataset.v;
    document.querySelectorAll('.chip[data-k="' + chip.dataset.k + '"]').forEach(x =>
      x.classList.toggle("on", x.dataset.v === chip.dataset.v));
    render(); return;
  }
  const cp = e.target.closest(".cp");
  if (cp) {
    e.stopPropagation();
    const txt = cp.parentElement.childNodes[0].textContent.trim();
    navigator.clipboard.writeText(txt).then(() => { cp.textContent = "已复制"; setTimeout(() => cp.textContent = "复制", 1200); });
    return;
  }
  const card = e.target.closest(".card");
  if (card) card.classList.toggle("open");
});

document.getElementById("q").addEventListener("input", e => { state.q = e.target.value; render(); });
document.getElementById("sev").addEventListener("change", e => { state.sev = e.target.value; render(); });
document.getElementById("onlyDead").addEventListener("change", e => { state.onlyDead = e.target.checked; render(); });
document.addEventListener("keydown", e => {
  if (e.key === "/" && document.activeElement.id !== "q") { e.preventDefault(); document.getElementById("q").focus(); }
  if (e.key === "Escape") { const q = document.getElementById("q"); q.value = ""; state.q = ""; render(); q.blur(); }
});

render();
</script>
</body>
</html>
"""

out = (TEMPLATE
       .replace("__TITLE__", DATA["meta"]["title"])
       .replace("__SUBTITLE__", DATA["meta"]["subtitle"])
       .replace("__DATE__", DATA["meta"]["date"])
       .replace("__PROJECT__", DATA["meta"]["project"])
       .replace("__LIVE__", DATA["meta"]["live"])
       .replace("__REPO__", DATA["meta"]["repo"])
       # 数据文本里可能出现字面 </script>，直接注入会提前闭合 <script> 导致整页失效。
       # JSON 字符串中 "\/" 是合法的转义，写成 <\/ 后浏览器与 JSON.parse 都能正确还原。
       .replace("__DATA_JSON__", json.dumps(DATA, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")))

path = ROOT / "index.html"
path.write_text(out, encoding="utf-8")
print("生成", path, path.stat().st_size, "bytes；卡片", len(DATA["lessons"]), "条")
