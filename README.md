# drawio-aws

A Claude Code skill for generating consistent AWS architecture diagrams in draw.io format.

## Requirements

- Python 3.9+
- draw.io desktop with the [official AWS icon pack](https://aws.amazon.com/architecture/icons/) installed

## Installation

Add this repo as a Claude Code plugin:

```
/plugin marketplace add <your-github-user>/skill-drawio
/plugin install drawio-aws@skill-drawio
```

## Usage

Describe your AWS architecture to Claude and it will:
1. Parse it into a structured JSON
2. Run `generate_drawio.py` to produce a `.drawio` file

## Visual rules enforced

- All icons: 50×50 px (official AWS stencil pack)
- All arrows: black, orthogonal
- Layout: left → right
- Naming: kebab-case enforced
- Title: centered at top
- VPC/Region/AZ: draw.io containers with AWS-style borders
