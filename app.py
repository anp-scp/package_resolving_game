import streamlit as st
import plotly.graph_objects as go
import networkx as nx
from game_logic import PackageDependencyGame
from graph_generator import generate_sample_graphs
from boolean_solver import BooleanSolver
import json

# Configure page
st.set_page_config(page_title="Package Dependency Resolution Game",
                   page_icon="📦",
                   layout="centered",
                   initial_sidebar_state="expanded")

# Initialize session state
if 'game' not in st.session_state:
    st.session_state.game = None
if 'mode' not in st.session_state:
    st.session_state.mode = 'wild'
if 'selected_scenario' not in st.session_state:
    st.session_state.selected_scenario = 0


def create_interactive_graph(game):
    """Create an interactive Plotly graph from the game state"""
    G = game.dependency_graph

    # Use hierarchical layout based on package levels
    pos = game.get_hierarchical_layout()

    # Prepare node traces
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    node_info = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        package_name, version = game.parse_package_node(node)
        node_text.append(f"{package_name}<br>v{version}")

        # Color based on selection status
        if node in game.selected_packages:
            node_colors.append('#28a745')  # Green for selected
        else:
            node_colors.append('#ffffff')  # White for unselected

        # Add hover information
        dependencies = list(G.successors(node))
        dep_text = f"Dependencies: {', '.join(dependencies) if dependencies else 'None'}"
        node_info.append(f"{node}<br>{dep_text}")

    # Prepare border colors - sky blue for root package, black for others
    border_colors = []
    for node in G.nodes():
        if node == game.root_package:
            border_colors.append('#87CEEB')  # Sky blue for root package
        else:
            border_colors.append('black')    # Black for other packages
    
    # Create node trace
    node_trace = go.Scatter(x=node_x,
                            y=node_y,
                            mode='markers+text',
                            text=node_text,
                            textposition="middle center",
                            textfont=dict(color='#000000'),
                            hovertext=node_info,
                            hoverinfo='text',
                            marker=dict(size=50,
                                        color=node_colors,
                                        line=dict(width=2, color=border_colors)),
                            customdata=list(G.nodes()),
                            name="Packages")

    # Prepare edge traces with curves to avoid overlaps
    edge_traces = []
    arrow_annotations = []
    
    # Group edges by source node to detect potential overlaps
    edges_by_source = {}
    for edge in G.edges():
        source = edge[0]
        if source not in edges_by_source:
            edges_by_source[source] = []
        edges_by_source[source].append(edge)
    
    for source, edges in edges_by_source.items():
        if len(edges) == 1:
            # Single edge - draw straight line
            edge = edges[0]
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            edge_trace = go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                line=dict(width=2, color='#888'),
                hoverinfo='none',
                mode='lines',
                showlegend=False
            )
            edge_traces.append(edge_trace)
            
            # Add arrow annotation for straight edge
            arrow_annotations.append(
                dict(
                    x=x1,
                    y=y1,
                    ax=x0 + (x1 - x0) * 0.1,
                    ay=y0 + (y1 - y0) * 0.1,
                    xref='x',
                    yref='y',
                    axref='x',
                    ayref='y',
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor='#888',
                    standoff=25,
                ))
        else:
            # Multiple edges from same source - create curves
            for i, edge in enumerate(edges):
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                
                # Calculate curve offset based on edge index
                num_edges = len(edges)
                if num_edges == 2:
                    curve_offsets = [-0.3, 0.3]
                elif num_edges == 3:
                    curve_offsets = [-0.4, 0, 0.4]
                else:
                    curve_offsets = [0.6 * (2*j/(num_edges-1) - 1) for j in range(num_edges)]
                
                curve_offset = curve_offsets[i]
                
                # Create curved path
                mid_x = (x0 + x1) / 2
                mid_y = (y0 + y1) / 2
                
                # Calculate perpendicular offset
                edge_length = ((x1 - x0)**2 + (y1 - y0)**2)**0.5
                if edge_length > 0:
                    perp_x = -(y1 - y0) / edge_length * curve_offset
                    perp_y = (x1 - x0) / edge_length * curve_offset
                else:
                    perp_x = perp_y = 0
                
                # Control point for curve
                ctrl_x = mid_x + perp_x
                ctrl_y = mid_y + perp_y
                
                # Generate curved path points
                curve_points = 20
                curve_x = []
                curve_y = []
                
                for t in range(curve_points + 1):
                    t_norm = t / curve_points
                    # Quadratic Bezier curve
                    px = (1-t_norm)**2 * x0 + 2*(1-t_norm)*t_norm * ctrl_x + t_norm**2 * x1
                    py = (1-t_norm)**2 * y0 + 2*(1-t_norm)*t_norm * ctrl_y + t_norm**2 * y1
                    curve_x.append(px)
                    curve_y.append(py)
                
                edge_trace = go.Scatter(
                    x=curve_x,
                    y=curve_y,
                    line=dict(width=2, color='#888'),
                    hoverinfo='none',
                    mode='lines',
                    showlegend=False
                )
                edge_traces.append(edge_trace)
                
                # Add arrow annotation at end of curve
                arrow_start_t = 0.9  # Arrow starts at 90% along curve
                arrow_start_x = (1-arrow_start_t)**2 * x0 + 2*(1-arrow_start_t)*arrow_start_t * ctrl_x + arrow_start_t**2 * x1
                arrow_start_y = (1-arrow_start_t)**2 * y0 + 2*(1-arrow_start_t)*arrow_start_t * ctrl_y + arrow_start_t**2 * y1
                
                arrow_annotations.append(
                    dict(
                        x=x1,
                        y=y1,
                        ax=arrow_start_x,
                        ay=arrow_start_y,
                        xref='x',
                        yref='y',
                        axref='x',
                        ayref='y',
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1,
                        arrowwidth=2,
                        arrowcolor='#888',
                        standoff=25,
                    ))

    # Create figure
    fig = go.Figure(
        data=edge_traces + [node_trace],
        layout=go.
        Layout(title=dict(
            text="Package Dependency Graph - Click nodes to select/deselect",
            font=dict(size=16)),
               showlegend=False,
               hovermode='closest',
               margin=dict(b=20, l=5, r=5, t=40),
               annotations=arrow_annotations + [
                   dict(text="Click on packages to select/deselect them",
                        showarrow=False,
                        xref="paper",
                        yref="paper",
                        x=0.005,
                        y=-0.002,
                        xanchor="left",
                        yanchor="bottom",
                        font=dict(color="#888", size=12))
               ],
               xaxis=dict(showgrid=False, zeroline=False,
                          showticklabels=False),
               yaxis=dict(showgrid=False, zeroline=False,
                          showticklabels=False),
               plot_bgcolor='white'))

    return fig


def display_boolean_clauses(game):
    """Display boolean clauses with their evaluation status"""
    boolean_solver = BooleanSolver(game.dependency_graph, game.root_package)
    clauses = boolean_solver.generate_clauses()

    st.subheader("Boolean Formula Analysis")
    st.write(
        "The dependency constraints are converted to boolean clauses. All must be True:"
    )

    # Get original formulas and evaluate them
    original_formulas = boolean_solver.get_original_formulas()
    root_clauses = []
    version_clauses = []
    dependency_clauses = []

    for i, (clause, formula_info) in enumerate(zip(clauses,
                                                   original_formulas)):
        is_satisfied = boolean_solver.evaluate_clause(clause,
                                                      game.selected_packages)
        color = "green" if is_satisfied else "red"
        status = "✓ True" if is_satisfied else "✗ False"

        clause_info = {
            'index': i + 1,
            'original_formula': formula_info['formula'],
            'description': formula_info['description'],
            'satisfied': is_satisfied,
            'color': color,
            'status': status,
            'type': formula_info['type']
        }

        # Categorize clauses by type
        if formula_info['type'] == 'root':
            root_clauses.append(clause_info)
        elif formula_info['type'] == 'version_constraint':
            version_clauses.append(clause_info)
        elif formula_info['type'] == 'dependency':
            dependency_clauses.append(clause_info)

    # Display root package constraint
    if root_clauses:
        st.write("**Root Package Constraint:**")
        for clause_info in root_clauses:
            st.markdown(
                f"Term {clause_info['index']}: {clause_info['original_formula']}"
            )
            st.markdown(
                f"<span style='color: {clause_info['color']}; font-weight: bold;'>{clause_info['status']}</span>",
                unsafe_allow_html=True)
        st.write("---")

    # Display version constraints
    if version_clauses:
        st.write(
            "**Version Uniqueness Constraints (at most one version per package):**"
        )
        for clause_info in version_clauses:
            st.markdown(
                f"Term {clause_info['index']}: {clause_info['original_formula']}"
            )
            st.markdown(
                f"<span style='color: {clause_info['color']}; font-weight: bold;'>{clause_info['status']}</span>",
                unsafe_allow_html=True)
        st.write("---")

    # Display dependency constraints
    if dependency_clauses:
        st.write(
            "**Dependency Implications (if package selected, dependencies must be satisfied):**"
        )
        for clause_info in dependency_clauses:
            st.markdown(
                f"Term {clause_info['index']}: {clause_info['original_formula']}"
            )
            st.markdown(
                f"<span style='color: {clause_info['color']}; font-weight: bold;'>{clause_info['status']}</span>",
                unsafe_allow_html=True)
        st.write("---")

    # Overall satisfaction
    all_satisfied = all(clause_info['satisfied']
                        for clause_info in root_clauses + version_clauses +
                        dependency_clauses)
    overall_color = "green" if all_satisfied else "red"
    overall_status = "✓ ALL CONSTRAINTS SATISFIED" if all_satisfied else "✗ CONSTRAINTS VIOLATED"
    st.markdown(f"<h4 style='color: {overall_color};'>{overall_status}</h4>",
                unsafe_allow_html=True)


def main():
    st.title("📦 Package Dependency Resolution Game")
    st.write("Solve package dependencies like a package manager!")

    # Sidebar for game controls
    with st.sidebar:
        st.header("Game Controls")

        # Mode selection
        mode = st.radio(
            "Select Game Mode:", ["Wild Mode", "Boolean Mode"],
            help=
            "Wild Mode: Solve without assistance. Boolean Mode: See boolean clause evaluation."
        )
        st.session_state.mode = 'wild' if mode == "Wild Mode" else 'boolean'

        # Scenario selection
        scenarios = generate_sample_graphs()
        scenario_names = [
            f"Scenario {i+1}: {desc['name']}"
            for i, desc in enumerate(scenarios)
        ]

        selected_idx = st.selectbox("Choose a scenario:",
                                    range(len(scenarios)),
                                    format_func=lambda x: scenario_names[x])

        if selected_idx != st.session_state.selected_scenario or st.session_state.game is None:
            st.session_state.selected_scenario = selected_idx
            scenario = scenarios[selected_idx]
            st.session_state.game = PackageDependencyGame(
                scenario['graph'], scenario['root'])

        # Game controls
        if st.button("Reset Game"):
            scenario = scenarios[st.session_state.selected_scenario]
            st.session_state.game = PackageDependencyGame(
                scenario['graph'], scenario['root'])
            st.rerun()

        # Display game rules
        st.header("Game Rules")
        st.write("""
        1. **Goal**: Select packages to satisfy all dependencies for the root package
        2. **Constraints**:
           - No two versions of the same package can be selected
           - All selected packages must form a valid dependency chain
        3. **How to play**: Click on nodes in the graph to select/deselect them
        4. **Win condition**: All constraints satisfied and root package installable
        """)

    game = st.session_state.game

    if game is None:
        st.error("Failed to initialize game. Please try refreshing the page.")
        return

    # Main game area
    st.subheader("Dependency Graph")
    fig = create_interactive_graph(game)
    selected_points = st.plotly_chart(fig,
                                      use_container_width=True,
                                      key="graph")

    # Handle graph interactions
    if st.session_state.get('graph_click'):
        # This would be triggered by plotly events, but since we can't easily
        # capture clicks in Streamlit, we'll use buttons as an alternative
        pass

    # Alternative interaction method: Buttons for package selection
    st.subheader("Package Selection")
    st.write("Select packages by clicking the buttons below:")

    packages = list(game.dependency_graph.nodes())
    packages.sort()

    cols = st.columns(min(4, len(packages)))
    for i, package in enumerate(packages):
        col_idx = i % len(cols)
        package_name, version = game.parse_package_node(package)

        with cols[col_idx]:
            is_selected = package in game.selected_packages
            button_text = f"{'✓' if is_selected else '○'} {package_name} v{version}"

            if st.button(button_text, key=f"btn_{package}"):
                if is_selected:
                    game.deselect_package(package)
                else:
                    game.select_package(package)
                st.rerun()

    # Game status
    st.subheader("Game Status")

    # Check if solution is valid using boolean solver
    is_valid_solution = game.is_valid_solution()

    if is_valid_solution:
        st.success(
            "🎉 Congratulations! You've successfully resolved all dependencies!"
        )
        st.balloons()
    elif game.selected_packages:
        st.error(
            "❌ Current selection does not satisfy all constraints. Keep trying!"
        )
    else:
        st.info("Start by selecting some packages to begin.")

    # Display selected packages
    if game.selected_packages:
        st.subheader("Selected Packages")
        selected_list = sorted(list(game.selected_packages))
        st.write(", ".join(selected_list))

    # Display Boolean Formula Analysis at the bottom in Boolean mode
    if st.session_state.mode == 'boolean':
        display_boolean_clauses(game)


if __name__ == "__main__":
    main()
