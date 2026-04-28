# Design: drawio-aws skill

**Date:** 2026-04-28
**Status:** Approved

## Context

Creating AWS architecture diagrams in draw.io is a repetitive process. The user regularly brainstorms architectures with Claude and then asks the LLM to generate draw.io XML — but the results are inconsistent: wrong icons, messy layouts, random colors, and no naming conventions. This skill standardizes the entire generation process so every diagram looks the same regardless of session or model.

Scope: AWS cloud architectures, Claude-specific for now. Future iterations may add support for other cloud providers and LLMs.

## Intended outcome

A Claude Code skill (`drawio-aws`) that accepts a free-text AWS architecture description and outputs a `.drawio` XML file that is visually consistent, uses official AWS icons, and applies a fixed set of visual rules every time.

---

## Architecture: 2-step pipeline

```
[Free text] → (Claude – Step 1) → [Intermediate JSON] → (Python script) → [.drawio XML]
```

Claude handles semantics only. The Python script handles all visual rendering deterministically.

---

## Project structure

The repo is structured as a Claude Code installable plugin. Users add it via:
```
/plugin marketplace add <github-user>/skill-drawio
/plugin install drawio-aws@skill-drawio
```

```
skill-drawio/                         # GitHub repo root
├── README.md                         # Install instructions + usage guide
├── LICENSE
├── skills/
│   └── drawio-aws/                   # Installable skill folder
│       ├── SKILL.md                  # Main skill instructions (Claude)
│       ├── scripts/
│       │   └── generate_drawio.py    # JSON → .drawio XML converter
│       ├── references/
│       │   ├── aws-shapes.md         # Lookup table: service key → mxgraph.aws4.* shape IDs
│       │   └── json-schema.md        # Extended JSON schema with annotated examples
│       └── examples/
│           ├── serverless-api.json
│           └── three-tier-web.json
└── docs/
    └── superpowers/specs/
        └── 2026-04-28-drawio-aws-skill-design.md
```

---

## Step 1 — Claude produces intermediate JSON

Claude reads the text description and produces a JSON document with three sections: `nodes`, `edges`, and optional `groups`.

### JSON schema

```json
{
  "title": "my-aws-architecture",
  "nodes": [
    { "id": "api-gateway-main", "service": "api-gateway" },
    { "id": "lambda-get-user",  "service": "lambda" },
    { "id": "rds-postgres-db",  "service": "rds" }
  ],
  "edges": [
    { "from": "api-gateway-main", "to": "lambda-get-user" },
    { "from": "lambda-get-user",  "to": "rds-postgres-db" }
  ],
  "groups": [
    {
      "id": "vpc-main",
      "type": "vpc",
      "label": "vpc-main",
      "contains": ["lambda-get-user", "rds-postgres-db"]
    }
  ]
}
```

**Field rules:**
- `id` — kebab-case, descriptive (validated by script, error if not kebab)
- `service` — lowercase service key mapped via `aws-shapes.md`
- `edges.label` — optional; omitted means no label on arrow
- `groups.type` — `vpc`, `region`, `availability-zone`, or `generic`

---

## Step 2 — Script applies all visual rules

`generate_drawio.py` takes the JSON and produces a valid `.drawio` XML with these rules applied deterministically:

| Rule | Value |
|------|-------|
| Icon size | 50 × 50 px |
| Icon source | Official AWS stencil pack (`mxgraph.aws4.*`) |
| Arrow color | Black (`#000000`) |
| Arrow style | Orthogonal, no label unless specified |
| Layout direction | Left → Right |
| Node spacing | 80px gap between node edges (horizontal), 60px (vertical) |
| Title | Centered at top, font size 18, bold |
| Naming | Kebab-case enforced (error on violation) |
| VPC/Region groups | draw.io container with dashed border, AWS orange |
| File output | `<title>.drawio` in the same directory as the input JSON file |

---

## SKILL.md structure

Located at `skills/drawio-aws/SKILL.md`. Body stays under 300 lines for fast context loading. Content:

1. **Overview** — what the skill does, when to use it
2. **Workflow** — the 2-step process with diagram
3. **Step 1 instructions** — how Claude interprets the text → JSON (with compact schema inline)
4. **Step 2 instructions** — how to run `scripts/generate_drawio.py`
5. **Naming rules** — kebab-case guide with examples
6. **Reference pointer** — load `references/aws-shapes.md` only when a service shape ID is unknown

---

## Token efficiency strategy

- `SKILL.md` contains the full workflow and JSON schema inline (~250 lines max)
- `aws-shapes.md` is a large lookup table loaded **on demand** — Claude reads it only when it doesn't know a service's shape ID
- `json-schema.md` provides extended examples and edge cases, loaded only if needed
- The Python script runs locally, zero tokens
- No back-and-forth XML generation — one shot: text → JSON → run script → done

---

## aws-shapes.md reference table

Contains entries for ~60 most common AWS services at minimum:

| Service key | draw.io shape style |
|-------------|-------------------|
| `lambda` | `shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.lambda` |
| `api-gateway` | `shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.api_gateway` |
| `s3` | `shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.s3` |
| `rds` | `shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.rds` |
| ... | ... |

Full table to be populated during implementation by inspecting the imported stencil XML files.

---

## Examples included

Two bundled example JSON files cover the most common patterns:
- `serverless-api.json` — API Gateway → Lambda → DynamoDB/S3
- `three-tier-web.json` — ALB → EC2/ECS → RDS within a VPC with public/private subnets

---

## Verification plan

1. Run `generate_drawio.py` on both example JSON files → open output in draw.io desktop, confirm icons load correctly with the AWS stencil pack active
2. Describe a simple architecture in free text to Claude with the skill active → confirm JSON output is valid, kebab-case, correct services
3. Run the full pipeline end-to-end (text → JSON → script → .drawio) → open file, verify: title centered, arrows black, icons 50×50, layout left→right
4. Test a VPC grouping: confirm container renders with dashed border in draw.io
5. Test kebab-case enforcement: pass a non-kebab id → confirm script raises an error

---

## Future extensions (out of scope now)

- Support for other cloud providers (GCP, Azure)
- Support for other LLMs (GPT-4, Gemini) via agent-specific prompt variants
- Template library for common AWS patterns (event-driven, microservices)
- PNG export via draw.io CLI
