#!/usr/bin/env python3
"""把 data/lessons.json 同步成一个 GitHub Projects (V2) 原生看板。

用法：
    python scripts/gh_project_sync.py            # 幂等：已存在的卡片会跳过
    python scripts/gh_project_sync.py --report    # 只打印当前看板状态，不写入

凭据从本机 git credential fill 读取（需要 repo + project scope），
脚本不会把 token 写入任何文件或打印出来。
"""
import json
import pathlib
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "lessons.json").read_text(encoding="utf-8"))
OWNER = "604665656"
REPO = "toy-publish-playbook"
PROJECT_TITLE = "B站 Toy 上架踩坑看板"
BOARD_VIEW = "踩坑看板"
STATUS_FIELD = "处置状态"
GQL = "https://api.github.com/graphql"
REST = "https://api.github.com/repos/%s/%s" % (OWNER, REPO)

STATUS_COLOR = {
    "solved": "GREEN",
    "verified": "BLUE",
    "note": "PURPLE",
    "deadend": "GRAY",
}


def token():
    out = subprocess.check_output(
        ["git", "credential", "fill"],
        input=b"protocol=https\nhost=github.com\n\n",
    ).decode("utf-8", "replace")
    for line in out.splitlines():
        if line.startswith("password="):
            return line[len("password="):]
    raise SystemExit("未找到 GitHub 凭据：请先 git credential 配置或用 gh auth login")


TOKEN = token()


def gql(query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    req = urllib.request.Request(
        GQL,
        data=body,
        headers={
            "Authorization": "Bearer " + TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "User-Agent": "toy-publish-playbook",
        },
    )
    try:
        res = json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        raise SystemExit("GraphQL HTTP %s: %s" % (e.code, e.read().decode()[:500]))
    if res.get("errors"):
        raise SystemExit("GraphQL 错误: " + json.dumps(res["errors"], ensure_ascii=False)[:900])
    return res["data"]


def rest(path):
    req = urllib.request.Request(
        REST + path,
        headers={"Authorization": "Bearer " + TOKEN, "Accept": "application/vnd.github+json"},
    )
    return json.load(urllib.request.urlopen(req, timeout=60))


def viewer_and_repo():
    d = gql("query { viewer { id login } }")
    return d["viewer"]["id"], rest("")["node_id"]


def find_project():
    d = gql("query { viewer { projectsV2(first: 100) { nodes { id title number url } } } }")
    for p in d["viewer"]["projectsV2"]["nodes"]:
        if p["title"] == PROJECT_TITLE:
            return p
    return None


def create_project(owner_id, repo_id):
    d = gql(
        """mutation($o:ID!,$r:ID!,$t:String!){
             createProjectV2(input:{ownerId:$o,repositoryId:$r,title:$t}){
               projectV2{id number url}
             }
           }""",
        {"o": owner_id, "r": repo_id, "t": PROJECT_TITLE},
    )
    return d["createProjectV2"]["projectV2"]


def project_state(project_id):
    q = """query($id:ID!){
      node(id:$id){ ... on ProjectV2 {
        fields(first:30){nodes{
          __typename
          ... on ProjectV2SingleSelectField { id name options{id name color} }
          ... on ProjectV2Field { id name }
        }}
        views(first:20){nodes{id name layout}}
        items(first:100){nodes{ id __typename content{ __typename
          ... on DraftIssue { title } } }}
      }}
    }"""
    return gql(q, {"id": project_id})["node"]


def ensure_status_field(project_id, state):
    fields = [f for f in state["fields"]["nodes"] if f and f.get("name") in ("Status", STATUS_FIELD)]
    field = next((f for f in fields if f.get("options") is not None), None)
    if field is None:
        raise SystemExit("未找到项目自带 Status 单选字段，请检查项目模板")
    options = [
        {"name": s["name"], "color": STATUS_COLOR[s["id"]], "description": s.get("desc", "")}
        for s in DATA["statuses"]
    ]
    if [o["name"] for o in field["options"]] == [o["name"] for o in options]:
        return field
    d = gql(
        """mutation($f:ID!,$n:String!,$o:[ProjectV2SingleSelectFieldOptionInput!]){
             updateProjectV2Field(input:{fieldId:$f,name:$n,singleSelectOptions:$o}){
               projectV2Field{ ... on ProjectV2SingleSelectField { id name options{id name color} } }
             }
           }""",
        # 内置 Status 字段不允许改名，保持原名，只替换选项。
        {"f": field["id"], "n": field["name"], "o": options},
    )
    return d["updateProjectV2Field"]["projectV2Field"]


def ensure_board_view(project_id, state, status_field_id):
    for v in state["views"]["nodes"]:
        if v["name"] == BOARD_VIEW and v["layout"] == "BOARD_LAYOUT":
            return v
    d = gql(
        """mutation($p:ID!,$n:String!){
             createProjectV2View(input:{projectId:$p,name:$n,layout:BOARD_LAYOUT}){
               projectV2View{id name layout}
             }
           }""",
        {"p": project_id, "n": BOARD_VIEW},
    )
    return d["createProjectV2View"]["projectV2View"]


def card_title(l):
    return "[%s] %s" % (l["id"], l["title"])


def card_body(l):
    cat = next((c["name"] for c in DATA["categories"] if c["id"] == l["cat"]), l["cat"])
    st = next((s["name"] for s in DATA["statuses"] if s["id"] == l["status"]), l["status"])
    sev = next((s["name"] for s in DATA["severities"] if s["id"] == l["severity"]), l["severity"])
    lines = [
        "**分类**：%s ｜ **严重度**：%s ｜ **处置状态**：%s" % (cat, sev, st),
        "",
        "### 现象",
        l.get("symptom", "—"),
        "",
        "### 原因",
        l.get("cause", "—"),
        "",
        "### 处理",
        l.get("fix", "—"),
    ]
    if l.get("cmd"):
        lines += ["", "### 复现 / 命令", "```bash", l["cmd"], "```"]
    if l.get("tags"):
        lines += ["", "标签：" + "、".join(l["tags"])]
    lines += [
        "",
        "---",
        "在线看板：https://604665656.github.io/toy-publish-playbook/",
        "方法论：docs/methodology.md ｜ 自检清单：docs/checklist.md",
    ]
    return "\n".join(lines)


def add_cards(project_id, existing_titles):
    todo = [l for l in DATA["lessons"] if card_title(l) not in existing_titles]
    created = {}
    for start in range(0, len(todo), 8):
        batch = todo[start:start + 8]
        parts, variables = [], {"p": project_id}
        for i, l in enumerate(batch):
            variables["t%d" % i] = card_title(l)
            variables["b%d" % i] = card_body(l)
            parts.append(
                "c%d: addProjectV2DraftIssue(input:{projectId:$p,title:$t%d,body:$b%d})"
                "{projectItem{id}}" % (i, i, i)
            )
        var_decl = ",".join(["$p:ID!"] + ["$t%d:String!,$b%d:String" % (i, i) for i in range(len(batch))])
        d = gql("mutation(%s){%s}" % (var_decl, " ".join(parts)), variables)
        for i, l in enumerate(batch):
            created[l["id"]] = d["c%d" % i]["projectItem"]["id"]
        print("  已添加卡片 %d/%d" % (min(start + 8, len(todo)), len(todo)))
    return created


def set_status(project_id, field, item_ids):
    opt = {o["name"]: o["id"] for o in field["options"]}
    # item_ids: dict lesson_id -> project item id
    todo = []
    for l in DATA["lessons"]:
        if l["id"] in item_ids:
            name = next(s["name"] for s in DATA["statuses"] if s["id"] == l["status"])
            todo.append((item_ids[l["id"]], opt[name]))
    for start in range(0, len(todo), 8):
        batch = todo[start:start + 8]
        parts, variables = [], {"p": project_id, "f": field["id"]}
        for i, (item_id, option_id) in enumerate(batch):
            variables["i%d" % i] = item_id
            variables["o%d" % i] = option_id
            parts.append(
                "s%d: updateProjectV2ItemFieldValue(input:{projectId:$p,itemId:$i%d,fieldId:$f,"
                "value:{singleSelectOptionId:$o%d}}){projectV2Item{id}}" % (i, i, i)
            )
        var_decl = ",".join(
            ["$p:ID!,$f:ID!"]
            + ["$i%d:ID!,$o%d:String" % (i, i) for i in range(len(batch))]
        )
        gql("mutation(%s){%s}" % (var_decl, " ".join(parts)), variables)
        print("  已设置状态 %d/%d" % (min(start + 8, len(todo)), len(todo)))


def main():
    report_only = "--report" in sys.argv
    owner_id, repo_id = viewer_and_repo()
    project = find_project()
    if project is None:
        if report_only:
            print("尚未创建项目看板")
            return
        project = create_project(owner_id, repo_id)
        print("已创建项目 #%s %s" % (project["number"], project["url"]))
    else:
        print("复用已有项目 #%s %s" % (project["number"], project["url"]))
    pid = project["id"]
    state = project_state(pid)
    titles = {
        (i.get("content") or {}).get("title")
        for i in state["items"]["nodes"]
        if i and i.get("content")
    }
    print("现有卡片：%d 张" % len([t for t in titles if t]))
    if report_only:
        print("视图：", [(v["name"], v["layout"]) for v in state["views"]["nodes"]])
        print("字段：", [f["name"] for f in state["fields"]["nodes"] if f])
        return

    field = ensure_status_field(pid, state)
    print("状态字段：%s / %s" % (field["name"], [o["name"] for o in field["options"]]))
    view = ensure_board_view(pid, state, field["id"])
    print("看板视图：%s (%s)" % (view["name"], view["layout"]))

    created = add_cards(pid, titles)
    state2 = project_state(pid)
    id_to_item = {}
    for i in state2["items"]["nodes"]:
        c = i.get("content") or {}
        t = c.get("title") or ""
        if t.startswith("[") and "]" in t:
            id_to_item[t[1:t.index("]")]] = i["id"]
    # 刚创建的 item 可能因最终一致性尚未出现在查询结果里，用创建返回值补齐。
    for lesson_id, item_id in created.items():
        id_to_item[lesson_id] = item_id
    set_status(pid, field, id_to_item)
    print("\n完成：%s" % project["url"])
    print("在线可视化看板：https://604665656.github.io/toy-publish-playbook/")


if __name__ == "__main__":
    main()
