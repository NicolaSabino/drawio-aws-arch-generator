# Intermediate JSON Schema

## Root object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | yes | kebab-case name; used as output filename |
| `nodes` | Node[] | yes | AWS services in the diagram |
| `edges` | Edge[] | yes | Connections between nodes |
| `groups` | Group[] | no | VPC / region / AZ containers |

## Node

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | kebab-case, unique, descriptive (e.g. `lambda-get-user`) |
| `service` | string | yes | Service key from aws-shapes.md (e.g. `lambda`) |

## Edge

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `from` | string | yes | Source node id |
| `to` | string | yes | Target node id |
| `label` | string | no | Arrow label (omit for unlabelled) |

## Group

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | kebab-case, unique |
| `type` | string | yes | `vpc` \| `region` \| `availability-zone` \| `generic` |
| `label` | string | yes | Display label (kebab-case) |
| `contains` | string[] | yes | List of node ids inside this group |

## Naming rules

- All `id` fields: kebab-case only — `lambda-get-user` ✅, `getLambda` ❌
- Descriptive: include purpose — `rds-postgres-db` instead of just `rds`
- No spaces, no underscores, no camelCase

## Full example with groups

```json
{
  "title": "serverless-api",
  "nodes": [
    { "id": "route53-main",      "service": "route53" },
    { "id": "cloudfront-cdn",    "service": "cloudfront" },
    { "id": "api-gateway-main",  "service": "api-gateway" },
    { "id": "lambda-get-user",   "service": "lambda" },
    { "id": "lambda-post-order", "service": "lambda" },
    { "id": "dynamodb-users",    "service": "dynamodb" },
    { "id": "s3-file-storage",   "service": "s3" }
  ],
  "edges": [
    { "from": "route53-main",     "to": "cloudfront-cdn" },
    { "from": "cloudfront-cdn",   "to": "api-gateway-main" },
    { "from": "api-gateway-main", "to": "lambda-get-user" },
    { "from": "api-gateway-main", "to": "lambda-post-order" },
    { "from": "lambda-get-user",  "to": "dynamodb-users" },
    { "from": "lambda-post-order","to": "s3-file-storage" }
  ],
  "groups": [
    {
      "id": "vpc-main",
      "type": "vpc",
      "label": "vpc-main",
      "contains": ["lambda-get-user", "lambda-post-order", "dynamodb-users"]
    }
  ]
}
```
