# 🌱 Greenhouse Job Board API: live jobs, companies, and new postings

A Python and MCP quick-start for the **Greenhouse job board API** on Apify. Pull live jobs from any Greenhouse-hosted career site, discover companies hiring through Greenhouse, and track new or changed postings, all without a Harvest key or a login.

- Actor: [Greenhouse Job Board API on Apify](https://apify.com/johnvc/greenhouse-job-board-api?fpr=9n7kx3)
- Input schema: [input parameters](https://apify.com/johnvc/greenhouse-job-board-api/input-schema?fpr=9n7kx3)
- Get a free API token: [apify.com](https://apify.com?fpr=9n7kx3)

Greenhouse is the applicant tracking system behind the career pages of thousands of companies, including Stripe, Airbnb, GitLab, and Anthropic. This Actor reads the public Greenhouse job board API live at run time, so every row reflects what the board says right now, not what an index remembered last week. Give it board tokens or URLs, or give it nothing and let it sweep a bundled directory of 4,400+ verified boards.

[![Watch the walkthrough](https://img.youtube.com/vi/jREWahDGhJM/maxresdefault.jpg)](https://www.youtube.com/watch?v=jREWahDGhJM)

### Text walkthrough

The **Greenhouse job board API** takes company board tokens (stripe, gitlab) or any boards.greenhouse.io URL, and returns structured job rows: `title`, `companyName`, `departments`, `location`, `isRemote`, `datePublished`, `dateUpdated`, `salaryRaw`, `salaryDerived`, and the description as Markdown by default. Set `updatedAfter` to a window like `25h` and only jobs the employer touched since then come back, which is how the "Track New Greenhouse Job Postings Daily" task turns a schedule into a change feed with zero state. Switch `outputMode` to `companiesOnly` and you get one row per company hiring through Greenhouse with a live open-jobs count, the fastest way to find companies using Greenhouse ATS. Filters run before billing, so a filtered job costs nothing.

## Quick Start

Prerequisites: Python 3.11 or newer, [uv](https://docs.astral.sh/uv/), and a free Apify API token from [apify.com](https://apify.com?fpr=9n7kx3).

```bash
git clone https://github.com/johnisanerd/Apify-Greenhouse-Job-Board-API.git
cd Apify-Greenhouse-Job-Board-API
uv sync
cp .env.example .env          # paste your token into .env
uv run python greenhouse-job-board-api-example.py
```

Each example is a separate flag:

```bash
uv run python greenhouse-job-board-api-example.py --example jobs       # full job records
uv run python greenhouse-job-board-api-example.py --example companies  # company discovery
uv run python greenhouse-job-board-api-example.py --example new-jobs   # change detection
uv run python greenhouse-job-board-api-example.py --example markdown   # LLM-ready descriptions
uv run python greenhouse-job-board-api-example.py --example salary     # postings with pay data
uv run python greenhouse-job-board-api-example.py --example all
```

Every example asks for a small number of rows on purpose. You pay per row delivered, so confirm the shape of the data first, then raise `maxJobs`.

## Why use this API

**Live, not indexed.** One request per board against the public API means every row is what the employer's board says right now. No stale index, no ghost jobs.

**Discovery built in.** A bundled directory of 4,400+ verified Greenhouse boards powers `companiesOnly` mode and empty-input sweeps. Nobody else combines the directory and the scraper in one tool.

**Change detection without state.** Every Greenhouse job carries the employer's own `updated_at` and `first_published` timestamps, so `updatedAfter: "25h"` on a daily schedule is a complete change feed. No seen-lists, no delta stores.

**Pay for exactly what you receive.** No start fee, no minimum. The base job record is one event; Markdown, HTML, text, application questions, and the run report are add-ons billed only on rows that carry them. Filters run before billing.

**Salary data two ways.** Published pay ranges pass through verbatim as `salaryRaw`; a deterministic parser adds `salaryDerived` with min, max, currency, and period from the description text.

## Recipes

Ready-made configurations with their own Store landing pages:

- [Use the Greenhouse Job Board API Without a Key](https://apify.com/johnvc/greenhouse-job-board-api/examples/greenhouse-job-board-api-no-key?fpr=9n7kx3)
- [Find Companies Using Greenhouse ATS](https://apify.com/johnvc/greenhouse-job-board-api/examples/find-companies-using-greenhouse?fpr=9n7kx3)
- [Track New Greenhouse Job Postings Daily](https://apify.com/johnvc/greenhouse-job-board-api/examples/track-new-greenhouse-jobs-daily?fpr=9n7kx3)
- [Greenhouse Jobs as Markdown for AI Agents](https://apify.com/johnvc/greenhouse-job-board-api/examples/greenhouse-jobs-markdown-ai-agents?fpr=9n7kx3)
- [Greenhouse Job Postings With Salary Data](https://apify.com/johnvc/greenhouse-job-board-api/examples/greenhouse-job-postings-salary-data?fpr=9n7kx3)

**Schedule tip.** Save your input as a Task in the [Apify Console](https://console.apify.com), set `updatedAfter` to `25h`, and schedule it daily. From then on the dataset only ever contains jobs that changed since the last run, so the pipeline stays current without anyone touching it.

## Usage Examples

Basic, matching the default run:

```json
{
  "companies": ["gitlab", "stripe"],
  "titleKeywords": ["engineer"],
  "maxJobs": 10
}
```

Advanced, a discovery sweep with every add-on on:

```json
{
  "discoveryQuery": "labs",
  "maxCompanies": 5,
  "maxJobs": 100,
  "includeDescriptionMarkdown": true,
  "includeDescriptionHtml": true,
  "includeQuestions": true,
  "report": "markdown"
}
```

## Input Parameters

Every parameter is optional.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `companies` | array | `["stripe"]` | Board tokens or any board, embed, or single-job URL, mixed freely. Empty sweeps the bundled directory. |
| `startUrls` | array | empty | Same values in URL-list form; merged with `companies`. |
| `outputMode` | string | `jobs` | `jobs` for full records, `urlsOnly` for the cheap index, `companiesOnly` for discovery. |
| `discoveryQuery` | string | empty | Text match over the company directory for discovery and sweeps. |
| `verifyCompanies` | boolean | `true` | Live-probe each discovered company; dead boards are never billed. |
| `titleKeywords` | array | empty | Keep jobs whose title contains any of these. Runs before billing. |
| `departments` | array | empty | Keep jobs in matching departments. |
| `locationKeywords` | array | empty | Keep jobs in matching locations or offices. |
| `updatedAfter` | string | empty | Change detection: `24h`, `7d`, `2w`, or an ISO date. |
| `publishedAfter` | string | empty | Same grammar, against the first-published date. |
| `includeDescriptionMarkdown` | boolean | `true` | Add the description as Markdown (paid add-on). |
| `includeDescriptionHtml` | boolean | `false` | Add the original HTML (paid add-on). |
| `includeDescriptionText` | boolean | `false` | Add plain text (paid add-on). |
| `includeQuestions` | boolean | `false` | Add application form questions (paid add-on). |
| `report` | string | `none` | Write a Markdown or HTML run report to the key-value store (paid add-on). |
| `maxCompanies` | integer | `25` | Cap on companies in sweeps and discovery. |
| `maxJobsPerCompany` | integer | `0` | Per-board cap, 0 means all. |
| `maxJobs` | integer | `100` | Whole-run cap, the main cost control. |
| `maxConcurrency` | integer | `5` | Parallel per-job requests. |
| `proxyConfiguration` | object | direct | Optional Apify Proxy settings; direct connections work. |

## Output Format

A full job record:

```json
{
  "resultType": "job",
  "id": "8503792002",
  "title": "Account Executive - Italy",
  "companyName": "GitLab",
  "boardToken": "gitlab",
  "url": "https://job-boards.greenhouse.io/gitlab/jobs/8503792002",
  "departments": [{ "id": 4011044002, "name": "Sales" }],
  "location": "Remote, Italy",
  "isRemote": true,
  "language": "en",
  "datePublished": "2026-04-17T05:58:03-04:00",
  "dateUpdated": "2026-08-10T16:52:46-04:00",
  "salaryDerived": { "min": 71400, "max": 126000, "currency": "EUR", "period": "year", "source": "description-regex" },
  "descriptionMarkdown": "## About the role\n\nGitLab is looking for...",
  "source": "greenhouse",
  "scrapedAt": "2026-08-25T16:00:00Z"
}
```

A discovered company row:

```json
{
  "resultType": "company",
  "boardToken": "gitlab",
  "boardUrl": "https://boards.greenhouse.io/gitlab",
  "companyName": "GitLab",
  "jobCount": 210,
  "live": true,
  "region": "us",
  "verifiedAt": "2026-08-25T16:00:00Z"
}
```

<!-- ask-ai:start -->
## 🤖 Ask an AI assistant about this Actor

Open a ready-to-send prompt about the Greenhouse Job Board API in the AI of your choice:

- 💬 [ChatGPT](https://chatgpt.com/?q=Using%20the%20Greenhouse%20Job%20Board%20API%20on%20Apify%20%28https://apify.com/johnvc/greenhouse-job-board-api?fpr=9n7kx3%29%2C%20walk%20me%20through%20this%20use%20case:%20%22Use%20the%20Greenhouse%20Job%20Board%20API%20Without%20a%20Key%22.%20Show%20me%20the%20input%20JSON%2C%20the%20output%20fields%2C%20and%20how%20to%20automate%20it%20with%20the%20API%20or%20MCP.)
- 🧠 [Claude](https://claude.ai/new?q=Using%20the%20Greenhouse%20Job%20Board%20API%20on%20Apify%20%28https://apify.com/johnvc/greenhouse-job-board-api?fpr=9n7kx3%29%2C%20walk%20me%20through%20this%20use%20case:%20%22Use%20the%20Greenhouse%20Job%20Board%20API%20Without%20a%20Key%22.%20Show%20me%20the%20input%20JSON%2C%20the%20output%20fields%2C%20and%20how%20to%20automate%20it%20with%20the%20API%20or%20MCP.)
- 🔍 [Perplexity](https://www.perplexity.ai/search?q=Using%20the%20Greenhouse%20Job%20Board%20API%20on%20Apify%20%28https://apify.com/johnvc/greenhouse-job-board-api?fpr=9n7kx3%29%2C%20walk%20me%20through%20this%20use%20case:%20%22Use%20the%20Greenhouse%20Job%20Board%20API%20Without%20a%20Key%22.%20Show%20me%20the%20input%20JSON%2C%20the%20output%20fields%2C%20and%20how%20to%20automate%20it%20with%20the%20API%20or%20MCP.)
- 🅒 [Copilot](https://copilot.microsoft.com/?q=Using%20the%20Greenhouse%20Job%20Board%20API%20on%20Apify%20%28https://apify.com/johnvc/greenhouse-job-board-api?fpr=9n7kx3%29%2C%20walk%20me%20through%20this%20use%20case:%20%22Use%20the%20Greenhouse%20Job%20Board%20API%20Without%20a%20Key%22.%20Show%20me%20the%20input%20JSON%2C%20the%20output%20fields%2C%20and%20how%20to%20automate%20it%20with%20the%20API%20or%20MCP.)
<!-- ask-ai:end -->

## People also search for

### Is this a Greenhouse scraper?

Under the hood it reads the same public endpoints a scraper would. What you get is an API: structured JSON on demand, filters, stable field names, and no HTML unless you ask for it. If you have been maintaining your own scrape of Greenhouse boards, this is the version where someone else maintains the parser.

### What is boards-api.greenhouse.io?

The public, read-only job board API that powers every hosted Greenhouse career page. This Actor reads it directly, which is why results are live rather than indexed.

### Do I need a Greenhouse Harvest API key?

No. The Harvest API is Greenhouse's private, authenticated API for employers. This Actor uses only the public job board layer, so there is nothing to sign up for.

### How do I find companies that use Greenhouse?

Set `outputMode` to `companiesOnly`. You get one row per company with its board token, a live open-jobs count, and the board URL. The `--example companies` script does exactly this.

### How do I get only new job postings?

Set `updatedAfter` (any change) or `publishedAfter` (new roles only) to a window like `24h` or an ISO date. The Actor uses the employer's own timestamps, so there is no state to manage between runs.

### How do I use the Greenhouse job board API from Python?

Clone this repo, run `uv sync`, put your Apify token in `.env`, and run the example. The `rows()` helper shows the whole pattern: call the Actor, then iterate the dataset.

## Install in Claude Cowork Desktop

![Install in Claude Cowork Desktop](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_desktop.png)

Cowork is the desktop app's automation mode. To give it the Greenhouse Job Board API as a tool, add the Apify MCP server as a connector.

1. Open the Claude desktop app and go to **Settings → Connectors** (or **Settings → Developer → Edit Config** to edit `claude_desktop_config.json` directly).
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
2. Add the Apify MCP server, preloaded with only this Actor:

```json
{
  "mcpServers": {
    "apify": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.apify.com/?tools=actors,docs,johnvc/greenhouse-job-board-api"
      ]
    }
  }
}
```

3. Restart the app. When Cowork first calls the tool, complete the OAuth prompt in your browser, or add your Apify API token in the connector settings to skip OAuth.
4. In a Cowork chat, confirm the tool is available and ask it to run the Greenhouse Job Board API.

Download the desktop app and start a free trial: https://claude.ai/referral/uIlpa7nPLg
More help: https://docs.apify.com/platform/integrations/claude-desktop

---

## Install in Claude Code

![Install in Claude Code](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_code.png)

Claude Code is the command-line tool. Add the Actor's MCP server with one command:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/greenhouse-job-board-api"
```

To use a token instead of browser OAuth:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/greenhouse-job-board-api" \
  --header "Authorization: Bearer YOUR_APIFY_TOKEN"
```

Then verify with `claude mcp list`, or run `/mcp` inside a session. Ask Claude Code to call the Greenhouse Job Board API.

Try Claude Code free: https://claude.ai/referral/uIlpa7nPLg
Claude Code MCP docs: https://code.claude.com/docs/en/mcp

---

## Install in Claude (website)

![Install in Claude (website)](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_ai.png)

On claude.ai you add Apify as a connector, then enable just this Actor's tool.

1. Go to **Settings → Connectors → Browse connectors** and search for **Apify MCP server**. Install it (enable or update if prompted).
2. When connecting, authenticate with your Apify API token, and enable the tool `johnvc/greenhouse-job-board-api`.
3. In any chat, open **+ → Connectors** and turn on **Apify**.
4. Alternatively, choose **Add custom connector** and paste the full MCP URL `https://mcp.apify.com/?tools=actors,docs,johnvc/greenhouse-job-board-api`, using OAuth when prompted.
5. Ask Claude to run the Greenhouse Job Board API.

Open Claude on the web: https://claude.ai

---

## Install in Cursor

![Install in Cursor](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_cursor.png)

Cursor reads MCP servers from a project file at `.cursor/mcp.json`.

1. In your project, create `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/greenhouse-job-board-api"
    }
  }
}
```

2. If you prefer token auth over browser OAuth, add a header:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/greenhouse-job-board-api",
      "headers": { "Authorization": "Bearer YOUR_APIFY_TOKEN" }
    }
  }
}
```

3. Open **Cursor → Settings → MCP** and confirm the **apify** server is connected (green dot).
4. In Composer or Chat, ask Cursor to call the Greenhouse Job Board API.

New to Cursor? Get it here: https://cursor.com/referral?code=XQP4VBLI3NNX

---

## Install in ChatGPT

![Install in ChatGPT](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_ChatGPT.png)

ChatGPT connects to the Apify MCP server through Developer mode (available on ChatGPT Pro, Plus, Business, Enterprise, and Education plans).

1. Click your profile icon, then go to **Settings > Apps**. If you do not see a **Create app** button, open **Advanced settings** and enable **Developer mode**.
2. Click **Create app** and fill out the form:
   - **Name:** Apify
   - **MCP Server URL:** `https://mcp.apify.com/?tools=actors,docs,johnvc/greenhouse-job-board-api`
   - **Authentication:** OAuth
3. Click **Create** and authorize the connection with Apify.
4. To use the app in a conversation, click **+** in the chat, choose **Developer mode**, and select **Apify**.

More help: https://docs.apify.com/platform/integrations/mcp

---

Made with care by [johnvc on Apify](https://apify.com/johnvc?fpr=9n7kx3).

Last Updated: 2026.09.26
