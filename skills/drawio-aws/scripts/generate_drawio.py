"""
generate_drawio.py — Converts intermediate JSON to draw.io XML.

Usage:
    python generate_drawio.py <input.json>

Output:
    <title>.drawio in the same directory as input.json
"""

import json
import re
import sys
import argparse
from dataclasses import dataclass, field
from pathlib import Path
import xml.etree.ElementTree as ET


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Node:
    id: str
    service: str


@dataclass
class Edge:
    from_id: str
    to_id: str
    label: str = ""


@dataclass
class Group:
    id: str
    type: str      # vpc | region | availability-zone | generic
    label: str
    contains: list  # list of node ids


@dataclass
class Architecture:
    title: str
    nodes: list   # list[Node]
    edges: list   # list[Edge]
    groups: list  # list[Group]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

KEBAB_RE = re.compile(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$')


def validate_kebab_case(s: str) -> bool:
    """Return True if s is valid kebab-case (lowercase, hyphens only)."""
    return bool(KEBAB_RE.match(s))


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_architecture(data: dict) -> Architecture:
    """Parse raw JSON dict into Architecture. Raises ValueError on violations."""
    title = data.get("title", "")
    if not validate_kebab_case(title):
        raise ValueError(f"title '{title}' must be kebab-case (e.g. 'my-aws-architecture')")

    nodes = []
    for n in data.get("nodes", []):
        nid = n["id"]
        if not validate_kebab_case(nid):
            raise ValueError(f"node id '{nid}' must be kebab-case (e.g. 'lambda-get-user')")
        nodes.append(Node(id=nid, service=n["service"]))

    edges = []
    for e in data.get("edges", []):
        edges.append(Edge(
            from_id=e["from"],
            to_id=e["to"],
            label=e.get("label", "")
        ))

    groups = []
    for g in data.get("groups", []):
        gid = g["id"]
        if not validate_kebab_case(gid):
            raise ValueError(f"group id '{gid}' must be kebab-case")
        groups.append(Group(
            id=gid,
            type=g["type"],
            label=g["label"],
            contains=g.get("contains", [])
        ))

    return Architecture(title=title, nodes=nodes, edges=edges, groups=groups)


# ---------------------------------------------------------------------------
# Shape lookup
# ---------------------------------------------------------------------------

# (service_key) -> (resIcon, fillColor)
SHAPES = {
    "lambda":          ("mxgraph.aws4.lambda",                    "#ED7100"),  # Compute
    "api-gateway":     ("mxgraph.aws4.api_gateway",               "#E7157B"),
    "s3":              ("mxgraph.aws4.s3",                        "#3F8624"),
    "rds":             ("mxgraph.aws4.rds",                       "#C7131F"),
    "dynamodb":        ("mxgraph.aws4.dynamodb",                  "#C7131F"),
    "elasticache":     ("mxgraph.aws4.elasticache",               "#C7131F"),
    "opensearch":      ("mxgraph.aws4.opensearch_service",        "#0050D1"),
    "ec2":             ("mxgraph.aws4.ec2",                       "#ED7100"),
    "ecs":             ("mxgraph.aws4.ecs",                       "#ED7100"),
    "eks":             ("mxgraph.aws4.eks",                       "#ED7100"),
    "fargate":         ("mxgraph.aws4.fargate",                   "#ED7100"),
    "ecr":             ("mxgraph.aws4.ecr",                       "#ED7100"),
    "cloudfront":      ("mxgraph.aws4.cloudfront",                "#8C4FFF"),
    "route53":         ("mxgraph.aws4.route_53",                  "#8C4FFF"),
    "alb":             ("mxgraph.aws4.application_load_balancer", "#8C4FFF"),
    "nlb":             ("mxgraph.aws4.network_load_balancer",     "#8C4FFF"),
    "waf":             ("mxgraph.aws4.waf",                       "#DD344C"),
    "cognito":         ("mxgraph.aws4.cognito",                   "#DD344C"),
    "iam":             ("mxgraph.aws4.iam",                       "#DD344C"),
    "secrets-manager": ("mxgraph.aws4.secrets_manager",          "#DD344C"),
    "kms":             ("mxgraph.aws4.key_management_service",    "#DD344C"),
    "sqs":             ("mxgraph.aws4.sqs",                       "#E7157B"),
    "sns":             ("mxgraph.aws4.sns",                       "#E7157B"),
    "eventbridge":     ("mxgraph.aws4.eventbridge",               "#E7157B"),
    "step-functions":  ("mxgraph.aws4.step_functions",            "#E7157B"),
    "kinesis":         ("mxgraph.aws4.kinesis_data_streams",      "#8C4FFF"),  # Analytics
    "cloudwatch":      ("mxgraph.aws4.cloudwatch",                "#E7157B"),
    "cloudtrail":      ("mxgraph.aws4.cloudtrail",                "#E7157B"),
    "codepipeline":    ("mxgraph.aws4.codepipeline",              "#ED7100"),
    "codebuild":       ("mxgraph.aws4.codebuild",                 "#ED7100"),
    "codedeploy":      ("mxgraph.aws4.codedeploy",                "#ED7100"),
    "glue":            ("mxgraph.aws4.glue",                      "#8C4FFF"),
    "athena":          ("mxgraph.aws4.athena",                    "#8C4FFF"),  # Analytics
    "connect":         ("mxgraph.aws4.connect",                   "#E7157B"),
}

_NODE_STYLE_TEMPLATE = (
    "outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=none;"
    "fillColor={fill};labelBackgroundColor=#ffffff;align=center;html=1;"
    "fontSize=12;fontStyle=0;aspect=fixed;"
    "verticalLabelPosition=bottom;verticalAlign=top;"
    "shape=mxgraph.aws4.resourceIcon;resIcon={res};"
)


def get_node_style(service: str) -> str:
    """Return the draw.io style string for a given service key."""
    res, fill = SHAPES.get(service, ("mxgraph.aws4.general", "#232F3E"))
    return _NODE_STYLE_TEMPLATE.format(fill=fill, res=res)


# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------

ICON_SIZE = 50
H_GAP = 140    # horizontal gap between node edges
V_GAP = 100    # vertical gap between node edges
H_STEP = ICON_SIZE + H_GAP   # 190 px per column
V_STEP = ICON_SIZE + V_GAP   # 150 px per row
PADDING_LEFT = 100
PADDING_TOP = 180   # reserved for title (title ends at ~y=70; groups top = PADDING_TOP-55)


# ---------------------------------------------------------------------------
# Layout engine
# ---------------------------------------------------------------------------

def compute_layout(nodes, edges):
    """
    Returns {node_id: (x, y)} using left-to-right topological layout.

    Nodes with no incoming edges start at column 0. Each hop right
    is one column. Nodes in the same column are stacked vertically.
    """
    node_ids = [n.id for n in nodes]
    successors = {nid: [] for nid in node_ids}
    in_degree = {nid: 0 for nid in node_ids}

    for edge in edges:
        if edge.from_id in successors and edge.to_id in in_degree:
            successors[edge.from_id].append(edge.to_id)
            in_degree[edge.to_id] += 1

    # BFS column assignment
    queue = [nid for nid in node_ids if in_degree[nid] == 0]
    col = {nid: 0 for nid in queue}
    visited = set(queue)

    while queue:
        nid = queue.pop(0)
        for succ in successors.get(nid, []):
            if succ not in visited:
                col[succ] = max(col.get(succ, 0), col[nid] + 1)
                visited.add(succ)
                queue.append(succ)
            # Back-edges (cycles) are skipped: already-visited nodes
            # keep their column from the forward traversal.

    # Assign any isolated nodes (no edges) to column 0
    for nid in node_ids:
        if nid not in col:
            col[nid] = 0

    # Assign rows within each column (insertion order preserves declaration order)
    col_row_count: dict = {}
    positions = {}
    for nid in node_ids:
        c = col[nid]
        r = col_row_count.get(c, 0)
        col_row_count[c] = r + 1
        positions[nid] = (PADDING_LEFT + c * H_STEP, PADDING_TOP + r * V_STEP)

    return positions


# ---------------------------------------------------------------------------
# XML generation
# ---------------------------------------------------------------------------

PAGE_WIDTH = 1169
PAGE_HEIGHT = 827

_EDGE_STYLE = (
    "edgeStyle=orthogonalEdgeStyle;html=1;strokeColor=#000000;"
)

_GROUP_STYLES = {
    "vpc": (
        "points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],"
        "[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];"
        "shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_vpc;"
        "strokeColor=#8C4FFF;fillColor=#F4F0FA;verticalLabelPosition=top;"
        "verticalAlign=bottom;align=center;spacingTop=25;fontColor=#8C4FFF;dashed=0;"
    ),
    "region": (
        "points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],"
        "[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];"
        "shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_region;"
        "strokeColor=#147EBA;fillColor=#E6F2F8;verticalLabelPosition=top;"
        "verticalAlign=bottom;align=center;spacingTop=25;fontColor=#147EBA;dashed=1;"
    ),
    "availability-zone": (
        "shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_availability_zone;"
        "strokeColor=#147EBA;fillColor=none;verticalLabelPosition=top;"
        "verticalAlign=bottom;align=center;spacingTop=25;fontColor=#147EBA;dashed=1;"
    ),
    "generic": (
        "strokeColor=#666666;fillColor=#f5f5f5;verticalLabelPosition=top;"
        "verticalAlign=bottom;align=center;spacingTop=25;fontColor=#333333;dashed=1;rounded=1;"
    ),
}

_GROUP_PADDING = 30   # padding inside group container around nodes
_LABEL_HEIGHT = 25   # height of label rendered below the icon


def _group_bounds(contains, positions):
    """Return (x, y, w, h) that wraps all nodes in a group."""
    xs = [positions[nid][0] for nid in contains if nid in positions]
    ys = [positions[nid][1] for nid in contains if nid in positions]
    if not xs:
        return (PADDING_LEFT, PADDING_TOP, 200, 150)
    x = min(xs) - _GROUP_PADDING
    y = min(ys) - _GROUP_PADDING - 25   # extra space for label at top
    w = max(xs) - min(xs) + ICON_SIZE + _GROUP_PADDING * 2
    h = max(ys) - min(ys) + ICON_SIZE + _LABEL_HEIGHT + _GROUP_PADDING * 2 + 25
    return (x, y, w, h)


def generate_xml(arch: Architecture, positions: dict) -> str:
    """Generate draw.io XML string from Architecture and computed positions."""

    # Determine which nodes are in a group (for parent assignment)
    node_parent = {}  # node_id -> group_id or "1"
    for group in arch.groups:
        for nid in group.contains:
            node_parent[nid] = group.id

    root_el = ET.Element("mxGraphModel", {
        "dx": "1422", "dy": "762", "grid": "1", "gridSize": "10",
        "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1",
        "fold": "1", "page": "1", "pageScale": "1",
        "pageWidth": str(PAGE_WIDTH), "pageHeight": str(PAGE_HEIGHT),
        "math": "0", "shadow": "0"
    })
    root_inner = ET.SubElement(root_el, "root")
    ET.SubElement(root_inner, "mxCell", {"id": "0"})
    ET.SubElement(root_inner, "mxCell", {"id": "1", "parent": "0"})

    # Title cell — centered at top
    title_cell = ET.SubElement(root_inner, "mxCell", {
        "id": "title",
        "value": arch.title,
        "style": (
            "text;html=1;strokeColor=none;fillColor=none;"
            "align=center;verticalAlign=middle;whiteSpace=wrap;"
            "rounded=0;fontSize=18;fontStyle=1;"
        ),
        "vertex": "1",
        "parent": "1"
    })
    ET.SubElement(title_cell, "mxGeometry", {
        "x": "0", "y": "20",
        "width": str(PAGE_WIDTH), "height": "50",
        "as": "geometry"
    })

    # Group containers (must be added before their child nodes)
    for group in arch.groups:
        gx, gy, gw, gh = _group_bounds(group.contains, positions)
        style = _GROUP_STYLES.get(group.type, _GROUP_STYLES["generic"])
        g_cell = ET.SubElement(root_inner, "mxCell", {
            "id": group.id,
            "value": group.label,
            "style": style,
            "vertex": "1",
            "parent": "1"
        })
        ET.SubElement(g_cell, "mxGeometry", {
            "x": str(gx), "y": str(gy),
            "width": str(gw), "height": str(gh),
            "as": "geometry"
        })

    # Node cells
    for node in arch.nodes:
        x, y = positions[node.id]
        parent_id = node_parent.get(node.id, "1")

        # If node is inside a group, coordinates are relative to group
        if parent_id != "1":
            gx, gy, _, _ = _group_bounds(
                [nid for g in arch.groups if g.id == parent_id for nid in g.contains],
                positions
            )
            x = x - gx
            y = y - gy

        n_cell = ET.SubElement(root_inner, "mxCell", {
            "id": node.id,
            "value": node.id,
            "style": get_node_style(node.service),
            "vertex": "1",
            "parent": parent_id
        })
        ET.SubElement(n_cell, "mxGeometry", {
            "x": str(x), "y": str(y),
            "width": "50", "height": "50",
            "as": "geometry"
        })

    # Edge cells
    for edge in arch.edges:
        edge_id = f"edge_{edge.from_id}_{edge.to_id}"
        e_cell = ET.SubElement(root_inner, "mxCell", {
            "id": edge_id,
            "value": edge.label,
            "style": _EDGE_STYLE,
            "edge": "1",
            "source": edge.from_id,
            "target": edge.to_id,
            "parent": "1"
        })
        ET.SubElement(e_cell, "mxGeometry", {"relative": "1", "as": "geometry"})

    ET.indent(root_el, space="  ")
    return ET.tostring(root_el, encoding="unicode", xml_declaration=False)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Convert intermediate JSON to draw.io XML with AWS icons."
    )
    parser.add_argument("input", help="Path to the input .json file")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(input_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        arch = parse_architecture(data)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    positions = compute_layout(arch.nodes, arch.edges)
    xml_str = generate_xml(arch, positions)

    output_path = input_path.parent / f"{arch.title}.drawio"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_str)

    print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()
