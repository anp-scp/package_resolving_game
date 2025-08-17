// Graph Generator - JavaScript port of the Python graph_generator.py

class GraphGenerator {
    static generateSampleGraphs() {
        const scenarios = [];

        // Scenario 1: Boolean Logic
        const G1 = {
            nodes: [
                "A==2.0",
                "B==1.3", "B==1.4",
                "G==0.5", "G==0.6", "G==0.7"
            ],
            edges: [
                ["A==2.0", "B==1.3"],
                ["A==2.0", "B==1.4"],
                ["A==2.0", "G==0.6"],
                ["A==2.0", "G==0.7"],
                ["B==1.3", "G==0.5"],
                ["B==1.3", "G==0.6"],
                ["B==1.4", "G==0.7"]
            ]
        };
        
        scenarios.push({
            name: 'Boolean Logic',
            description: 'A==2.0 with complex B and G version dependencies',
            graph: G1,
            root: 'A==2.0'
        });

        // Scenario 2: Simple Web App
        const G2 = {
            nodes: [
                "myapp==1.0.0",
                "flask==2.0.0", "flask==1.5.0",
                "req==2.25.0", "req==2.20.0",
                "jinja2==3.0.0",
                "urllib3==1.26.0"
            ],
            edges: [
                ["myapp==1.0.0", "flask==2.0.0"],
                ["myapp==1.0.0", "req==2.25.0"],
                ["flask==2.0.0", "jinja2==3.0.0"],
                ["req==2.25.0", "urllib3==1.26.0"],
                ["flask==1.5.0", "jinja2==3.0.0"],
                ["req==2.20.0", "urllib3==1.26.0"]
            ]
        };
        
        scenarios.push({
            name: 'Simple Web App',
            description: 'A basic web application with Flask and requests',
            graph: G2,
            root: 'myapp==1.0.0'
        });

        // Scenario 3: Data Science Stack
        const G3 = {
            nodes: [
                "sklearn==1.0.0",
                "numpy==1.21.0", "numpy==1.20.0",
                "pandas==1.3.0", "pandas==1.2.0",
                "plotly==3.4.0",
                "scipy==1.7.0",
                "py_util==2.8.0"
            ],
            edges: [
                ["sklearn==1.0.0", "numpy==1.21.0"],
                ["sklearn==1.0.0", "pandas==1.3.0"],
                ["sklearn==1.0.0", "plotly==3.4.0"],
                ["pandas==1.3.0", "numpy==1.21.0"],
                ["pandas==1.3.0", "py_util==2.8.0"],
                ["pandas==1.2.0", "numpy==1.20.0"],
                ["pandas==1.2.0", "py_util==2.8.0"],
                ["plotly==3.4.0", "numpy==1.21.0"],
                ["scipy==1.7.0", "numpy==1.21.0"]
            ]
        };
        
        scenarios.push({
            name: 'Data Science Stack',
            description: 'Scientific computing with numpy, pandas, and matplotlib',
            graph: G3,
            root: 'sklearn==1.0.0'
        });

        // Scenario 4: Torch GPU Stack (Unsatisfiable)
        const G4 = {
            nodes: [
                "torch==2.3.1",
                "cuda==12.1", "cuda==11.8",
                "cudnn==8.9.2", "cudnn==8.7.0",
                "driver==35.10"
            ],
            edges: [
                ["torch==2.3.1", "cuda==12.1"],
                ["torch==2.3.1", "cudnn==8.9.2"],
                ["cuda==12.1", "cudnn==8.7.0"],
                ["cuda==11.8", "driver==35.10"],
                ["cudnn==8.9.2", "cuda==11.8"],
                ["cudnn==8.7.0", "driver==35.10"]
            ]
        };
        
        scenarios.push({
            name: 'Torch GPU Stack',
            description: 'A moderately tough scenario with a version conflict in the torch, cuda, cudnn, and driver GPU stack.',
            graph: G4,
            root: 'torch==2.3.1'
        });

        // Scenario 5: Complex Interdependent Packages (Difficult)
        const G5 = {
            nodes: [
                "app==1.0",
                "libA==1.0", "libA==2.0",
                "libB==1.0", "libB==2.0",
                "libC==1.0", "libC==2.0",
                "libD==1.0", "libD==2.0",
                "libE==1.0", "libE==2.0"
            ],
            edges: [
                // app depends on both versions of libA and libB (user must pick compatible versions)
                ["app==1.0", "libA==1.0"],
                ["app==1.0", "libA==2.0"],
                ["app==1.0", "libB==1.0"],
                ["app==1.0", "libB==2.0"],
                // libA v1.0 and v2.0 depend on different versions of libC
                ["libA==1.0", "libC==1.0"],
                ["libA==2.0", "libC==2.0"],
                // libB v1.0 and v2.0 depend on different versions of libD
                ["libB==1.0", "libD==1.0"],
                ["libB==2.0", "libD==2.0"],
                // libC v1.0 depends on libE v1.0, v2.0 on libE v2.0
                ["libC==1.0", "libE==1.0"],
                ["libC==2.0", "libE==2.0"],
                // libD v1.0 depends on libE v2.0, v2.0 on libE v1.0 (cross dependency)
                ["libD==1.0", "libE==2.0"],
                ["libD==2.0", "libE==1.0"],
                // Add a diamond/cycle: libE v1.0 depends on libA v2.0, libE v2.0 depends on libB v1.0
                ["libE==1.0", "libA==2.0"],
                ["libE==2.0", "libB==1.0"]
            ]
        };
        scenarios.push({
            name: 'Complex Interdependent Packages',
            description: 'A difficult scenario with multiple versions, cross dependencies, and a diamond/cycle structure. Requires careful selection to avoid version conflicts.',
            graph: G5,
            root: 'app==1.0'
        });

        return scenarios;
    }

    static createCustomGraph(packages, dependencies, root) {
        return {
            name: 'Custom Graph',
            description: 'User-defined dependency graph',
            graph: {
                nodes: packages,
                edges: dependencies
            },
            root: root
        };
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GraphGenerator;
}
