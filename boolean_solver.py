import networkx as nx
from typing import Dict, List, Set, Tuple, Any, Union
from itertools import combinations

class BooleanSolver:
    """Convert package dependency constraints to boolean formulas and evaluate them"""
    
    def __init__(self, dependency_graph: nx.DiGraph, root_package: str):
        self.dependency_graph = dependency_graph
        self.root_package = root_package
        self.packages = list(dependency_graph.nodes())
        
        # Group packages by name
        self.package_groups = {}
        for package in self.packages:
            name = self._get_package_name(package)
            if name not in self.package_groups:
                self.package_groups[name] = []
            self.package_groups[name].append(package)
    
    def _get_package_name(self, package: str) -> str:
        """Extract package name from package string"""
        if '-' in package:
            parts = package.rsplit('-', 1)
            if len(parts) == 2 and '.' in parts[1]:
                return parts[0]
        elif '==' in package:
            return package.split('==')[0]
        return package
    
    def generate_clauses(self) -> List[List[Tuple[str, bool]]]:
        """Generate boolean clauses representing the dependency constraints"""
        clauses = []
        
        # 1. Root package must be installed (at least one version)
        root_name = self._get_package_name(self.root_package)
        if root_name in self.package_groups:
            root_clause = [(pkg, True) for pkg in self.package_groups[root_name]]
            clauses.append(root_clause)
        
        # 2. At most one version of each package can be selected
        for package_name, versions in self.package_groups.items():
            if len(versions) > 1:
                # For each pair of versions, at least one must be false
                for pkg1, pkg2 in combinations(versions, 2):
                    clauses.append([(pkg1, False), (pkg2, False)])
        
        # 3. Dependency constraints: if package A is selected, its dependencies must be satisfied
        for package in self.packages:
            dependencies = list(self.dependency_graph.successors(package))
            
            for dep in dependencies:
                dep_name = self._get_package_name(dep)
                if dep_name in self.package_groups:
                    # If package is selected, then at least one version of dependency must be selected
                    dep_versions = [(pkg, True) for pkg in self.package_groups[dep_name]]
                    clause = [(package, False)] + dep_versions
                    clauses.append(clause)
        
        return clauses
    
    def evaluate_clause(self, clause: List[Tuple[str, bool]], selected_packages: Set[str]) -> bool:
        """Evaluate a single boolean clause given the current selection"""
        for package, required_state in clause:
            is_selected = package in selected_packages
            
            if required_state and is_selected:
                return True  # At least one positive literal is true
            elif not required_state and not is_selected:
                return True  # At least one negative literal is true
        
        return False  # No literal in the clause is satisfied
    
    def evaluate_all_clauses(self, selected_packages: Set[str]) -> Tuple[bool, List[bool]]:
        """Evaluate all clauses and return overall satisfaction and individual results"""
        clauses = self.generate_clauses()
        results = []
        
        for clause in clauses:
            result = self.evaluate_clause(clause, selected_packages)
            results.append(result)
        
        all_satisfied = all(results)
        return all_satisfied, results
    
    def format_clause_for_display(self, clause: List[Tuple[str, bool]]) -> str:
        """Format a clause for human-readable display"""
        parts = []
        
        for package, required_state in clause:
            package_name = self._get_package_name(package)
            version = package.replace(package_name, '').lstrip('-=')
            
            if required_state:
                parts.append(f"{package_name}({version})")
            else:
                parts.append(f"¬{package_name}({version})")
        
        return " ∨ ".join(parts)  # OR operator
    
    def get_constraint_explanation(self) -> Dict[str, List[str]]:
        """Get human-readable explanations of the constraints"""
        explanations = {
            'root_constraint': [],
            'version_constraints': [],
            'dependency_constraints': []
        }
        
        # Root constraint
        root_name = self._get_package_name(self.root_package)
        explanations['root_constraint'].append(
            f"At least one version of {root_name} must be selected (it's the root package)"
        )
        
        # Version constraints
        for package_name, versions in self.package_groups.items():
            if len(versions) > 1:
                version_list = [v.replace(package_name, '').lstrip('-=') for v in versions]
                explanations['version_constraints'].append(
                    f"At most one version of {package_name} can be selected: {', '.join(version_list)}"
                )
        
        # Dependency constraints
        for package in self.packages:
            dependencies = list(self.dependency_graph.successors(package))
            if dependencies:
                package_name = self._get_package_name(package)
                package_version = package.replace(package_name, '').lstrip('-=')
                
                dep_names = [self._get_package_name(dep) for dep in dependencies]
                unique_dep_names = list(set(dep_names))
                
                explanations['dependency_constraints'].append(
                    f"If {package_name}({package_version}) is selected, "
                    f"then {', '.join(unique_dep_names)} must also be selected"
                )
        
        return explanations
    
    def suggest_solution(self) -> Set[str]:
        """Suggest a valid solution using constraint satisfaction"""
        # Simple greedy approach: start with root and add required dependencies
        solution = set()
        
        # Add root package (prefer latest version)
        root_name = self._get_package_name(self.root_package)
        if root_name in self.package_groups:
            # Sort versions and pick the latest (simple string sort)
            root_versions = sorted(self.package_groups[root_name], reverse=True)
            solution.add(root_versions[0])
        
        # Recursively add dependencies
        def add_dependencies(package: str, visited: Set[str]):
            if package in visited:
                return
            visited.add(package)
            
            dependencies = list(self.dependency_graph.successors(package))
            for dep in dependencies:
                dep_name = self._get_package_name(dep)
                
                # Check if we already have a version of this dependency
                already_have = False
                for selected in solution:
                    if self._get_package_name(selected) == dep_name:
                        already_have = True
                        break
                
                if not already_have and dep_name in self.package_groups:
                    # Add latest version of dependency
                    dep_versions = sorted(self.package_groups[dep_name], reverse=True)
                    selected_dep = dep_versions[0]
                    solution.add(selected_dep)
                    add_dependencies(selected_dep, visited)
        
        # Start from selected root package
        for package in solution.copy():
            add_dependencies(package, set())
        
        return solution
    
    def get_boolean_formula_stats(self) -> Dict[str, Any]:
        """Get statistics about the boolean formula"""
        clauses = self.generate_clauses()
        
        return {
            'total_clauses': len(clauses),
            'total_variables': len(self.packages),
            'package_groups': len(self.package_groups),
            'avg_clause_length': sum(len(clause) for clause in clauses) / len(clauses) if clauses else 0,
            'max_clause_length': max(len(clause) for clause in clauses) if clauses else 0,
            'min_clause_length': min(len(clause) for clause in clauses) if clauses else 0
        }
