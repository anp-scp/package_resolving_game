# Package Dependency Resolution Game - Web Version

A web-based interactive game where you play the role of a package manager and solve package dependencies by selecting the right packages to install. This is the web version of the original Streamlit application that can be hosted on GitHub Pages or any static hosting service.

## 🎮 How to Play

1. **Choose a Scenario**: Select from different pre-built dependency scenarios
2. **Understand the Goal**: Select packages to satisfy all dependencies for the root package
3. **Select Packages**: Click on nodes in the graph or use the package buttons to select/deselect packages
4. **Follow Constraints**: 
   - No two versions of the same package can be selected
   - All selected packages must form a valid dependency chain
5. **Win**: All constraints satisfied to make the root package installable

## 🚀 Features

- **Interactive Graph Visualization**: D3.js-powered dependency graph with force-directed layout
- **Multiple Scenarios**: Pre-built scenarios ranging from simple to complex dependency problems
- **Boolean Logic Hints**: Get hints based on boolean propositional logic
- **Solution Finder**: View all possible valid solutions
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time Validation**: Instant feedback on constraint satisfaction

## 🛠 Technologies Used

- **HTML5/CSS3**: Modern responsive layout
- **JavaScript (ES6+)**: Game logic and interactions  
- **D3.js v7**: Interactive graph visualization
- **CSS Grid/Flexbox**: Responsive layout system

## 📁 File Structure

```
web/
├── index.html          # Main HTML file
├── styles.css          # CSS styles and responsive design
├── app.js             # Main application logic and UI
├── game-logic.js      # Core game mechanics (port of Python game_logic.py)
├── graph-generator.js # Scenario generation (port of Python graph_generator.py)
├── boolean-solver.js  # Boolean constraint solver (port of Python boolean_solver.py)
└── README.md          # This file
```

## 🌐 Hosting

This is a static web application that can be hosted on:

- **GitHub Pages**: Just upload the files to a GitHub repository and enable Pages
- **Netlify**: Drag and drop the folder to Netlify
- **Vercel**: Import from GitHub or upload directly
- **Any static hosting service**: No server-side processing required

### GitHub Pages Setup

1. Create a new GitHub repository
2. Upload all files from the `web/` directory to the repository
3. Go to repository Settings > Pages
4. Select source as "Deploy from a branch"
5. Select branch "main" and folder "/ (root)"
6. Your game will be available at `https://yourusername.github.io/repository-name`

## 🎯 Game Scenarios

The game includes several built-in scenarios:

1. **Boolean Logic**: A==2.0 with complex B and G version dependencies
2. **Simple Web App**: A basic web application with Flask and requests
3. **Data Science Stack**: Scientific computing with numpy, pandas, and matplotlib  
4. **Torch GPU Stack**: A challenging scenario with version conflicts (unsatisfiable)

## 🔧 Customization

You can easily add new scenarios by modifying the `GraphGenerator.generateSampleGraphs()` function in `graph-generator.js`. Each scenario needs:

- `name`: Scenario display name
- `description`: Brief description
- `graph`: Object with `nodes` (array) and `edges` (array of [source, target] pairs)
- `root`: The root package name

## 📱 Responsive Design

The application is fully responsive and adapts to different screen sizes:

- **Desktop**: Full sidebar with graph and package selection side by side
- **Tablet**: Sidebar collapses to top, graph stacks vertically
- **Mobile**: Optimized touch interface with simplified layout

## 🧠 Boolean Logic

The game uses boolean propositional logic to represent package dependencies:

- **Root constraint**: Root package must be installed
- **Version constraints**: At most one version per package can be selected  
- **Dependency constraints**: If a package is selected, its dependencies must be satisfied

The boolean hints feature shows these constraints as logical formulas to help guide your selection.

## 🎨 Features Highlights

- **Visual Graph**: Interactive force-directed graph showing package dependencies
- **Real-time Updates**: Graph and status update immediately as you select packages
- **Color Coding**: 
  - Green: Selected packages and satisfied dependencies
  - Red border: Root package
  - Different colors: Different package families
- **Animations**: Smooth transitions and celebration effects
- **Modal Dialogs**: Clean interfaces for hints, solutions, and errors

## 🏆 Educational Value

This game helps understand:

- Package dependency resolution in software engineering
- Boolean satisfiability problems (SAT)
- Graph theory and dependency graphs
- Constraint satisfaction problems
- Package manager internals

## 👥 Credits

Brought to life by [Anupam](https://github.com/anp-scp) and [Ayush](https://github.com/AyushShrivstava).

Built with [Replit](https://replit.com/), [Cursor](https://www.cursor.com/) and sprinkled with a dash of creativity!

## 📝 License

This project is open source. Feel free to use, modify, and distribute as needed.
