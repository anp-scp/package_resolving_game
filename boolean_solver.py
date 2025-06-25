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
    
    def _get_clean_name(self, package: str) -> str:
        """Get clean package name for display (remove version separators)"""
        name = self._get_package_name(package)
        version = package.replace(name, '').lstrip('-=')
        return f"{name}{version}" if version else name
    
    def generate_clauses(self) -> List[List[Tuple[str, bool]]]:
        """Generate boolean clauses representing the dependency constraints"""
        clauses = []
        self.original_formulas = []  # Track original unsimplified formulas
        
        # 1. Root package must be installed
        clauses.append([(self.root_package, True)])
        self.original_formulas.append({
            'type': 'root',
            'formula': f"{self._get_clean_name(self.root_package)}",
            'description': f"Root package {self._get_clean_name(self.root_package)} must be installed"
        })
        
        # 2. At most one version of each package can be selected
        # NOT (X1 AND X2) = (NOT X1) OR (NOT X2)
        for package_name, versions in self.package_groups.items():
            if len(versions) > 1:
                # For each pair of versions, at least one must be false
                for pkg1, pkg2 in combinations(versions, 2):
                    clauses.append([(pkg1, False), (pkg2, False)])
                    # Original formula: NOT (X1 AND X2)
                    clean_pkg1 = self._get_clean_name(pkg1)
                    clean_pkg2 = self._get_clean_name(pkg2)
                    self.original_formulas.append({
                        'type': 'version_constraint',
                        'formula': f"¬({clean_pkg1} ∧ {clean_pkg2})",
                        'description': f"Cannot select both {clean_pkg1} and {clean_pkg2}"
                    })
        
        # 3. Dependency constraints: if package A is selected, its dependencies must be satisfied
        # A -> (B1 OR B2) becomes (NOT A) OR (B1 OR B2)
        for package in self.packages:
            dependencies = list(self.dependency_graph.successors(package))
            
            if dependencies:
                # Group dependencies by package name
                dep_groups = {}
                for dep in dependencies:
                    dep_name = self._get_package_name(dep)
                    if dep_name not in dep_groups:
                        dep_groups[dep_name] = []
                    dep_groups[dep_name].append(dep)
                
                # For each dependency group, create implication clause
                for dep_name, dep_versions in dep_groups.items():
                    # NOT package OR (dep_version1 OR dep_version2 OR ...)
                    clause = [(package, False)]  # NOT package
                    clause += [(dep, True) for dep in dep_versions]  # OR all versions
                    clauses.append(clause)
                    
                    # Original formula: A -> (B1 OR B2 OR ...)
                    clean_package = self._get_clean_name(package)
                    if len(dep_versions) == 1:
                        clean_deps = self._get_clean_name(dep_versions[0])
                    else:
                        clean_deps = " ∨ ".join([self._get_clean_name(dep) for dep in dep_versions])
                        clean_deps = f"({clean_deps})"
                    
                    self.original_formulas.append({
                        'type': 'dependency',
                        'formula': f"{clean_package} → {clean_deps}",
                        'description': f"If {clean_package} is selected, then {clean_deps} must be selected"
                    })
        
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
    
    def get_original_formulas(self) -> List[Dict[str, str]]:
        """Get the original unsimplified boolean formulas"""
        if not hasattr(self, 'original_formulas'):
            self.generate_clauses()  # Generate if not already done
        return self.original_formulas
    
    def all_solutions(self, max_solutions: int = 20) -> List[Set[str]]:
        """Enumerate all valid solutions (sets of packages) that satisfy all constraints. Returns up to max_solutions solutions."""
        clauses = self.generate_clauses()
        packages = list(self.packages)
        solutions = []
        n = len(packages)

        def backtrack(idx: int, selected: Set[str]):
            if len(solutions) >= max_solutions:
                return
            if idx == n:
                all_sat, _ = self.evaluate_all_clauses(selected)
                if all_sat:
                    solutions.append(set(selected))
                return
            pkg = packages[idx]
            # Try not selecting pkg
            backtrack(idx + 1, selected)
            # Try selecting pkg if no other version of this package is already selected
            pkg_name = self._get_package_name(pkg)
            for sel in selected:
                if self._get_package_name(sel) == pkg_name:
                    break
            else:
                selected.add(pkg)
                backtrack(idx + 1, selected)
                selected.remove(pkg)

        backtrack(0, set())

        # Minimize each solution by removing unnecessary packages
        minimized_solutions = []
        for sol in solutions:
            minimized = set(sol)
            for pkg in list(minimized):
                test_sol = minimized - {pkg}
                all_sat, _ = self.evaluate_all_clauses(test_sol)
                if all_sat:
                    minimized.remove(pkg)
            minimized_solutions.append(frozenset(minimized))

        # Deduplicate solutions
        unique_solutions = []
        seen = set()
        for sol in minimized_solutions:
            if sol not in seen:
                seen.add(sol)
                unique_solutions.append(set(sol))

        solutions = unique_solutions

        return solutions
