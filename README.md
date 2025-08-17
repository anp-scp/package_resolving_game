# Package Dependency Resolution Game

A web-based interactive game where you play the role of a package manager and solve package dependencies by selecting the right packages to install. There are two version of the game:

1. **Web Version (Fast)**: [View on Web](https://anp-scp.github.io/package_resolving_game/)
2. **Streamlit Version (Sometimes slow)**: [View on Streamlit](https://package-puzzle.streamlit.app/)

NOTE: The source code for the web version is in the `docs` dir. The name is kept as `docs` such that GitHub pages can fetch
static files from the directory. GitHub pages only `docs` name for static files.

## 🎮 How to Play

1. **Choose a Scenario**: Select from different pre-built dependency scenarios
2. **Understand the Goal**: Select packages to satisfy all dependencies for the root package
3. **Select Packages**: Click on nodes in the graph or use the package buttons to select/deselect packages
4. **Follow Constraints**: 
   - No two versions of the same package can be selected
   - All selected packages must form a valid dependency chain
5. **Win**: All constraints satisfied to make the root package installable

## 🔧 Customization

You can easily add new scenarios by modifying the `GraphGenerator.generateSampleGraphs()` function in `graph-generator.js` for the web version. Each scenario needs:

- `name`: Scenario display name
- `description`: Brief description
- `graph`: Object with `nodes` (array) and `edges` (array of [source, target] pairs)
- `root`: The root package name

Similar to the web version, you can modify the Streamlit app to add new scenarios by updating the `generate_sample_graphs()` function in `graph_generator.py`.

## 🧠 Boolean Logic

The game uses boolean propositional logic to represent package dependencies:

- **Root constraint**: Root package must be installed
- **Version constraints**: At most one version per package can be selected  
- **Dependency constraints**: If a package is selected, its dependencies must be satisfied

The boolean hints feature shows these constraints as logical formulas to help guide your selection.

## 👥 Credits

Brought to life by [Anupam](https://github.com/anp-scp) and [Ayush](https://github.com/AyushShrivstava).

Built with [Replit](https://replit.com/), [Cursor](https://www.cursor.com/), [Copilot](https://github.com/features/copilot) and sprinkled with a dash of creativity!
