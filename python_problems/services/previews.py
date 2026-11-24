import binarytree
from python_problems.models import ProblemType


def is_grid_shape(data):
    if not data:
        return

    for row in data:
        if not row or not isinstance(row, list):
            return
        if len(row) != len(data[0]):
            return

    return True


def draw_grid(data, parameter_name, parameter_type):
    if not is_grid_shape(data):
        return

    rows = len(data)
    cols = len(data[0])
    chars = {str(char) for line in data for char in line}
    char_map = {}

    # if all(char.isalpha() for char in chars):
    #     return

    match len(chars):
        case 1 | 2 | 3:
            char_map = {
                '-1': '█',
                '0': '·',
                '1': '■',
                '2': 'X',
                "2147483647": '∞',
                "-2147483648": '-∞',
                "9223372036854775807": '∞',
                "9223372036854775808": '-∞',
                'O': 'O',
                'X': 'X'
            }
        case _:
            char_map = {char: char for char in chars}
            char_map['-1'] = '█'

    grid = ""
    max_col_lens = [0] * cols

    for col in range(cols):
        for row in range(rows):
            max_col_lens[col] = max(
                max_col_lens[col], len(str(data[row][col])))

    for row in range(rows):
        grid_line = "│ "

        for col in range(cols):
            val = data[row][col]
            str_val = char_map.get(str(val), "J")
            val_len = len(str_val)
            grid_line += str_val + " " * (max_col_lens[col] - val_len) + " "

        grid_line = grid_line + "│\n"
        grid = grid + grid_line

    grid = """┌""" + '─' * (sum(max_col_lens) + cols + 1) + "┐\n" + grid
    grid = grid + """└""" + '─' * (sum(max_col_lens) + cols + 1) + '┘'

    return (parameter_name, grid)


def draw_tree(data, parameter_name):
    bt = binarytree.build2(data).__str__()
    parameter_name = parameter_name or "root"
    return (parameter_name, bt)


def unpack_linked_list_payload(data):
    if not isinstance(data, dict):
        return data, -1

    values = None
    for key in ("values", "nodes", "list"):
        if key in data:
            values = data[key]
            break

    cycle_position = -1
    for key in ("cycle_position", "cyclePosition", "pos"):
        if key in data:
            cycle_position = data[key]
            break

    if values is None:
        return data, -1

    if not isinstance(cycle_position, int):
        cycle_position = -1

    return values, cycle_position


def draw_linked_list(data, parameter_name):
    values, cycle_position = unpack_linked_list_payload(data)

    if not isinstance(values, list):
        preview = str(data)
        return (parameter_name, preview)

    preview = ("(" + ") -> (".join(map(str, values)) + ")") if values else "null"

    if 0 <= cycle_position < len(values):
        preview += f" -> ↺ index {cycle_position} ({values[cycle_position]})"

    return (parameter_name, preview)


def draw_list(heights, parameter_name):
    if not heights:
        return ""

    max_height = max(heights)

    if max_height > 1000:
        return ""

    fill = "█"
    lines = []

    for level in range(max_height, 0, -1):
        row = f"{level:>2} │ "

        for h in heights:
            if h >= level:
                row += f"{fill} "
            else:
                row += "  "

        lines.append(row.rstrip())

    axis = "   +" + '-' * (2 * len(heights) + 1)
    indexes = "     " + " ".join(str(i) for i in range(len(heights)))

    lines.append(axis)
    lines.append(indexes)

    return (parameter_name, "\n".join(lines))


def _parse_edge_list(data, directed, vertex_count):
    if not isinstance(data, list):
        return

    if vertex_count is not None:
        if type(vertex_count) is not int or vertex_count < 0:
            return
        vertices = set(range(vertex_count))
    else:
        vertices = set()

    edges = set()
    for edge in data:
        if (
            not isinstance(edge, list)
            or len(edge) != 2
            or type(edge[0]) is not int
            or type(edge[1]) is not int
        ):
            return

        start, end = edge
        if vertex_count is not None and (
            start < 0 or end < 0 or start >= vertex_count or end >= vertex_count
        ):
            return

        vertices.update((start, end))
        edges.add((start, end) if directed else tuple(sorted((start, end))))

    return vertices, edges


def _parse_adjacency_matrix(data, directed):
    if not isinstance(data, list) or any(not isinstance(row, list) for row in data):
        return

    size = len(data)
    if any(len(row) != size for row in data):
        return

    for row in data:
        for cell in row:
            if type(cell) is not int and type(cell) is not bool:
                return
            if cell not in (0, 1, False, True):
                return

    if not directed:
        for row in range(size):
            for col in range(row + 1, size):
                if bool(data[row][col]) != bool(data[col][row]):
                    return

    edges = set()
    for row in range(size):
        for col in range(size):
            if not data[row][col]:
                continue
            edges.add((row, col) if directed else tuple(sorted((row, col))))

    return set(range(size)), edges


def _graph_components(vertices, edges):
    neighbours = {vertex: set() for vertex in vertices}
    for start, end in edges:
        if start != end:
            neighbours[start].add(end)
            neighbours[end].add(start)

    components = []
    remaining = set(vertices)
    while remaining:
        root = min(remaining)
        stack = [root]
        component = set()
        while stack:
            vertex = stack.pop()
            if vertex in component:
                continue
            component.add(vertex)
            stack.extend(neighbours[vertex] - component)
        remaining -= component
        components.append(component)

    return components, neighbours


def _draw_graph_component(component, neighbours, edges, directed):
    component_edges = {
        edge for edge in edges
        if edge[0] in component and edge[1] in component
    }
    root = min(component)
    parent = {root: None}
    traversal = [root]
    tree_edges = set()

    for vertex in traversal:
        for neighbour in sorted(neighbours[vertex]):
            if neighbour in parent:
                continue
            parent[neighbour] = vertex
            traversal.append(neighbour)
            if directed:
                tree_edges.add(
                    (vertex, neighbour)
                    if (vertex, neighbour) in component_edges
                    else (neighbour, vertex)
                )
            else:
                tree_edges.add(tuple(sorted((vertex, neighbour))))

    children = {vertex: [] for vertex in component}
    for vertex, parent_vertex in parent.items():
        if parent_vertex is not None:
            children[parent_vertex].append(vertex)

    lines = [f"({root})"]

    def connector(parent_vertex, child):
        if not directed:
            return "── "
        if (parent_vertex, child) in component_edges:
            return "─> "
        return "─< "

    def add_children(vertex, prefix=""):
        ordered_children = sorted(children[vertex])
        for index, child in enumerate(ordered_children):
            is_last = index == len(ordered_children) - 1
            branch = "└" if is_last else "├"
            lines.append(f"{prefix}{branch}{connector(vertex, child)}({child})")
            add_children(child, prefix + ("   " if is_last else "│  "))

    add_children(root)
    extra_edges = sorted(component_edges - tree_edges)
    if extra_edges:
        edge_marker = "->" if directed else "--"
        lines.append(
            "extra edges: " + ", ".join(
                f"({start}) {edge_marker} ({end})"
                for start, end in extra_edges
            )
        )
    return lines


def draw_graph(data, parameter_name, representation, directed, vertex_count=None):
    if representation == "edge_list":
        parsed = _parse_edge_list(data, directed, vertex_count)
    elif representation == "adjacency_matrix":
        parsed = _parse_adjacency_matrix(data, directed)
    else:
        return

    if not parsed:
        return

    vertices, edges = parsed
    total_vertices, total_edges = len(vertices), len(edges)
    selected_vertices = set(sorted(vertices)[:12])
    selected_edges = {
        edge for edge in edges
        if edge[0] in selected_vertices and edge[1] in selected_vertices
    }
    selected_edges = set(sorted(selected_edges)[:20])

    components, neighbours = _graph_components(selected_vertices, selected_edges)
    sections = []
    for index, component in enumerate(components, start=1):
        lines = [f"component {index}:"]
        lines.extend(_draw_graph_component(
            component, neighbours, selected_edges, directed))
        sections.append("\n".join(lines))

    if total_vertices > len(selected_vertices) or total_edges > len(selected_edges):
        sections.append(
            "… truncated: showing "
            f"{len(selected_vertices)} of {total_vertices} nodes and "
            f"{len(selected_edges)} of {total_edges} edges"
        )

    return (parameter_name, "\n\n".join(sections) if sections else "(empty graph)")


def draw_ascii(
    data,
    problem_type,
    parameter_name,
    parameter_type,
    graph_metadata=None,
    graph_vertex_count=None,
):
    """
    █▓▒░#║╬■⬛🧱~≈∼≋≀·○🌊💧■▲◆●⬤⛰GO⊙✦★
    """
    if (
        problem_type == ProblemType.GRAPH
        and graph_metadata
        and parameter_name == graph_metadata.get("graph_parameter")
    ):
        directed = graph_metadata.get("directed")
        if type(directed) is not bool:
            return
        return draw_graph(
            data,
            parameter_name,
            graph_metadata.get("graph_representation"),
            directed,
            graph_vertex_count,
        )

    if problem_type == ProblemType.GRAPH:
        return

    match parameter_type:
        case "int":
            return
        case "list[list[int]]":
            return draw_grid(data, parameter_name, parameter_type)

    # This part to be remove because all data should have type.
    match parameter_type:
        case ProblemType.LINKED_LIST:
            return draw_linked_list(data, parameter_name)
        case ProblemType.BINARY_TREE:
            return draw_tree(data, parameter_name)
        case "list[int]":
            return draw_list(data, parameter_name)
        case "list[list[int]]" | "list[list[string]]" | "grid":
            return draw_grid(data, parameter_name, parameter_type)

    if (
        problem_type == ProblemType.BINARY_TREE
        and isinstance(data, list)
    ):
        bt = binarytree.build2(data).__str__()
        return (parameter_name, bt)

    elif (
        problem_type == ProblemType.LINKED_LIST
        and isinstance(data, list)
    ):
        return draw_linked_list(data, parameter_name)

    # for grid/matrix/board-like data
    # When in-place method returns void there is no parameter type.
    elif (
        problem_type not in (
            ProblemType.BINARY_TREE,
            ProblemType.LINKED_LIST,
            ProblemType.GRAPH,
        )
        and data
        and isinstance(data, list)
        and isinstance(data[0], list)
    ):
        return draw_grid(data, parameter_name, parameter_type)
