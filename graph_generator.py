import networkx as nx
from typing import Dict, List, Any

def generate_sample_graphs() -> List[Dict[str, Any]]:
    """Generate sample dependency graphs for different game scenarios"""
    
    scenarios = []
    
    # Scenario 1: Simple web application
    G1 = nx.DiGraph()
    packages = [
        "myapp==1.0.0",
        "flask==2.0.0", "flask==1.5.0",
        "requests==2.25.0", "requests==2.20.0",
        "jinja2==3.0.0",
        "urllib3==1.26.0"
    ]
    
    G1.add_nodes_from(packages)
    G1.add_edges_from([
        ("myapp==1.0.0", "flask==2.0.0"),
        ("myapp==1.0.0", "requests==2.25.0"),
        ("flask==2.0.0", "jinja2==3.0.0"),
        ("requests==2.25.0", "urllib3==1.26.0"),
        ("flask==1.5.0", "jinja2==3.0.0"),
        ("requests==2.20.0", "urllib3==1.26.0")
    ])
    
    scenarios.append({
        'name': 'Simple Web App',
        'description': 'A basic web application with Flask and requests',
        'graph': G1,
        'root': 'myapp==1.0.0'
    })
    
    # Scenario 2: Data science project
    G2 = nx.DiGraph()
    packages = [
        "datascience==1.0.0",
        "numpy==1.21.0", "numpy==1.20.0",
        "pandas==1.3.0", "pandas==1.2.0",
        "matplotlib==3.4.0",
        "scipy==1.7.0",
        "python-dateutil==2.8.0"
    ]
    
    G2.add_nodes_from(packages)
    G2.add_edges_from([
        ("datascience==1.0.0", "numpy==1.21.0"),
        ("datascience==1.0.0", "pandas==1.3.0"),
        ("datascience==1.0.0", "matplotlib==3.4.0"),
        ("pandas==1.3.0", "numpy==1.21.0"),
        ("pandas==1.3.0", "python-dateutil==2.8.0"),
        ("pandas==1.2.0", "numpy==1.20.0"),
        ("pandas==1.2.0", "python-dateutil==2.8.0"),
        ("matplotlib==3.4.0", "numpy==1.21.0"),
        ("scipy==1.7.0", "numpy==1.21.0")
    ])
    
    scenarios.append({
        'name': 'Data Science Stack',
        'description': 'Scientific computing with numpy, pandas, and matplotlib',
        'graph': G2,
        'root': 'datascience==1.0.0'
    })
    
    # Scenario 3: Complex web framework
    G3 = nx.DiGraph()
    packages = [
        "webapp==2.0.0",
        "django==3.2.0", "django==3.1.0",
        "django-rest-framework==3.12.0",
        "psycopg2==2.9.0",
        "celery==5.1.0", "celery==4.4.0",
        "redis==3.5.0",
        "sqlparse==0.4.0",
        "pytz==2021.1"
    ]
    
    G3.add_nodes_from(packages)
    G3.add_edges_from([
        ("webapp==2.0.0", "django==3.2.0"),
        ("webapp==2.0.0", "django-rest-framework==3.12.0"),
        ("webapp==2.0.0", "psycopg2==2.9.0"),
        ("webapp==2.0.0", "celery==5.1.0"),
        ("django==3.2.0", "sqlparse==0.4.0"),
        ("django==3.2.0", "pytz==2021.1"),
        ("django==3.1.0", "sqlparse==0.4.0"),
        ("django==3.1.0", "pytz==2021.1"),
        ("django-rest-framework==3.12.0", "django==3.2.0"),
        ("celery==5.1.0", "redis==3.5.0"),
        ("celery==4.4.0", "redis==3.5.0")
    ])
    
    scenarios.append({
        'name': 'Django Web Framework',
        'description': 'Complex web application with Django, REST API, and background tasks',
        'graph': G3,
        'root': 'webapp==2.0.0'
    })
    
    # Scenario 4: Machine Learning project
    G4 = nx.DiGraph()
    packages = [
        "mlproject==1.0.0",
        "tensorflow==2.5.0", "tensorflow==2.4.0",
        "scikit-learn==0.24.0",
        "numpy==1.19.0", "numpy==1.21.0",
        "pandas==1.3.0",
        "matplotlib==3.4.0",
        "keras==2.5.0",
        "scipy==1.7.0"
    ]
    
    G4.add_nodes_from(packages)
    G4.add_edges_from([
        ("mlproject==1.0.0", "tensorflow==2.5.0"),
        ("mlproject==1.0.0", "scikit-learn==0.24.0"),
        ("mlproject==1.0.0", "pandas==1.3.0"),
        ("tensorflow==2.5.0", "numpy==1.21.0"),
        ("tensorflow==2.4.0", "numpy==1.19.0"),
        ("scikit-learn==0.24.0", "numpy==1.21.0"),
        ("scikit-learn==0.24.0", "scipy==1.7.0"),
        ("pandas==1.3.0", "numpy==1.21.0"),
        ("matplotlib==3.4.0", "numpy==1.21.0"),
        ("scipy==1.7.0", "numpy==1.21.0")
    ])
    
    scenarios.append({
        'name': 'Machine Learning',
        'description': 'ML project with TensorFlow, scikit-learn, and data processing tools',
        'graph': G4,
        'root': 'mlproject==1.0.0'
    })
    
    # Scenario 5: Boolean Logic Example (A-2.0 depends on B and G versions)
    G5 = nx.DiGraph()
    packages = [
        "A==2.0",
        "B==1.3", "B==1.4",
        "G==0.5", "G==0.6", "G==0.7"
    ]
    
    G5.add_nodes_from(packages)
    G5.add_edges_from([
        ("A==2.0", "B==1.3"),
        ("A==2.0", "B==1.4"),
        ("A==2.0", "G==0.6"),
        ("A==2.0", "G==0.7"),
        ("B==1.3", "G==0.5"),
        ("B==1.3", "G==0.6"),
        ("B==1.4", "G==0.7")
    ])
    
    scenarios.append({
        'name': 'Boolean Logic Example',
        'description': 'A==2.0 with complex B and G version dependencies',
        'graph': G5,
        'root': 'A==2.0'
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
