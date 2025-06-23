import networkx as nx
from typing import Dict, List, Set, Tuple, Any, Optional
import re

class PackageDependencyGame:
    """Main game logic for package dependency resolution"""
    
    def __init__(self, dependency_graph: nx.DiGraph, root_package: str):
        self.dependency_graph = dependency_graph.copy()
        self.root_package = root_package
        self.selected_packages: Set[str] = set()
        
        # Validate inputs
        if root_package not in dependency_graph.nodes():
            raise ValueError(f"Root package {root_package} not found in dependency graph")
    
    def parse_package_node(self, node: str) -> Tuple[str, str]:
        """Parse package node to extract package name and version"""
        # Assuming format like "package_name-1.0.0" or "package_name==1.0.0"
        if '-' in node:
            parts = node.rsplit('-', 1)
            if len(parts) == 2 and '.' in parts[1]:
                return parts[0], parts[1]
        elif '==' in node:
            parts = node.split('==')
            if len(parts) == 2:
                return parts[0], parts[1]
        
        # Fallback: treat as package name with default version
        return node, "1.0.0"
    
    def get_package_name(self, node: str) -> str:
        """Get package name without version"""
        return self.parse_package_node(node)[0]
    
    def get_package_version(self, node: str) -> str:
        """Get package version"""
        return self.parse_package_node(node)[1]
    
    def get_hierarchical_layout(self) -> Dict[str, Tuple[float, float]]:
        """Create hierarchical layout with packages organized by dependency levels"""
        # Calculate levels using topological sort
        try:
            # Check if graph is acyclic first
            if not nx.is_directed_acyclic_graph(self.dependency_graph):
                # If it has cycles, use spring layout
                return nx.spring_layout(self.dependency_graph, k=2, iterations=50)
            
            levels = {}
            topo_order = list(nx.topological_sort(self.dependency_graph))
            
            # Assign levels based on longest path from root
            for node in topo_order:
                if self.dependency_graph.in_degree(node) == 0:
                    levels[node] = 0
                else:
                    max_pred_level = -1
                    for pred in self.dependency_graph.predecessors(node):
                        if pred in levels:
                            max_pred_level = max(max_pred_level, levels[pred])
                    levels[node] = max_pred_level + 1
            
            # Group packages by level and by package name
            level_groups = {}
            for node, level in levels.items():
                if level not in level_groups:
                    level_groups[level] = {}
                
                package_name = self.get_package_name(node)
                if package_name not in level_groups[level]:
                    level_groups[level][package_name] = []
                level_groups[level][package_name].append(node)
            
            # Calculate positions
            pos = {}
            y_spacing = 2.0
            x_spacing = 2.0
            
            for level, package_groups in level_groups.items():
                y = -level * y_spacing  # Higher levels at top
                
                total_packages = sum(len(versions) for versions in package_groups.values())
                start_x = -(total_packages - 1) * x_spacing / 2
                
                x_offset = 0
                for package_name, versions in sorted(package_groups.items()):
                    for i, version_node in enumerate(sorted(versions)):
                        x = start_x + x_offset * x_spacing
                        pos[version_node] = (x, y + i * 0.3)  # Slight vertical offset for versions
                        x_offset += 1
            
            return pos
            
        except nx.NetworkXError:
            # Fallback to spring layout if graph has cycles
            return nx.spring_layout(self.dependency_graph, k=2, iterations=50)
    
    def select_package(self, package: str) -> bool:
        """Select a package. Returns True if selection was successful."""
        if package not in self.dependency_graph.nodes():
            return False
        
        # Check if selecting this package would violate version constraints
        package_name = self.get_package_name(package)
        for selected in self.selected_packages:
            if self.get_package_name(selected) == package_name:
                # Cannot select two versions of the same package
                return False
        
        self.selected_packages.add(package)
        return True
    
    def deselect_package(self, package: str) -> bool:
        """Deselect a package. Returns True if deselection was successful."""
        if package in self.selected_packages:
            self.selected_packages.remove(package)
            return True
        return False
    
    def check_constraints(self) -> List[str]:
        """Check all constraints and return list of violations"""
        violations = []
        
        # Check for multiple versions of same package
        package_names = {}
        for package in self.selected_packages:
            name = self.get_package_name(package)
            if name not in package_names:
                package_names[name] = []
            package_names[name].append(package)
        
        for name, versions in package_names.items():
            if len(versions) > 1:
                violations.append(f"Multiple versions selected for {name}: {', '.join(versions)}")
        
        # Check dependency satisfaction
        for package in self.selected_packages:
            dependencies = list(self.dependency_graph.successors(package))
            for dep in dependencies:
                dep_name = self.get_package_name(dep)
                
                # Check if any version of this dependency is selected
                dep_satisfied = False
                for selected in self.selected_packages:
                    if self.get_package_name(selected) == dep_name:
                        dep_satisfied = True
                        break
                
                if not dep_satisfied:
                    violations.append(f"{package} requires {dep_name} but it's not selected")
        
        return violations
    
    def is_valid_solution(self) -> bool:
        """Check if current selection is a valid solution using boolean solver"""
        from boolean_solver import BooleanSolver
        
        # Use boolean solver to check if all clauses are satisfied
        boolean_solver = BooleanSolver(self.dependency_graph, self.root_package)
        all_satisfied, _ = boolean_solver.evaluate_all_clauses(self.selected_packages)
        return all_satisfied
    
    def get_installable_packages(self) -> Set[str]:
        """Get set of packages that can be successfully installed with current selection"""
        installable = set()
        
        def can_install(package: str, visited: Optional[Set[str]] = None) -> bool:
            if visited is None:
                visited = set()
            assert visited is not None  # Type hint for mypy
            
            if package in visited:
                return True  # Assume already handled
            
            visited.add(package)
            
            # Check if package is selected
            package_name = self.get_package_name(package)
            package_selected = False
            for selected in self.selected_packages:
                if self.get_package_name(selected) == package_name:
                    package_selected = True
                    break
            
            if not package_selected:
                return False
            
            # Check dependencies
            dependencies = list(self.dependency_graph.successors(package))
            for dep in dependencies:
                if not can_install(dep, visited.copy()):
                    return False
            
            return True
        
        for package in self.selected_packages:
            if can_install(package):
                installable.add(package)
        
        return installable
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state for serialization/debugging"""
        return {
            'root_package': self.root_package,
            'selected_packages': list(self.selected_packages),
            'constraint_violations': self.check_constraints(),
            'is_valid_solution': self.is_valid_solution(),
            'total_packages': self.dependency_graph.number_of_nodes(),
            'total_dependencies': self.dependency_graph.number_of_edges()
        }
