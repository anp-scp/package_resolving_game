import networkx as nx
from typing import Dict, List, Any

def generate_sample_graphs() -> List[Dict[str, Any]]:
    """Generate sample dependency graphs for different game scenarios"""
    
    scenarios = []

    # Scenario 1: Simple example (A-2.0 depends on B and G versions)
    G1 = nx.DiGraph()
    packages = [
        "A==2.0",
        "B==1.3", "B==1.4",
        "G==0.5", "G==0.6", "G==0.7"
    ]

    G1.add_nodes_from(packages)
    G1.add_edges_from([
        ("A==2.0", "B==1.3"),
        ("A==2.0", "B==1.4"),
        ("A==2.0", "G==0.6"),
        ("A==2.0", "G==0.7"),
        ("B==1.3", "G==0.5"),
        ("B==1.3", "G==0.6"),
        ("B==1.4", "G==0.7")
    ])
    
    scenarios.append({
        'name': 'Boolean Logic',
        'description': 'A==2.0 with complex B and G version dependencies',
        'graph': G1,
        'root': 'A==2.0'
    })
    
    # Scenario 1: Simple web application
    G2 = nx.DiGraph()
    packages = [
        "myapp==1.0.0",
        "flask==2.0.0", "flask==1.5.0",
        "req==2.25.0", "req==2.20.0",
        "jinja2==3.0.0",
        "urllib3==1.26.0"
    ]

    G2.add_nodes_from(packages)
    G2.add_edges_from([
        ("myapp==1.0.0", "flask==2.0.0"),
        ("myapp==1.0.0", "req==2.25.0"),
        ("flask==2.0.0", "jinja2==3.0.0"),
        ("req==2.25.0", "urllib3==1.26.0"),
        ("flask==1.5.0", "jinja2==3.0.0"),
        ("req==2.20.0", "urllib3==1.26.0")
    ])
    
    scenarios.append({
        'name': 'Simple Web App',
        'description': 'A basic web application with Flask and requests',
        'graph': G2,
        'root': 'myapp==1.0.0'
    })
    
    # Scenario 2: Data science project
    G3 = nx.DiGraph()
    packages = [
        "sklearn==1.0.0",
        "numpy==1.21.0", "numpy==1.20.0",
        "pandas==1.3.0", "pandas==1.2.0",
        "plotly==3.4.0",
        "scipy==1.7.0",
        "py_util==2.8.0"
    ]
    
    G3.add_nodes_from(packages)
    G3.add_edges_from([
        ("sklearn==1.0.0", "numpy==1.21.0"),
        ("sklearn==1.0.0", "pandas==1.3.0"),
        ("sklearn==1.0.0", "plotly==3.4.0"),
        ("pandas==1.3.0", "numpy==1.21.0"),
        ("pandas==1.3.0", "py_util==2.8.0"),
        ("pandas==1.2.0", "numpy==1.20.0"),
        ("pandas==1.2.0", "py_util==2.8.0"),
        ("plotly==3.4.0", "numpy==1.21.0"),
        ("scipy==1.7.0", "numpy==1.21.0")
    ])
    
    scenarios.append({
        'name': 'Data Science Stack',
        'description': 'Scientific computing with numpy, pandas, and matplotlib',
        'graph': G3,
        'root': 'sklearn==1.0.0'
    })
    
    # Scenario 4: Moderately tough but unsatisfiable
    G4 = nx.DiGraph()
    packages = [
        "torch==2.3.1",
        "cuda==12.1", "cuda==11.8",
        "cudnn==8.9.2", "cudnn==8.7.0",
        "driver==35.10"
    ]
    G4.add_nodes_from(packages)
    G4.add_edges_from([
        ("torch==2.3.1", "cuda==12.1"),
        ("torch==2.3.1", "cudnn==8.9.2"),
        ("cuda==12.1", "cudnn==8.7.0"),
        ("cuda==11.8", "driver==35.10"),
        ("cudnn==8.9.2", "cuda==11.8"),
        ("cudnn==8.7.0", "driver==35.10"),
        # Unsatisfiable: cuda==12.1 needs cudnn==8.7.0, but torch needs cudnn==8.9.2
    ])
    scenarios.append({
        'name': 'Torch GPU Stack',
        'description': 'A moderately tough scenario with a version conflict in the torch, cuda, cudnn, and driver GPU stack.',
        'graph': G4,
        'root': 'torch==2.3.1'
    })
    
    return scenarios

def create_custom_graph(packages: List[str], dependencies: List[tuple], root: str) -> Dict[str, Any]:
    """Create a custom dependency graph"""
    G = nx.DiGraph()
    G.add_nodes_from(packages)
    G.add_edges_from(dependencies)
    
    return {
        'name': 'Custom Graph',
        'description': 'User-defined dependency graph',
        'graph': G,
        'root': root
    }
