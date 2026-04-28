import sys
import os
import json
import pytest

# Make the script importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'skills', 'drawio-aws', 'scripts'))
import generate_drawio as gd


# --- validate_kebab_case ---

def test_valid_kebab_cases():
    assert gd.validate_kebab_case("lambda-get-user") is True
    assert gd.validate_kebab_case("api-gateway-main") is True
    assert gd.validate_kebab_case("rds-postgres-db") is True
    assert gd.validate_kebab_case("s3") is True

def test_invalid_kebab_cases():
    assert gd.validate_kebab_case("getLambda") is False
    assert gd.validate_kebab_case("APIGateway") is False
    assert gd.validate_kebab_case("rds_postgres") is False
    assert gd.validate_kebab_case("RDS") is False
    assert gd.validate_kebab_case("") is False


# --- parse_architecture ---

MINIMAL_JSON = {
    "title": "my-arch",
    "nodes": [
        {"id": "lambda-fn", "service": "lambda"}
    ],
    "edges": [],
    "groups": []
}

def test_parse_minimal_architecture():
    arch = gd.parse_architecture(MINIMAL_JSON)
    assert arch.title == "my-arch"
    assert len(arch.nodes) == 1
    assert arch.nodes[0].id == "lambda-fn"
    assert arch.nodes[0].service == "lambda"
    assert arch.edges == []
    assert arch.groups == []

def test_parse_architecture_with_edge():
    data = {
        "title": "test-arch",
        "nodes": [
            {"id": "api-gw", "service": "api-gateway"},
            {"id": "lambda-fn", "service": "lambda"}
        ],
        "edges": [{"from": "api-gw", "to": "lambda-fn"}],
        "groups": []
    }
    arch = gd.parse_architecture(data)
    assert len(arch.edges) == 1
    assert arch.edges[0].from_id == "api-gw"
    assert arch.edges[0].to_id == "lambda-fn"
    assert arch.edges[0].label == ""

def test_parse_architecture_with_group():
    data = {
        "title": "test-arch",
        "nodes": [{"id": "lambda-fn", "service": "lambda"}],
        "edges": [],
        "groups": [{"id": "vpc-main", "type": "vpc", "label": "vpc-main", "contains": ["lambda-fn"]}]
    }
    arch = gd.parse_architecture(data)
    assert len(arch.groups) == 1
    assert arch.groups[0].id == "vpc-main"
    assert arch.groups[0].type == "vpc"
    assert arch.groups[0].contains == ["lambda-fn"]

def test_parse_rejects_non_kebab_node_id():
    data = {
        "title": "test-arch",
        "nodes": [{"id": "LambdaFn", "service": "lambda"}],
        "edges": [],
        "groups": []
    }
    with pytest.raises(ValueError, match="kebab-case"):
        gd.parse_architecture(data)

def test_parse_rejects_non_kebab_title():
    data = {
        "title": "MyArch",
        "nodes": [],
        "edges": [],
        "groups": []
    }
    with pytest.raises(ValueError, match="kebab-case"):
        gd.parse_architecture(data)


# --- get_node_style ---

def test_known_service_returns_style():
    style = gd.get_node_style("lambda")
    assert "mxgraph.aws4.lambda" in style
    assert "shape=mxgraph.aws4.resourceIcon" in style
    assert "aspect=fixed" in style

def test_known_service_api_gateway():
    style = gd.get_node_style("api-gateway")
    assert "mxgraph.aws4.api_gateway" in style

def test_known_service_s3():
    style = gd.get_node_style("s3")
    assert "mxgraph.aws4.s3" in style

def test_unknown_service_returns_generic_style():
    style = gd.get_node_style("some-unknown-service")
    assert "shape=mxgraph.aws4.resourceIcon" in style
    assert "mxgraph.aws4.general" in style


# --- compute_layout ---

def test_single_node_placed_at_origin():
    nodes = [gd.Node(id="lambda-fn", service="lambda")]
    edges = []
    positions = gd.compute_layout(nodes, edges)
    x, y = positions["lambda-fn"]
    assert x == gd.PADDING_LEFT
    assert y == gd.PADDING_TOP

def test_linear_chain_left_to_right():
    nodes = [
        gd.Node(id="a", service="lambda"),
        gd.Node(id="b", service="lambda"),
        gd.Node(id="c", service="lambda"),
    ]
    edges = [
        gd.Edge(from_id="a", to_id="b"),
        gd.Edge(from_id="b", to_id="c"),
    ]
    positions = gd.compute_layout(nodes, edges)
    ax, _ = positions["a"]
    bx, _ = positions["b"]
    cx, _ = positions["c"]
    assert ax < bx < cx, "Nodes should be ordered left to right"

def test_parallel_nodes_same_column_stacked_vertically():
    nodes = [
        gd.Node(id="gateway", service="api-gateway"),
        gd.Node(id="lambda-a", service="lambda"),
        gd.Node(id="lambda-b", service="lambda"),
    ]
    edges = [
        gd.Edge(from_id="gateway", to_id="lambda-a"),
        gd.Edge(from_id="gateway", to_id="lambda-b"),
    ]
    positions = gd.compute_layout(nodes, edges)
    ax, ay = positions["lambda-a"]
    bx, by = positions["lambda-b"]
    assert ax == bx, "Parallel nodes should be in the same column"
    assert ay != by, "Parallel nodes should be stacked vertically"

def test_isolated_node_placed_in_first_column():
    nodes = [gd.Node(id="isolated", service="s3")]
    edges = []
    positions = gd.compute_layout(nodes, edges)
    assert "isolated" in positions


# --- generate_xml ---

import xml.etree.ElementTree as ET

def _parse_xml(xml_str):
    return ET.fromstring(xml_str)

def test_xml_has_mxgraphmodel_root():
    arch = gd.parse_architecture(MINIMAL_JSON)
    positions = gd.compute_layout(arch.nodes, arch.edges)
    xml = gd.generate_xml(arch, positions)
    root = _parse_xml(xml)
    assert root.tag == "mxGraphModel"

def test_xml_has_title_cell():
    arch = gd.parse_architecture(MINIMAL_JSON)
    positions = gd.compute_layout(arch.nodes, arch.edges)
    xml = gd.generate_xml(arch, positions)
    root = _parse_xml(xml)
    cells = root.findall(".//mxCell[@id='title']")
    assert len(cells) == 1
    assert cells[0].get("value") == "my-arch"

def test_xml_node_has_correct_size():
    arch = gd.parse_architecture(MINIMAL_JSON)
    positions = gd.compute_layout(arch.nodes, arch.edges)
    xml = gd.generate_xml(arch, positions)
    root = _parse_xml(xml)
    cell = root.find(".//mxCell[@id='lambda-fn']")
    assert cell is not None
    geo = cell.find("mxGeometry")
    assert geo.get("width") == "50"
    assert geo.get("height") == "50"

def test_xml_node_has_aws_shape_style():
    arch = gd.parse_architecture(MINIMAL_JSON)
    positions = gd.compute_layout(arch.nodes, arch.edges)
    xml = gd.generate_xml(arch, positions)
    root = _parse_xml(xml)
    cell = root.find(".//mxCell[@id='lambda-fn']")
    style = cell.get("style", "")
    assert "mxgraph.aws4.lambda" in style

def test_xml_edge_has_black_stroke():
    data = {
        "title": "test-arch",
        "nodes": [
            {"id": "a", "service": "lambda"},
            {"id": "b", "service": "s3"}
        ],
        "edges": [{"from": "a", "to": "b"}],
        "groups": []
    }
    arch = gd.parse_architecture(data)
    positions = gd.compute_layout(arch.nodes, arch.edges)
    xml = gd.generate_xml(arch, positions)
    root = _parse_xml(xml)
    edges = root.findall(".//mxCell[@edge='1']")
    assert len(edges) == 1
    assert "#000000" in edges[0].get("style", "")

def test_xml_node_value_is_kebab_id():
    arch = gd.parse_architecture(MINIMAL_JSON)
    positions = gd.compute_layout(arch.nodes, arch.edges)
    xml = gd.generate_xml(arch, positions)
    root = _parse_xml(xml)
    cell = root.find(".//mxCell[@id='lambda-fn']")
    assert cell.get("value") == "lambda-fn"


# --- CLI / end-to-end ---

import subprocess
import tempfile
import shutil

def test_cli_generates_drawio_file():
    """Run the script on serverless-api.json, verify output file is created."""
    script = os.path.join(
        os.path.dirname(__file__), '..', 'skills', 'drawio-aws', 'scripts', 'generate_drawio.py'
    )
    example = os.path.join(
        os.path.dirname(__file__), '..', 'skills', 'drawio-aws', 'examples', 'serverless-api.json'
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "serverless-api.json")
        shutil.copy(example, input_path)
        result = subprocess.run(
            [sys.executable, script, input_path],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        output_path = os.path.join(tmpdir, "serverless-api.drawio")
        assert os.path.exists(output_path), "Output .drawio file not found"
        content = open(output_path).read()
        assert "<mxGraphModel" in content
        assert "serverless-api" in content

def test_cli_rejects_invalid_json():
    script = os.path.join(
        os.path.dirname(__file__), '..', 'skills', 'drawio-aws', 'scripts', 'generate_drawio.py'
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        bad_json = os.path.join(tmpdir, "bad.json")
        with open(bad_json, "w") as f:
            json.dump({
                "title": "BadTitle",
                "nodes": [],
                "edges": [],
                "groups": []
            }, f)
        result = subprocess.run(
            [sys.executable, script, bad_json],
            capture_output=True, text=True
        )
        assert result.returncode != 0
        assert "kebab-case" in result.stderr
