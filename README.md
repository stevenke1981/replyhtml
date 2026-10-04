# replyhtml — STE Reply Rules for AI Agents

[English](#english) | [繁體中文](#繁體中文)

## English

This project gives AI agents a set of rules for clear replies. The rules use ASD-STE100 Simplified Technical English as their base. Each reply uses a fixed Markdown structure. An optional HTML viewer shows the reply and its score.

The target is 90% or more of prose sentences with no linter finding. This is a style gate. It does not certify full ASD-STE100 compliance.

### Contents

| File | Purpose |
|---|---|
| [`STE-REPLY-RULES.md`](STE-REPLY-RULES.md) | Rules for agent replies. Add them to `CLAUDE.md`, `AGENTS.md`, or a system prompt. |
| [`tools/ste_score.py`](tools/ste_score.py) | Score gate. It calculates the percent of prose sentences with no finding. |
| [`viewer.html`](viewer.html) | Optional viewer. It shows a Markdown reply as HTML and marks the sentences with findings. |
| [`replies/example.md`](replies/example.md) | Example reply with a score of 100%. |

### Requirements

- Python 3.10 or later.
- The local `asd-ste100` skill. The score script uses its Markdown parser and its agent-profile linter.
- A modern browser for `viewer.html`. The viewer loads `marked` and `DOMPurify` from cdnjs.

The script looks for the skill in `~/.claude/skills/asd-ste100`. If the skill is in a different folder, set `STE_SKILL_DIR`:

```bash
export STE_SKILL_DIR=/path/to/asd-ste100
```

### Quick start

1. Clone the repository.

   ```bash
   git clone https://github.com/stevenke1981/replyhtml.git
   cd replyhtml
   ```

2. Add the rules to your agent. For Claude Code, add this line to the project `CLAUDE.md`:

   ```markdown
   Obey the reply rules in @STE-REPLY-RULES.md.
   ```

3. Score a reply.

   ```bash
   python tools/ste_score.py replies/example.md
   ```

4. Optional: open `viewer.html` in a browser. Then open a `.md` file, drop a file on the page, or paste Markdown.

### Score script

```bash
python tools/ste_score.py reply.md                      # description mode, 25 words per sentence
python tools/ste_score.py reply.md --mode procedure     # instruction mode, 20 words per sentence
python tools/ste_score.py reply.md --min 95             # change the minimum percent
python tools/ste_score.py reply.md --errors-only        # count only ERROR findings
python tools/ste_score.py reply.md --json               # machine-readable output
```

| Exit code | Meaning |
|---|---|
| `0` | The score is equal to or more than the minimum. |
| `1` | The score is less than the minimum. |
| `2` | The script cannot find the file or the skill. |

The script counts prose sentences only. It does not count code blocks, inline code, paths, URLs, or flags. A sentence fails if it has one or more findings. The script also finds contractions, because the skill linter does not check them.

Example output:

```text
STE score: 50.0% (3/6 sentences) - minimum 90.0% - FAIL
  L2: [contraction] I've gone ahead and fixed the bug.
  L2: [passive-voice] The tests are being run right now.
  L2: [marketing-adjective] We leverage a robust cache.
```

### HTML viewer

- Open `viewer.html` directly from the disk. You do not need a server.
- If you serve the folder over HTTP, you can load a file with a URL parameter: `viewer.html?src=replies/example.md`.
- The viewer shows the score, a 90% target line, and a list of findings.
- The viewer uses simple browser checks. Use `tools/ste_score.py` as the gate.

### Reply format

The rules tell the agent to use this structure when a reply has more than 3 sentences:

```markdown
## Result
The main answer or status.

## Details
- One fact or one change in each item.

## Steps
1. One instruction in each step.

## Open items
- Missing facts, risks, or work that is not done.
```

### Limits

- The checks are heuristic. They do not use the official ASD-STE100 dictionary.
- The checks cannot compare the meaning of a source and a rewrite.
- STE applies to English. For other languages, the rules apply the same sentence structure only.

### Credits

- ASD-STE100 is a specification of ASD. This project is not affiliated with ASD. See [asd-ste100.org](https://www.asd-ste100.org/).
- The `asd-ste100` skill includes work from [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill) (MIT License).

## 繁體中文

這個專案提供一套給 AI agent 的回覆規則，以 ASD-STE100（簡化技術英文）為基礎。回覆一律使用固定的 Markdown 結構，也可以選擇用 HTML 檢視器顯示回覆和分數。

目標是 90% 以上的散文句沒有 linter finding。這是風格門檻，不代表完全符合 ASD-STE100。

### 檔案

| 檔案 | 用途 |
|---|---|
| `STE-REPLY-RULES.md` | Agent 回覆規則，可放進 `CLAUDE.md`、`AGENTS.md` 或 system prompt |
| `tools/ste_score.py` | 評分門檻：計算沒有 finding 的散文句比例 |
| `viewer.html` | 可選的 HTML 檢視器，會標示有 finding 的句子 |
| `replies/example.md` | 100 分的範例回覆 |

### 使用方式

1. 安裝 `asd-ste100` skill（預設路徑 `~/.claude/skills/asd-ste100`，其他路徑請設定 `STE_SKILL_DIR`）。
2. 在專案的 `CLAUDE.md` 加入：`Obey the reply rules in @STE-REPLY-RULES.md.`
3. 執行評分：`python tools/ste_score.py reply.md`。分數低於 90% 時 exit code 為 `1`。
4. 可選：用瀏覽器開啟 `viewer.html`，然後選擇檔案、拖放檔案或貼上 Markdown。

### 注意事項

- 評分只計算散文句，不計算程式碼、路徑、URL 和參數。
- 檢查是啟發式的，不會比對官方 ASD-STE100 詞典，也無法判斷改寫後語意是否相同。
- STE 只適用於英文。如果回覆語言是中文，規則只套用相同的句型原則：短句、一句一個概念、主動語態、一個詞只指一件事。
- 如果你的全域設定要求用中文回覆，agent 不會自動改用英文。需要英文 STE 回覆時，請在專案層級另外指定。
