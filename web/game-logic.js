// Package Dependency Game Logic - JavaScript port of the Python game_logic.py

class PackageDependencyGame {
    constructor(dependencyGraph, rootPackage) {
        this.dependencyGraph = dependencyGraph;
        this.rootPackage = rootPackage;
        this.selectedPackages = new Set();
        
        // Validate inputs
        if (!dependencyGraph.nodes.includes(rootPackage)) {
            throw new Error(`Root package ${rootPackage} not found in dependency graph`);
        }
    }

    parsePackageNode(node) {
        // Parse package node to extract package name and version
        if (node.includes('-') && node.split('-').length === 2) {
            const parts = node.split('-');
            if (parts.length === 2 && parts[1].includes('.')) {
                return [parts[0], parts[1]];
            }
        } else if (node.includes('==')) {
            const parts = node.split('==');
            if (parts.length === 2) {
                return [parts[0], parts[1]];
            }
        }
        
        // Fallback: treat as package name with default version
        return [node, "1.0.0"];
    }

    getPackageName(node) {
        return this.parsePackageNode(node)[0];
    }

    getPackageVersion(node) {
        return this.parsePackageNode(node)[1];
    }

    getHierarchicalLayout() {
        // Create hierarchical layout for the graph visualization
        const levels = new Map();
        const visited = new Set();
        const inDegree = new Map();
        
        // Calculate in-degrees
        for (const node of this.dependencyGraph.nodes) {
            inDegree.set(node, 0);
        }
        
        for (const [source, target] of this.dependencyGraph.edges) {
            inDegree.set(target, inDegree.get(target) + 1);
        }
        
        // Topological sort to assign levels
        const queue = [];
        for (const [node, degree] of inDegree.entries()) {
            if (degree === 0) {
                levels.set(node, 0);
                queue.push(node);
            }
        }
        
        while (queue.length > 0) {
            const current = queue.shift();
            const currentLevel = levels.get(current);
            
            // Find all nodes that depend on current
            for (const [source, target] of this.dependencyGraph.edges) {
                if (source === current) {
                    const newDegree = inDegree.get(target) - 1;
                    inDegree.set(target, newDegree);
                    
                    if (newDegree === 0) {
                        levels.set(target, currentLevel + 1);
                        queue.push(target);
                    }
                }
            }
        }
        
        // Group packages by level and by package name
        const levelGroups = new Map();
        for (const [node, level] of levels.entries()) {
            if (!levelGroups.has(level)) {
                levelGroups.set(level, new Map());
            }
            
            const packageName = this.getPackageName(node);
            if (!levelGroups.get(level).has(packageName)) {
                levelGroups.get(level).set(packageName, []);
            }
            levelGroups.get(level).get(packageName).push(node);
        }
        
        // Calculate positions
        const positions = new Map();
        const ySpacing = 120;
        const xSpacing = 150;
        
        for (const [level, packageGroups] of levelGroups.entries()) {
            const y = level * ySpacing;
            
            let totalPackages = 0;
            for (const versions of packageGroups.values()) {
                totalPackages += versions.length;
            }
            
            const startX = -(totalPackages - 1) * xSpacing / 2;
            let xOffset = 0;
            
            for (const [packageName, versions] of Array.from(packageGroups.entries()).sort()) {
                for (let i = 0; i < versions.length; i++) {
                    const versionNode = versions[i];
                    const x = startX + xOffset * xSpacing;
                    positions.set(versionNode, [x, y + i * 30]); // Slight vertical offset for versions
                    xOffset++;
                }
            }
        }
        
        return positions;
    }

    selectPackage(packageNode) {
        // Select a package. Returns 1 if selection was successful, 0 if version conflict, -1 if error
        if (!this.dependencyGraph.nodes.includes(packageNode)) {
            return -1;
        }
        
        // Check if selecting this package would violate version constraints
        const packageName = this.getPackageName(packageNode);
        for (const selected of this.selectedPackages) {
            if (this.getPackageName(selected) === packageName) {
                // Cannot select two versions of the same package
                return 0;
            }
        }
        
        this.selectedPackages.add(packageNode);
        return 1;
    }

    deselectPackage(packageNode) {
        // Deselect a package. Returns true if deselection was successful
        if (this.selectedPackages.has(packageNode)) {
            this.selectedPackages.delete(packageNode);
            return true;
        }
        return false;
    }

    checkConstraints() {
        // Check all constraints and return list of violations
        const violations = [];
        
        // Check for multiple versions of same package
        const packageNames = new Map();
        for (const pkg of this.selectedPackages) {
            const name = this.getPackageName(pkg);
            if (!packageNames.has(name)) {
                packageNames.set(name, []);
            }
            packageNames.get(name).push(pkg);
        }
        
        for (const [name, versions] of packageNames.entries()) {
            if (versions.length > 1) {
                violations.push(`Multiple versions selected for ${name}: ${versions.join(', ')}`);
            }
        }
        
        // Check dependency satisfaction
        for (const pkg of this.selectedPackages) {
            const dependencies = this.getDependencies(pkg);
            for (const dep of dependencies) {
                const depName = this.getPackageName(dep);
                
                // Check if any version of this dependency is selected
                let depSatisfied = false;
                for (const selected of this.selectedPackages) {
                    if (this.getPackageName(selected) === depName) {
                        depSatisfied = true;
                        break;
                    }
                }
                
                if (!depSatisfied) {
                    violations.push(`${pkg} requires ${depName} but it's not selected`);
                }
            }
        }
        
        return violations;
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

    isValidSolution() {
        // Check if current selection is a valid solution using boolean solver
        try {
            const booleanSolver = new BooleanSolver(this.dependencyGraph, this.rootPackage);
            const [allSatisfied, _] = booleanSolver.evaluateAllClauses(this.selectedPackages);
            return allSatisfied;
        } catch (error) {
            console.error('Error checking solution validity:', error);
            return false;
        }
    }

    getGameState() {
        // Get current game state for serialization/debugging
        return {
            rootPackage: this.rootPackage,
            selectedPackages: Array.from(this.selectedPackages),
            constraintViolations: this.checkConstraints(),
            isValidSolution: this.isValidSolution(),
            totalPackages: this.dependencyGraph.nodes.length,
            totalDependencies: this.dependencyGraph.edges.length
        };
    }

    reset() {
        // Reset the game state
        this.selectedPackages.clear();
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PackageDependencyGame;
}
