// Boolean Solver - JavaScript port of the Python boolean_solver.py

class BooleanSolver {
    constructor(dependencyGraph, rootPackage) {
        this.dependencyGraph = dependencyGraph;
        this.rootPackage = rootPackage;
        this.packages = dependencyGraph.nodes;
        
        // Group packages by name
        this.packageGroups = new Map();
        for (const pkg of this.packages) {
            const name = this.getPackageName(pkg);
            if (!this.packageGroups.has(name)) {
                this.packageGroups.set(name, []);
            }
            this.packageGroups.get(name).push(pkg);
        }
        
        this.originalFormulas = [];
    }

    getPackageName(packageStr) {
        // Extract package name from package string
        if (packageStr.includes('-') && packageStr.split('-').length === 2) {
            const parts = packageStr.split('-');
            if (parts.length === 2 && parts[1].includes('.')) {
                return parts[0];
            }
        } else if (packageStr.includes('==')) {
            return packageStr.split('==')[0];
        }
        return packageStr;
    }

    getCleanName(packageStr) {
        // Get clean package name for display
        const name = this.getPackageName(packageStr);
        const version = packageStr.replace(name, '').replace(/^[-=]+/, '');
        return version ? `${name}${version}` : name;
    }

    generateClauses() {
        // Generate boolean clauses representing the dependency constraints
        const clauses = [];
        this.originalFormulas = [];
        
        // 1. Root package must be installed
        clauses.push([[this.rootPackage, true]]);
        this.originalFormulas.push({
            type: 'root',
            formula: this.getCleanName(this.rootPackage),
            description: `Root package ${this.getCleanName(this.rootPackage)} must be installed`
        });
        
        // 2. At most one version of each package can be selected
        // NOT (X1 AND X2) = (NOT X1) OR (NOT X2)
        for (const [packageName, versions] of this.packageGroups.entries()) {
            if (versions.length > 1) {
                // For each pair of versions, at least one must be false
                for (let i = 0; i < versions.length; i++) {
                    for (let j = i + 1; j < versions.length; j++) {
                        const pkg1 = versions[i];
                        const pkg2 = versions[j];
                        clauses.push([[pkg1, false], [pkg2, false]]);
                        
                        // Original formula: NOT (X1 AND X2)
                        const cleanPkg1 = this.getCleanName(pkg1);
                        const cleanPkg2 = this.getCleanName(pkg2);
                        this.originalFormulas.push({
                            type: 'version_constraint',
                            formula: `¬(${cleanPkg1} ∧ ${cleanPkg2})`,
                            description: `Cannot select both ${cleanPkg1} and ${cleanPkg2}`
                        });
                    }
                }
            }
        }
        
        // 3. Dependency constraints: if package A is selected, its dependencies must be satisfied
        // A -> (B1 OR B2) becomes (NOT A) OR (B1 OR B2)
        for (const pkg of this.packages) {
            const dependencies = this.getDependencies(pkg);
            
            if (dependencies.length > 0) {
                // Group dependencies by package name
                const depGroups = new Map();
                for (const dep of dependencies) {
                    const depName = this.getPackageName(dep);
                    if (!depGroups.has(depName)) {
                        depGroups.set(depName, []);
                    }
                    depGroups.get(depName).push(dep);
                }
                
                // For each dependency group, create implication clause
                for (const [depName, depVersions] of depGroups.entries()) {
                    // NOT package OR (dep_version1 OR dep_version2 OR ...)
                    const clause = [[pkg, false]]; // NOT package
                    for (const dep of depVersions) {
                        clause.push([dep, true]); // OR all versions
                    }
                    clauses.push(clause);
                    
                    // Original formula: A -> (B1 OR B2 OR ...)
                    const cleanPackage = this.getCleanName(pkg);
                    let cleanDeps;
                    if (depVersions.length === 1) {
                        cleanDeps = this.getCleanName(depVersions[0]);
                    } else {
                        cleanDeps = depVersions.map(dep => this.getCleanName(dep)).join(' ∨ ');
                        cleanDeps = `(${cleanDeps})`;
                    }
                    
                    this.originalFormulas.push({
                        type: 'dependency',
                        formula: `${cleanPackage} → ${cleanDeps}`,
                        description: `If ${cleanPackage} is selected, then ${cleanDeps} must be selected`
                    });
                }
            }
        }
        
        return clauses;
    }

    getDependencies(packageNode) {
        // Get direct dependencies of a package
        const dependencies = [];
        for (const [source, target] of this.dependencyGraph.edges) {
            if (source === packageNode) {
                dependencies.push(target);
            }
        }
        return dependencies;
    }

    evaluateClause(clause, selectedPackages) {
        // Evaluate a single clause with given package selection
        for (const [pkg, required] of clause) {
            const isSelected = selectedPackages.has(pkg);
            if ((required && isSelected) || (!required && !isSelected)) {
                return true; // Clause is satisfied
            }
        }
        return false; // Clause is not satisfied
    }

    evaluateAllClauses(selectedPackages) {
        // Evaluate all clauses with given package selection
        const clauses = this.generateClauses();
        const results = [];
        
        for (const clause of clauses) {
            const satisfied = this.evaluateClause(clause, selectedPackages);
            results.push(satisfied);
        }
        
        const allSatisfied = results.every(result => result);
        return [allSatisfied, results];
    }

    getOriginalFormulas() {
        // Get the original formulas (call after generateClauses)
        return this.originalFormulas;
    }

    allSolutions(maxSolutions = 5) {
        // Find all valid solutions (simplified brute force for small examples)
        const solutions = [];
        const packages = this.packages;
        const n = packages.length;
        
        // Try all possible combinations (2^n possibilities)
        // This is not efficient for large graphs, but works for game scenarios
        const maxCombinations = Math.min(Math.pow(2, n), 10000); // Limit for performance
        
        for (let i = 0; i < maxCombinations && solutions.length < maxSolutions; i++) {
            const selectedPackages = new Set();
            
            // Convert number to binary and select packages accordingly
            for (let j = 0; j < n; j++) {
                if (i & (1 << j)) {
                    selectedPackages.add(packages[j]);
                }
            }
            
            // Check if this combination is valid
            const [allSatisfied, _] = this.evaluateAllClauses(selectedPackages);
            if (allSatisfied && selectedPackages.has(this.rootPackage)) {
                solutions.push(selectedPackages);
            }
        }
        
        return solutions;
    }

    // Helper method to get detailed clause information for UI
    getClauseDetails(selectedPackages) {
        const clauses = this.generateClauses();
        const originalFormulas = this.getOriginalFormulas();
        const details = [];
        
        for (let i = 0; i < clauses.length; i++) {
            const clause = clauses[i];
            const formula = originalFormulas[i];
            const satisfied = this.evaluateClause(clause, selectedPackages);
            
            details.push({
                index: i + 1,
                originalFormula: formula.formula,
                description: formula.description,
                satisfied: satisfied,
                type: formula.type,
                color: satisfied ? 'green' : 'red',
                status: satisfied ? '✓ True' : '✗ False'
            });
        }
        
        return details;
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BooleanSolver;
}
