import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from game_logic import PackageDependencyGame
from graph_generator import generate_sample_graphs
from boolean_solver import BooleanSolver
import json
import random
import colorsys

# Configure page
st.set_page_config(page_title="Package Dependency Resolution Game",
                   page_icon="📦",
                   layout="wide",
                   initial_sidebar_state="expanded")

# Initialize session state
if 'game' not in st.session_state:
    st.session_state.game = None
if 'selected_scenario' not in st.session_state:
    st.session_state.selected_scenario = 0

def generate_high_contrast_colors(n, seed=None):
    """
    Generate n visually distinct, high-contrast colors.
    Returns a list of hex color strings.
    Optionally takes a random seed for reproducibility.
    """
    rng = random.Random(seed)
    hues = [(i / n) for i in range(n)]
    rng.shuffle(hues)
    colors = []
    for h in hues:
        # High saturation and value for vivid colors
        r, g, b = colorsys.hsv_to_rgb(h, 0.85, 0.95)
        colors.append(f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}')
    return colors

def create_matplotlib_graph(game):
    """Create a matplotlib graph from the game state"""
    G = game.dependency_graph
    
    # Use hierarchical layout based on package levels
    pos = game.get_hierarchical_layout()
    
    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    # ax.set_aspect('equal')
    
    # Prepare node colors and edge colors for different border colors
    node_colors = []
    edge_colors = []
    package_color_map = dict()
    random_colors = generate_high_contrast_colors(len(G.nodes()), seed=17342)
    clr_index = 0
    
    for node in G.nodes():
        if node in game.selected_packages:
            node_colors.append('#28a745')  # Green for selected
        else:
            node_colors.append('#ffffff')  # White for unselected
        
        # Determine edge color - sky blue for root package, black for others
        if node == game.root_package:
            edge_colors.append('red')
        else:
            if package_color_map.get(node[:node.find('==')]) is None:
                package_color_map[node[:node.find('==')]] = random_colors[clr_index]
                clr_index += 1
            edge_colors.append('black')
    
    # Prepare edge colors: green if both nodes are selected, else black
    edge_colors_draw = []
    for u, v in G.edges():
        if u in game.selected_packages and v in game.selected_packages:
            edge_colors_draw.append('#28a745')  # Green
        else:
            edge_colors_draw.append('black')
    
    # Draw edges first (so they appear behind nodes)
    nx.draw_networkx_edges(G, pos, ax=ax, 
                          edgelist=list(G.edges()),
                          edge_color=edge_colors_draw,  # type: ignore
                          arrows=True, 
                          arrowsize=25, 
                          arrowstyle='->', 
                          width=3,
                          connectionstyle="arc3,rad=0.4",
                          min_source_margin=30,
                          min_target_margin=30)
    
    # Draw nodes using nx.draw_networkx_nodes
    nx.draw_networkx_nodes(G, pos, ax=ax,
                          node_color=node_colors,
                          edgecolors=edge_colors,
                          linewidths=2,
                          node_size=3800,
                          nodelist=list(G.nodes()))
    
    # Draw labels
    labels = {}
    for node in G.nodes():
        package_name, version = game.parse_package_node(node)
        labels[node] = f"{package_name}\nv{version}"
    
    nx.draw_networkx_labels(G, pos, labels, ax=ax, 
                           font_size=13, 
                           font_color='black',
                           font_weight='bold')
    
    # Set title and remove axes
    root_name, root_version = game.parse_package_node(game.root_package)
    ax.set_title(f'Solve dependencies for {root_name} v{root_version}', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    # Adjust layout to prevent clipping
    plt.tight_layout()
    
    return fig

@st.dialog("Boolean Hints")
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


    # Overall satisfaction
    all_satisfied = all(clause_info['satisfied']
                        for clause_info in root_clauses + version_clauses +
                        dependency_clauses)
    overall_color = "green" if all_satisfied else "red"
    overall_status = "✓ ALL CONSTRAINTS SATISFIED" if all_satisfied else "✗ SOME CONSTRAINTS VIOLATED. CHECK THEM BELOW"
    st.markdown(f"<h4 style='color: {overall_color};'>{overall_status}</h4>",
                unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Root Constraints", "Version Constraints", "Dependency Constraints"])
    # Display root package constraint
    if root_clauses:
        with tab1:
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
        with tab2:
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
        with tab3:
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

@st.dialog("Version Conflict")
def show_version_conflict_dialog():
    st.warning("Cannot select multiple versions of the same package. Deselect the previous version.", icon="⚠️")

@st.dialog("Solution")
def show_solution_dialog(game):
    """Display all valid solutions (sets of packages) in a dialog box"""
    boolean_solver = BooleanSolver(game.dependency_graph, game.root_package)
    all_solutions = boolean_solver.all_solutions(max_solutions=5)
    if not all_solutions:
        st.error("The constraints are unsatisfiable. No valid solution exists for this scenario.")
        return
    st.subheader("Valid Solutions")
    st.write(f"Showing {len(all_solutions)} solution(s):")
    for idx, solution in enumerate(all_solutions, 1):
        formatted = []
        for pkg in sorted(solution):
            name, version = game.parse_package_node(pkg)
            formatted.append(f"{name} v{version}")
        st.markdown(f"**Solution {idx}:** " + ", ".join(formatted))
    st.info("Here, we show 5 possibles solutions at max. Feel free to find more solutions.", icon="ℹ️")

def main():
    st.title("Package Dependency Resolution Game")
    # st.write("Put on the robe of a package manager and solve dependencies!")
    st.markdown(
        """Whenever we install a package from a package manager like `pip`, `apt`, `conda`, etc., the package manager has to
        ensure that all direct and indirect dependencies of the package are satisfied without any conflicts. Such dependencies
        can be represented as a directed graph, where nodes are packages and edges represent dependencies.
        """ 
    )
    st.write(
        """You will play the role of a package manager and resolve package dependencies by selecting packages to install. The goal is
        to select packages such that all dependencies for the root package are satisfied without any conflicts. 
        The game presents a dependency graph for the root package on the left. The right side shows the packages that are available to install. You can select packages by clicking on them. The game will automatically update the dependency graph to reflect the selected packages."""
    )
    st.info(
        """Before starting, we recommend that you go through this article which explains what happens behing the scenes when you install a package using a package manager:
        [Boolean Propositional Logic for software installations?](https://anp-scp.github.io/blog/2025/06/12/boolean-propositional-logic-for-software-installations/)""",
        icon="⚠️"
    )
    # st.write("The game presents a dependency graph for the root package on the left. The right side shows the packages that are available to install. You can select packages by clicking on them. The game will automatically update the dependency graph to reflect the selected packages.")

    # Sidebar for game controls
    with st.sidebar:
        st.header("Game Controls")


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
        1. **Goal**: Select packages to satisfy all dependencies (direct/indirect) for the root package
        2. If a package depend on multiple versions of the same package, selecting any one version is enough
        3. **Constraints**:
           - No two versions of the same package can be selected
           - All selected packages must form a valid dependency chain
        4. **How to play**: Click on nodes in the graph to select/deselect them for installation
        5. **Win condition**: All constraints satisfied to make root package installable
        6. **Boolean Hints**: Use boolean clauses to guide your selection whenever you are stuck.
        """)

    game = st.session_state.game    

    if game is None:
        st.error("Failed to initialize game. Please try refreshing the page.")
        return

    # Main game area
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Dependency Graph")
        fig = create_matplotlib_graph(game)
        st.pyplot(fig, use_container_width=True)
    with col2:
        st.subheader("Package Selection")
        st.write("Select packages by clicking the buttons below:")

        packages = list(game.dependency_graph.nodes())
        packages.sort()
        cols = st.columns(min(2, len(packages)))
        for i, package in enumerate(packages):
            col_idx = i % len(cols)
            package_name, version = game.parse_package_node(package)

            with cols[col_idx]:
                is_selected = package in game.selected_packages
                button_text = f"{'✓' if is_selected else '○'} {package_name} v{version}"

                if st.button(button_text, key=f"btn_{package}"):
                    if is_selected:
                        game.deselect_package(package)
                        st.rerun()
                    else:
                        result = game.select_package(package)
                        if result == 1:
                            st.rerun()
                        elif result == 0:
                            show_version_conflict_dialog()
                        else:
                            st.warning("Failed to select package. Please try again.", icon="❌")
        # Show selected packages below selection buttons
        st.subheader("Selected Packages")
        if game.selected_packages:
            selected_list = sorted(list(game.selected_packages))
            st.write(", ".join(selected_list))
        else:
            st.write("None")
        # Place the hint button below selected packages
        st.subheader("Boolean Hints")
        st.write("Want hints as boolean clauses?")
        if st.button("Show Boolean Hints", key="show_boolean_hints_col2"):
            if st.session_state.game is not None:
                display_boolean_clauses(st.session_state.game)
            else:
                st.error("Game not initialized. Please select a scenario first.")

        # Add Show Solution button
        st.write("Or reveal the solution?")
        if st.button("Show Solution", key="show_solution_col2"):
            if st.session_state.game is not None:
                show_solution_dialog(st.session_state.game)
            else:
                st.error("Game not initialized. Please select a scenario first.")

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

    # Footer with authors
    st.markdown("---")
    st.markdown(
        """
        <style>
        #footer-authors a, 
        #footer-authors a:visited, 
        #footer-authors a:active, 
        #footer-authors a:hover {
            color: inherit !important;
            text-decoration: underline;
            font-weight: bold;
        }
        </style>
        <div id='footer-authors' style='text-align: center; color: #666; font-size: 14px; padding: 1px 0 1px 0;'>
            Brought to life by <a href='https://github.com/anp-scp' target='_blank'>Anupam</a> and <a href='https://github.com/AyushShrivstava' target='_blank'>Ayush</a>.<br>
            Built with Streamlit, Replit, Cursor and sprinkled with a dash of creativity!<br>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
