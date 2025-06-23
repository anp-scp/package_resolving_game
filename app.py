import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import networkx as nx
from game_logic import PackageDependencyGame
from graph_generator import generate_sample_graphs
from boolean_solver import BooleanSolver
import json
import numpy as np

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
    """Create a matplotlib graph from the game state with clean edge routing"""
    G = game.dependency_graph
    pos = game.get_hierarchical_layout()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_aspect('equal')
    
    # Draw edges with proper routing to avoid overlaps
    edge_offsets = {}
    for edge in G.edges():
        # Create unique edge identifier
        edge_key = tuple(sorted([edge[0], edge[1]]))
        if edge_key not in edge_offsets:
            edge_offsets[edge_key] = 0
        else:
            edge_offsets[edge_key] += 1
        
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        
        # Calculate offset for multiple edges between same nodes
        offset = edge_offsets[edge_key] * 0.1
        
        # Calculate perpendicular vector for offset
        dx = x1 - x0
        dy = y1 - y0
        length = np.sqrt(dx**2 + dy**2)
        
        if length > 0:
            # Perpendicular unit vector
            perp_x = -dy / length
            perp_y = dx / length
            
            # Apply offset
            offset_x = perp_x * offset
            offset_y = perp_y * offset
            
            # Draw curved edge using bezier-like curve
            if offset == 0:
                # Straight line for first edge
                ax.plot([x0, x1], [y0, y1], 'k-', alpha=0.6, linewidth=2)
                
                # Add arrow
                arrow_length = 0.15
                arrow_x = x1 - arrow_length * dx / length
                arrow_y = y1 - arrow_length * dy / length
                ax.annotate('', xy=(x1, y1), xytext=(arrow_x, arrow_y),
                           arrowprops=dict(arrowstyle='->', color='black', lw=2))
            else:
                # Curved line for subsequent edges
                mid_x = (x0 + x1) / 2 + offset_x
                mid_y = (y0 + y1) / 2 + offset_y
                
                # Create smooth curve using quadratic bezier
                t = np.linspace(0, 1, 50)
                curve_x = (1-t)**2 * x0 + 2*(1-t)*t * mid_x + t**2 * x1
                curve_y = (1-t)**2 * y0 + 2*(1-t)*t * mid_y + t**2 * y1
                
                ax.plot(curve_x, curve_y, 'k-', alpha=0.6, linewidth=2)
                
                # Add arrow at the end of curve
                arrow_t = 0.85
                arrow_x = (1-arrow_t)**2 * x0 + 2*(1-arrow_t)*arrow_t * mid_x + arrow_t**2 * x1
                arrow_y = (1-arrow_t)**2 * y0 + 2*(1-arrow_t)*arrow_t * mid_y + arrow_t**2 * y1
                ax.annotate('', xy=(x1, y1), xytext=(arrow_x, arrow_y),
                           arrowprops=dict(arrowstyle='->', color='black', lw=2))
    
    # Draw nodes
    for node in G.nodes():
        x, y = pos[node]
        package_name, version = game.parse_package_node(node)
        
        # Determine colors
        if node in game.selected_packages:
            face_color = '#28a745'  # Green for selected
            text_color = 'white'
        else:
            face_color = '#ffffff'  # White for unselected
            text_color = 'black'
        
        # Border color - sky blue for root package
        if node == game.root_package:
            edge_color = '#87CEEB'
            linewidth = 3
        else:
            edge_color = 'black'
            linewidth = 2
        
        # Draw node as circle
        circle = Circle((x, y), 0.2, facecolor=face_color, 
                           edgecolor=edge_color, linewidth=linewidth, zorder=3)
        ax.add_patch(circle)
        
        # Add text
        ax.text(x, y, f"{package_name}\nv{version}", 
               ha='center', va='center', fontsize=9, 
               color=text_color, weight='bold', zorder=4)
    
    # Style the plot
    ax.set_xlim(-1, max(pos.values(), key=lambda x: x[0])[0] + 1)
    ax.set_ylim(-1, max(pos.values(), key=lambda x: x[1])[1] + 1)
    ax.set_title('Package Dependency Graph', fontsize=16, pad=20)
    ax.axis('off')
    
    plt.tight_layout()
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
    st.pyplot(fig, use_container_width=True)

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
