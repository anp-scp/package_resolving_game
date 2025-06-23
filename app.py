import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from game_logic import PackageDependencyGame
from graph_generator import generate_sample_graphs
from boolean_solver import BooleanSolver
import json

# Configure page
st.set_page_config(page_title="Package Dependency Resolution Game",
                   page_icon="📦",
                   layout="wide",
                   initial_sidebar_state="expanded")

# Initialize session state
if 'game' not in st.session_state:
    st.session_state.game = None
if 'mode' not in st.session_state:
    st.session_state.mode = 'wild'
if 'selected_scenario' not in st.session_state:
    st.session_state.selected_scenario = 0


def create_matplotlib_graph(game):
    """Create a matplotlib graph from the game state"""
    G = game.dependency_graph
    
    # Use hierarchical layout based on package levels
    pos = game.get_hierarchical_layout()
    
    # Create figure and axis
    fig, ax = plt.subplots(1, 1, )
    ax.set_aspect('equal')
    
    # Prepare node colors and edge colors for different border colors
    node_colors = []
    edge_colors = []
    
    for node in G.nodes():
        if node in game.selected_packages:
            node_colors.append('#28a745')  # Green for selected
        else:
            node_colors.append('#ffffff')  # White for unselected
        
        # Determine edge color - sky blue for root package, black for others
        if node == game.root_package:
            edge_colors.append('#87CEEB')  # Sky blue for root package
        else:
            edge_colors.append('#888888')    # Black for other packages
    
    # Draw edges first (so they appear behind nodes)
    nx.draw_networkx_edges(G, pos, ax=ax, 
                          edge_color='#888888', 
                          arrows=True, 
                          arrowsize=20, 
                          arrowstyle='->', 
                          width=2,
                          connectionstyle="arc3,rad=0.1")
    
    # Draw nodes using nx.draw_networkx_nodes
    nx.draw_networkx_nodes(G, pos, ax=ax,
                          node_color=node_colors,
                          edgecolors=edge_colors,
                          linewidths=2,
                          node_size=800,
                          nodelist=list(G.nodes()))
    
    # Draw labels
    labels = {}
    for node in G.nodes():
        package_name, version = game.parse_package_node(node)
        labels[node] = f"{package_name}\nv{version}"
    
    nx.draw_networkx_labels(G, pos, labels, ax=ax, 
                           font_size=8, 
                           font_color='black',
                           font_weight='bold')
    
    # Set title and remove axes
    ax.set_title('Package Dependency Graph', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    # Adjust layout to prevent clipping
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
    fig = create_matplotlib_graph(game)
    st.pyplot(fig, use_container_width=False)

    # Graph is now non-interactive - use buttons below for interaction

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
