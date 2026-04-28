# drawio-aws

A Claude Code skill for generating consistent AWS architecture diagrams in draw.io format.

Describe your AWS architecture in plain text — Claude converts it to a `.drawio` file
with official AWS icons, consistent layout, and enforced visual rules.

## Requirements

- Python 3.9+ (stdlib only, no pip install needed)
- draw.io desktop with the [official AWS icon pack](https://aws.amazon.com/architecture/icons/) imported

## Installation in Claude Code

```bash
/plugin marketplace add <your-github-user>/skill-drawio
/plugin install drawio-aws@skill-drawio
```

## Usage

Just describe your architecture to Claude:

> "Crea un draw.io per un'architettura serverless: API Gateway → due Lambda
> (get-user e post-order) → DynamoDB. Metti le Lambda in un VPC."

Claude will:
1. Parse the description into a structured JSON
2. Run `generate_drawio.py` to produce a `.drawio` file
3. Tell you the output path

## Visual rules enforced

| Rule | Value |
|------|-------|
| Icons | Official AWS stencil pack (mxgraph.aws4.*), 50 × 50 px |
| Arrows | Black (#000000), orthogonal routing |
| Layout | Left → Right, auto-spaced |
| Names | kebab-case (validated, error on violation) |
| Title | Centered at top, 18px bold |
| Groups | VPC / Region / AZ as draw.io containers |

## Run the script directly

```bash
python skills/drawio-aws/scripts/generate_drawio.py my-architecture.json
# Output: my-architecture.drawio
```

## Run tests

```bash
python3 -m pytest tests/ -v
```

## Supported AWS services

See [`skills/drawio-aws/references/aws-shapes.md`](skills/drawio-aws/references/aws-shapes.md)
for the full list of supported service keys (33 services across Compute, Networking,
Storage, Database, Security, Integration, and DevTools categories).
