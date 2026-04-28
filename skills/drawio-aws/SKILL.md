---
name: drawio-aws
description: >
  Use this skill whenever the user wants to create, generate, or produce an AWS
  architecture diagram in draw.io format. Trigger on phrases like "crea un drawio",
  "genera il diagramma", "draw this architecture", "make a draw.io for my AWS setup",
  or any description of AWS services that implies a diagram should be produced.
  Use even if the user doesn't say "draw.io" explicitly — if they describe an AWS
  architecture and want a diagram, this skill applies.
---

# drawio-aws

Generate visually consistent AWS architecture diagrams as `.drawio` files from a
free-text description. Uses official AWS icons (mxgraph.aws4 stencil pack).

**Prerequisites:** Python 3.9+, draw.io desktop with the
[official AWS icon pack](https://aws.amazon.com/architecture/icons/) installed.

## Visual rules (enforced by script)

| Rule | Value |
|------|-------|
| Icon size | 50 × 50 px |
| Icon set | Official AWS stencil pack (mxgraph.aws4.*) |
| Arrow color | Black (#000000), orthogonal |
| Layout | Left → Right |
| Title | Centered at top, 18px bold |
| Naming | kebab-case enforced (error on violation) |
| Groups | VPC / Region / AZ as draw.io containers |

## Workflow

```
User text → Step 1: produce JSON → save as <title>.json
           → Step 2: run script  → produces <title>.drawio
```

## Step 1 — Produce intermediate JSON

Read the user's architecture description and produce the following JSON.
Save it as `<title>.json` in the user's working directory.

**Naming rules:**
- `title` and all `id` fields must be **kebab-case**: `lambda-get-user` ✅ `LambdaFn` ❌
- Node ids must be descriptive: `rds-postgres-db` not just `rds`
- If unsure of a service key, read `references/aws-shapes.md`

```json
{
  "title": "my-aws-architecture",
  "nodes": [
    { "id": "api-gateway-main",  "service": "api-gateway" },
    { "id": "lambda-get-user",   "service": "lambda" },
    { "id": "rds-postgres-db",   "service": "rds" }
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

`groups` is optional. `edges[].label` is optional (omit for unlabelled arrows).
`groups[].type` must be one of: `vpc`, `region`, `availability-zone`, `generic`.

## Step 2 — Run the script

```bash
python /path/to/skills/drawio-aws/scripts/generate_drawio.py <title>.json
```

The script outputs `<title>.drawio` in the same directory as the input JSON.

Tell the user the output path when done.

## Service keys

Most common services (full list in `references/aws-shapes.md`):

`lambda` `api-gateway` `s3` `rds` `dynamodb` `ec2` `ecs` `eks` `fargate`
`cloudfront` `route53` `alb` `nlb` `waf` `cognito` `iam` `secrets-manager`
`sqs` `sns` `eventbridge` `step-functions` `kinesis` `cloudwatch` `elasticache`
