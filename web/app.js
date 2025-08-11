// Main Application Logic - JavaScript

class PackageGameApp {
    constructor() {
        this.game = null;
        this.selectedScenario = 0;
        this.scenarios = GraphGenerator.generateSampleGraphs();
        this.gameWon = false;
        
        this.initializeDOM();
        this.setupEventListeners();
        this.loadScenario(0);
    }

    createBalloonAnimation() {
        // Remove any existing balloon canvas first
        const existingCanvas = document.getElementById('balloon-canvas');
        if (existingCanvas) {
            document.body.removeChild(existingCanvas);
        }
        
        const canvas = document.createElement('canvas');
        canvas.id = 'balloon-canvas';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.pointerEvents = 'none';
        canvas.style.zIndex = '9999';
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        document.body.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        const balloons = [];
        
        // Balloon colors
        const colors = [
            '#FF6B6B', // Red
            '#4ECDC4', // Teal
            '#45B7D1', // Blue
            '#96CEB4', // Green
            '#FFEAA7', // Yellow
            '#DDA0DD', // Plum
            '#98D8C8', // Mint
            '#F7DC6F'  // Light Yellow
        ];
        
        class Balloon {
            constructor(x, startY) {
                this.x = x + (Math.random() - 0.5) * 30; // Small random offset
                this.y = startY;
                this.targetY = -100; // Move above screen
                this.speed = Math.random() * 2 + 1.5; // Speed between 1.5-3.5
                this.color = colors[Math.floor(Math.random() * colors.length)];
                this.radius = Math.random() * 15 + 20; // Radius between 20-35
                this.swayAmount = Math.random() * 30 + 10; // Horizontal sway
                this.swaySpeed = Math.random() * 0.02 + 0.01; // Sway frequency
                this.time = Math.random() * Math.PI * 2; // Random start phase
                this.stringLength = Math.random() * 30 + 40; // String length
            }
            
            update() {
                this.y -= this.speed;
                this.time += this.swaySpeed;
                
                // Add horizontal sway
                this.currentX = this.x + Math.sin(this.time) * this.swayAmount;
            }
            
            draw() {
                if (this.y > -100) {
                    // Draw balloon string
                    ctx.strokeStyle = '#8B4513';
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.moveTo(this.currentX, this.y + this.radius);
                    ctx.lineTo(this.currentX, this.y + this.radius + this.stringLength);
                    ctx.stroke();
                    
                    // Draw balloon
                    ctx.fillStyle = this.color;
                    ctx.beginPath();
                    // Draw balloon shape (circle with slight oval at bottom)
                    ctx.ellipse(this.currentX, this.y, this.radius * 0.8, this.radius, 0, 0, Math.PI * 2);
                    ctx.fill();
                    
                    // Add highlight to balloon
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                    ctx.beginPath();
                    ctx.ellipse(this.currentX - this.radius * 0.3, this.y - this.radius * 0.3, this.radius * 0.3, this.radius * 0.4, 0, 0, Math.PI * 2);
                    ctx.fill();
                    
                    // Draw balloon tie
                    ctx.fillStyle = '#8B4513';
                    ctx.beginPath();
                    ctx.ellipse(this.currentX, this.y + this.radius * 0.9, 3, 6, 0, 0, Math.PI * 2);
                    ctx.fill();
                }
            }
            
            isOffScreen() {
                return this.y < this.targetY;
            }
        }
        
        // Create balloons at random positions along the bottom
        const numBalloons = 8;
        for (let i = 0; i < numBalloons; i++) {
            const x = (canvas.width / (numBalloons + 1)) * (i + 1);
            const startY = canvas.height + Math.random() * 50 + 50; // Start below screen
            balloons.push(new Balloon(x, startY));
            
            // Stagger balloon release
            balloons[i].delay = i * 200;
            balloons[i].released = false;
        }
        
        let animationTime = 0;
        
        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            animationTime += 16; // Approximate frame time
            
            let balloonsOnScreen = 0;
            
            // Update and draw balloons
            for (let i = balloons.length - 1; i >= 0; i--) {
                const balloon = balloons[i];
                
                // Check if balloon should be released
                if (!balloon.released && animationTime >= balloon.delay) {
                    balloon.released = true;
                }
                
                if (balloon.released) {
                    balloon.update();
                    balloon.draw();
                    
                    if (!balloon.isOffScreen()) {
                        balloonsOnScreen++;
                    } else {
                        balloons.splice(i, 1);
                    }
                }
            }
            
            // Continue animation while balloons are on screen
            if (balloonsOnScreen > 0 || balloons.some(b => !b.released)) {
                requestAnimationFrame(animate);
            } else {
                // Remove canvas when animation is done
                const canvasToRemove = document.getElementById('balloon-canvas');
                if (canvasToRemove && canvasToRemove.parentNode) {
                    canvasToRemove.parentNode.removeChild(canvasToRemove);
                }
            }
        }
        
        animate();
        
        // Auto-remove after 10 seconds as a safety measure
        setTimeout(() => {
            const canvasToRemove = document.getElementById('balloon-canvas');
            if (canvasToRemove && canvasToRemove.parentNode) {
                canvasToRemove.parentNode.removeChild(canvasToRemove);
            }
        }, 10000);
    }

    initializeDOM() {
        // Initialize scenario selector
        const scenarioSelect = document.getElementById('scenario-select');
        this.scenarios.forEach((scenario, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = `Scenario ${index + 1}: ${scenario.name}`;
            scenarioSelect.appendChild(option);
        });
    }

    setupEventListeners() {
        // Scenario selection
        document.getElementById('scenario-select').addEventListener('change', (e) => {
            this.loadScenario(parseInt(e.target.value));
        });

        // Reset button
        document.getElementById('reset-btn').addEventListener('click', () => {
            this.resetGame();
        });

        // Modal controls
        this.setupModalControls();

        // Action buttons
        document.getElementById('show-hints-btn').addEventListener('click', () => {
            this.showBooleanHints();
        });

        document.getElementById('show-solution-btn').addEventListener('click', () => {
            this.showSolutions();
        });
    }

    setupModalControls() {
        const modals = document.querySelectorAll('.modal');
        const closes = document.querySelectorAll('.close');

        // Close modal when clicking X
        closes.forEach(close => {
            close.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                if (modal) {
                    modal.style.display = 'none';
                }
            });
        });

        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            modals.forEach(modal => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        });
    }

    loadScenario(scenarioIndex) {
        this.selectedScenario = scenarioIndex;
        const scenario = this.scenarios[scenarioIndex];
        this.gameWon = false;
        
        try {
            this.game = new PackageDependencyGame(scenario.graph, scenario.root);
            this.updateDisplay();
        } catch (error) {
            console.error('Failed to load scenario:', error);
            this.showError('Failed to load scenario. Please try again.');
        }
    }

    resetGame() {
        if (this.game) {
            this.gameWon = false;
            this.game.reset();
            this.updateDisplay();
        }
    }

    updateDisplay() {
        if (!this.game) return;

        this.updateGraph();
        this.updatePackageButtons();
        this.updateSelectedPackages();
        this.updateGameStatus();
    }

    updateGraph() {
        const container = document.getElementById('graph-container');
        const svg = d3.select('#dependency-graph');
        
        // Clear existing content
        svg.selectAll('*').remove();
        
        const containerRect = container.getBoundingClientRect();
        const width = containerRect.width;
        const height = containerRect.height;
        
        svg.attr('width', width).attr('height', height);
        
        // Create zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {
                g.attr('transform', event.transform);
            });
        
        svg.call(zoom);
        
        // Create main group for zooming
        const g = svg.append('g');
        
        // Create arrow marker
        svg.append('defs').append('marker')
            .attr('id', 'arrowhead')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 9) // Adjusted to align better with border endpoints
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', '#999');
        
        // Get graph data
        const nodes = this.game.dependencyGraph.nodes.map(node => ({
            id: node,
            name: this.game.getPackageName(node),
            version: this.game.getPackageVersion(node),
            selected: this.game.selectedPackages.has(node),
            isRoot: node === this.game.rootPackage
        }));
        
        const links = this.game.dependencyGraph.edges.map(([source, target]) => ({
            source: source,
            target: target,
            satisfied: this.game.selectedPackages.has(source) && this.game.selectedPackages.has(target)
        }));
        
        // Calculate hierarchical positions
        const positions = this.calculateHierarchicalPositions(nodes, links, width, height);
        
        // Set fixed positions for nodes
        nodes.forEach(node => {
            const pos = positions[node.id];
            if (pos) {
                node.fx = pos.x;
                node.fy = pos.y;
            }
        });
        
        // Create links
        const link = g.append('g')
            .selectAll('path')
            .data(links)
            .enter().append('path')
            .attr('class', d => `link ${d.satisfied ? 'satisfied' : ''}`)
            .attr('stroke', d => d.satisfied ? '#28a745' : '#999')
            .attr('stroke-width', d => d.satisfied ? 3 : 2)
            .attr('fill', 'none')
            .attr('marker-end', 'url(#arrowhead)')
            .attr('d', d => {
                const sourcePos = positions[d.source];
                const targetPos = positions[d.target];
                if (!sourcePos || !targetPos) return '';
                
                // Calculate curved path to avoid overlapping nodes
                return this.createCurvedPath(sourcePos, targetPos, positions, nodes, d.source, d.target);
            });
        
        // Create nodes
        const node = g.append('g')
            .selectAll('circle')
            .data(nodes)
            .enter().append('circle')
            .attr('class', d => `node ${d.selected ? 'selected' : ''} ${d.isRoot ? 'root' : ''}`)
            .attr('r', 25)
            .attr('fill', d => {
                if (d.selected) return '#28a745'; // Green fill for selected nodes
                return '#ffffff'; // White fill for all unselected nodes
            })
            .attr('fill-opacity', 0.85) // Make nodes translucent
            .attr('stroke', d => {
                if (d.isRoot) return '#dc3545'; // Red border for root node
                return '#000000'; // Black border for all other nodes
            })
            .attr('stroke-width', d => d.isRoot ? 3 : 2)
            .style('cursor', 'pointer')
            .attr('cx', d => positions[d.id] ? positions[d.id].x : 0)
            .attr('cy', d => positions[d.id] ? positions[d.id].y : 0)
            .on('click', (event, d) => {
                this.togglePackageSelection(d.id);
            });
        
        // Add labels
        const labels = g.append('g')
            .selectAll('g')
            .data(nodes)
            .enter().append('g')
            .attr('class', 'node-label-group')
            .attr('transform', d => `translate(${positions[d.id] ? positions[d.id].x : 0}, ${positions[d.id] ? positions[d.id].y : 0})`)
            .style('pointer-events', 'none');
        
        // Add package name
        labels.append('text')
            .attr('class', 'node-label')
            .attr('text-anchor', 'middle')
            .attr('dy', '-0.2em')
            .style('font-size', '11px')
            .style('font-weight', 'bold')
            .style('fill', '#2c3e50')
            .text(d => d.name);
        
        // Add version
        labels.append('text')
            .attr('class', 'node-label')
            .attr('text-anchor', 'middle')
            .attr('dy', '0.8em')
            .style('font-size', '9px')
            .style('font-weight', 'normal')
            .style('fill', '#6c757d')
            .text(d => `v${d.version}`);
        
        // Add zoom controls
        this.addZoomControls(svg, zoom);
    }

    calculateHierarchicalPositions(nodes, links, width, height) {
        const positions = {};
        const levels = new Map();
        const visited = new Set();
        const inDegree = new Map();
        
        // Initialize in-degrees
        for (const node of nodes) {
            inDegree.set(node.id, 0);
        }
        
        // Calculate in-degrees
        for (const link of links) {
            inDegree.set(link.target, (inDegree.get(link.target) || 0) + 1);
        }
        
        // Find root nodes (nodes with no incoming edges)
        const queue = [];
        for (const [nodeId, degree] of inDegree.entries()) {
            if (degree === 0) {
                levels.set(nodeId, 0);
                queue.push(nodeId);
            }
        }
        
        // Topological sort to assign levels
        while (queue.length > 0) {
            const currentId = queue.shift();
            const currentLevel = levels.get(currentId);
            
            // Find all nodes that depend on current node
            for (const link of links) {
                if (link.source === currentId) {
                    const targetLevel = Math.max(levels.get(link.target) || 0, currentLevel + 1);
                    levels.set(link.target, targetLevel);
                    
                    const newDegree = inDegree.get(link.target) - 1;
                    inDegree.set(link.target, newDegree);
                    
                    if (newDegree === 0 && !visited.has(link.target)) {
                        queue.push(link.target);
                        visited.add(link.target);
                    }
                }
            }
        }
        
        // Group nodes by level and package name
        const levelGroups = new Map();
        for (const node of nodes) {
            const level = levels.get(node.id) || 0;
            if (!levelGroups.has(level)) {
                levelGroups.set(level, new Map());
            }
            
            const packageName = node.name;
            if (!levelGroups.get(level).has(packageName)) {
                levelGroups.get(level).set(packageName, []);
            }
            levelGroups.get(level).get(packageName).push(node);
        }
        
        // Calculate positions
        const maxLevel = Math.max(...levels.values());
        const levelHeight = Math.max(80, (height - 100) / (maxLevel + 1));
        const margin = 50;
        
        for (const [level, packageGroups] of levelGroups.entries()) {
            const y = margin + level * levelHeight;
            
            // Calculate total width needed for this level
            let totalPackages = 0;
            for (const versions of packageGroups.values()) {
                totalPackages += versions.length;
            }
            
            const packageWidth = Math.max(100, (width - 2 * margin) / totalPackages);
            let xOffset = margin;
            
            for (const [packageName, versions] of Array.from(packageGroups.entries()).sort()) {
                for (let i = 0; i < versions.length; i++) {
                    const node = versions[i];
                    const x = xOffset + packageWidth / 2 + i * Math.min(60, packageWidth / versions.length);
                    positions[node.id] = { x, y };
                }
                xOffset += packageWidth;
            }
        }
        
        return positions;
    }

    addZoomControls(svg, zoom) {
        // Add zoom control buttons
        const controlsGroup = svg.append('g')
            .attr('class', 'zoom-controls')
            .attr('transform', 'translate(10, 10)');
        
        // Zoom in button
        const zoomInButton = controlsGroup.append('g')
            .attr('class', 'zoom-button')
            .style('cursor', 'pointer');
        
        zoomInButton.append('rect')
            .attr('width', 30)
            .attr('height', 30)
            .attr('fill', '#f8f9fa')
            .attr('stroke', '#dee2e6')
            .attr('stroke-width', 1)
            .attr('rx', 4);
        
        zoomInButton.append('text')
            .attr('x', 15)
            .attr('y', 20)
            .attr('text-anchor', 'middle')
            .attr('font-size', '16px')
            .attr('font-weight', 'bold')
            .attr('fill', '#495057')
            .text('+');
        
        zoomInButton.on('click', () => {
            svg.transition().duration(300).call(
                zoom.scaleBy, 1.5
            );
        });
        
        // Zoom out button
        const zoomOutButton = controlsGroup.append('g')
            .attr('class', 'zoom-button')
            .attr('transform', 'translate(0, 35)')
            .style('cursor', 'pointer');
        
        zoomOutButton.append('rect')
            .attr('width', 30)
            .attr('height', 30)
            .attr('fill', '#f8f9fa')
            .attr('stroke', '#dee2e6')
            .attr('stroke-width', 1)
            .attr('rx', 4);
        
        zoomOutButton.append('text')
            .attr('x', 15)
            .attr('y', 20)
            .attr('text-anchor', 'middle')
            .attr('font-size', '16px')
            .attr('font-weight', 'bold')
            .attr('fill', '#495057')
            .text('−');
        
        zoomOutButton.on('click', () => {
            svg.transition().duration(300).call(
                zoom.scaleBy, 0.67
            );
        });
        
        // Reset zoom button
        const resetButton = controlsGroup.append('g')
            .attr('class', 'zoom-button')
            .attr('transform', 'translate(0, 70)')
            .style('cursor', 'pointer');
        
        resetButton.append('rect')
            .attr('width', 30)
            .attr('height', 30)
            .attr('fill', '#f8f9fa')
            .attr('stroke', '#dee2e6')
            .attr('stroke-width', 1)
            .attr('rx', 4);
        
        resetButton.append('text')
            .attr('x', 15)
            .attr('y', 20)
            .attr('text-anchor', 'middle')
            .attr('font-size', '12px')
            .attr('font-weight', 'bold')
            .attr('fill', '#495057')
            .text('⌂');
        
        resetButton.on('click', () => {
            svg.transition().duration(500).call(
                zoom.transform,
                d3.zoomIdentity
            );
        });
    }

    createCurvedPath(source, target, allPositions, nodes, sourceId, targetId) {
        // Calculate border intersection points instead of using center points
        const nodeRadius = 25;
        const sourceCenter = source;
        const targetCenter = target;
        
        // Calculate the direction vector from source to target
        const dx = targetCenter.x - sourceCenter.x;
        const dy = targetCenter.y - sourceCenter.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance === 0) return `M ${sourceCenter.x} ${sourceCenter.y} L ${targetCenter.x} ${targetCenter.y}`;
        
        // Normalize the direction vector
        const unitX = dx / distance;
        const unitY = dy / distance;
        
        // Calculate edge start and end points on node borders
        const sourceEdge = {
            x: sourceCenter.x + unitX * nodeRadius,
            y: sourceCenter.y + unitY * nodeRadius
        };
        
        const targetEdge = {
            x: targetCenter.x - unitX * nodeRadius,
            y: targetCenter.y - unitY * nodeRadius
        };
        
        // Now check for collision detection using the edge points
        const buffer = 5; // Additional buffer space
        const totalRadius = nodeRadius + buffer;
        
        // Check if we need to curve around any nodes
        let needsCurve = false;
        let conflictingNodes = [];
        
        for (const node of nodes) {
            const nodePos = allPositions[node.id];
            if (!nodePos || node.id === sourceId || node.id === targetId) continue;
            
            // Check if this node is close to the straight line path
            const distanceFromLine = this.distanceFromPointToLine(nodePos, sourceEdge, targetEdge);
            if (distanceFromLine < totalRadius) {
                needsCurve = true;
                conflictingNodes.push(nodePos);
            }
        }
        
        if (!needsCurve) {
            // Simple straight line from border to border
            return `M ${sourceEdge.x} ${sourceEdge.y} L ${targetEdge.x} ${targetEdge.y}`;
        }
        
        // Create a curved path to avoid conflicting nodes
        const midX = (sourceEdge.x + targetEdge.x) / 2;
        const midY = (sourceEdge.y + targetEdge.y) / 2;
        
        // Calculate perpendicular offset
        const edgeDx = targetEdge.x - sourceEdge.x;
        const edgeDy = targetEdge.y - sourceEdge.y;
        const edgeLength = Math.sqrt(edgeDx * edgeDx + edgeDy * edgeDy);
        
        if (edgeLength === 0) return `M ${sourceEdge.x} ${sourceEdge.y} L ${targetEdge.x} ${targetEdge.y}`;
        
        // Perpendicular direction (normalized)
        const perpX = -edgeDy / edgeLength;
        const perpY = edgeDx / edgeLength;
        
        // Determine which direction to curve (try both and pick the one with less conflicts)
        const curveDistance = Math.max(50, totalRadius * 2);
        
        // Try curving to the right
        const controlPointRight = {
            x: midX + perpX * curveDistance,
            y: midY + perpY * curveDistance
        };
        
        // Try curving to the left  
        const controlPointLeft = {
            x: midX - perpX * curveDistance,
            y: midY - perpY * curveDistance
        };
        
        // Check which control point has fewer conflicts
        const conflictsRight = this.countNearbyNodes(controlPointRight, conflictingNodes, totalRadius);
        const conflictsLeft = this.countNearbyNodes(controlPointLeft, conflictingNodes, totalRadius);
        
        const controlPoint = conflictsLeft < conflictsRight ? controlPointLeft : controlPointRight;
        
        // Create quadratic Bezier curve from border to border
        return `M ${sourceEdge.x} ${sourceEdge.y} Q ${controlPoint.x} ${controlPoint.y} ${targetEdge.x} ${targetEdge.y}`;
    }
    
    distanceFromPointToLine(point, lineStart, lineEnd) {
        // Calculate distance from point to line segment
        const A = point.x - lineStart.x;
        const B = point.y - lineStart.y;
        const C = lineEnd.x - lineStart.x;
        const D = lineEnd.y - lineStart.y;
        
        const dot = A * C + B * D;
        const lenSq = C * C + D * D;
        
        if (lenSq === 0) {
            // Line start and end are the same point
            return Math.sqrt(A * A + B * B);
        }
        
        let param = dot / lenSq;
        
        let xx, yy;
        
        if (param < 0) {
            xx = lineStart.x;
            yy = lineStart.y;
        } else if (param > 1) {
            xx = lineEnd.x;
            yy = lineEnd.y;
        } else {
            xx = lineStart.x + param * C;
            yy = lineStart.y + param * D;
        }
        
        const dx = point.x - xx;
        const dy = point.y - yy;
        return Math.sqrt(dx * dx + dy * dy);
    }
    
    countNearbyNodes(point, nodePositions, radius) {
        let count = 0;
        for (const nodePos of nodePositions) {
            const distance = Math.sqrt(
                (point.x - nodePos.x) ** 2 + (point.y - nodePos.y) ** 2
            );
            if (distance < radius) count++;
        }
        return count;
    }

    updatePackageButtons() {
        const container = document.getElementById('package-buttons');
        container.innerHTML = '';
        
        const packages = [...this.game.dependencyGraph.nodes].sort();
        
        packages.forEach(pkg => {
            const [name, version] = this.game.parsePackageNode(pkg);
            const isSelected = this.game.selectedPackages.has(pkg);
            const isRoot = pkg === this.game.rootPackage;
            
            const button = document.createElement('button');
            button.className = `package-btn ${isSelected ? 'selected' : ''} ${isRoot ? 'root' : ''}`;
            button.textContent = `${isSelected ? '✓' : '○'} ${name} v${version}`;
            button.onclick = () => this.togglePackageSelection(pkg);
            
            container.appendChild(button);
        });
    }

    updateSelectedPackages() {
        const container = document.getElementById('selected-packages');
        
        if (this.game.selectedPackages.size === 0) {
            container.innerHTML = '<em>None</em>';
        } else {
            const selected = Array.from(this.game.selectedPackages).sort();
            container.textContent = selected.join(', ');
        }
    }

    updateGameStatus() {
        const statusDiv = document.getElementById('game-status');
        const isValid = this.game.isValidSolution();
        
        statusDiv.className = 'status-message';
        
        if (isValid) {
            statusDiv.classList.add('status-success');
            statusDiv.innerHTML = '🎉 Congratulations! You\'ve successfully resolved all dependencies!';
            // Add celebration animation
            statusDiv.classList.add('celebration');
            setTimeout(() => statusDiv.classList.remove('celebration'), 600);
            
            // Trigger balloon animation if this is a new success (not already won)
            if (!this.gameWon) {
                this.gameWon = true;
                // Start balloon animation slightly after celebration starts
                setTimeout(() => this.createBalloonAnimation(), 300);
            }
        } else {
            // Reset the win state if solution becomes invalid
            this.gameWon = false;
            
            if (this.game.selectedPackages.size > 0) {
                statusDiv.classList.add('status-error');
                statusDiv.innerHTML = '❌ Current selection does not satisfy all constraints. Keep trying!';
            } else {
                statusDiv.classList.add('status-info');
                statusDiv.innerHTML = 'Start by selecting some packages to begin.';
            }
        }
    }

    togglePackageSelection(packageNode) {
        if (this.game.selectedPackages.has(packageNode)) {
            this.game.deselectPackage(packageNode);
        } else {
            const result = this.game.selectPackage(packageNode);
            if (result === 0) {
                this.showVersionConflict();
                return;
            } else if (result === -1) {
                this.showError('Failed to select package. Please try again.');
                return;
            }
        }
        
        this.updateDisplay();
    }

    showBooleanHints() {
        try {
            const booleanSolver = new BooleanSolver(this.game.dependencyGraph, this.game.rootPackage);
            const clauseDetails = booleanSolver.getClauseDetails(this.game.selectedPackages);
            
            const modal = document.getElementById('hints-modal');
            const content = document.getElementById('hints-content');
            
            // Check overall satisfaction
            const allSatisfied = clauseDetails.every(clause => clause.satisfied);
            const overallStatus = allSatisfied ? 
                '✓ ALL CONSTRAINTS SATISFIED' : 
                '✗ SOME CONSTRAINTS VIOLATED. CHECK THEM BELOW';
            const overallColor = allSatisfied ? 'green' : 'red';
            
            let html = `
                <h4 style="color: ${overallColor};">${overallStatus}</h4>
                <p>The dependency constraints are converted to boolean clauses. All must be True:</p>
            `;
            
            // Group clauses by type
            const rootClauses = clauseDetails.filter(c => c.type === 'root');
            const versionClauses = clauseDetails.filter(c => c.type === 'version_constraint');
            const dependencyClauses = clauseDetails.filter(c => c.type === 'dependency');
            
            // Create tabs
            html += `
                <div class="tabs">
                    <button class="tab active" data-tab="root">Root Constraints</button>
                    <button class="tab" data-tab="version">Version Constraints</button>
                    <button class="tab" data-tab="dependency">Dependency Constraints</button>
                </div>
            `;
            
            // Root constraints
            html += `<div class="tab-content active" id="root-tab">`;
            if (rootClauses.length > 0) {
                html += '<h4>Root Package Constraint:</h4>';
                rootClauses.forEach(clause => {
                    html += `
                        <div class="clause-item ${clause.satisfied ? 'clause-satisfied' : 'clause-violated'}">
                            <div class="clause-formula">Term ${clause.index}: ${clause.originalFormula}</div>
                            <div class="clause-status ${clause.satisfied ? 'satisfied' : 'violated'}">${clause.status}</div>
                        </div>
                    `;
                });
            }
            html += '</div>';
            
            // Version constraints
            html += `<div class="tab-content" id="version-tab">`;
            if (versionClauses.length > 0) {
                html += '<h4>Version Uniqueness Constraints (at most one version per package):</h4>';
                versionClauses.forEach(clause => {
                    html += `
                        <div class="clause-item ${clause.satisfied ? 'clause-satisfied' : 'clause-violated'}">
                            <div class="clause-formula">Term ${clause.index}: ${clause.originalFormula}</div>
                            <div class="clause-status ${clause.satisfied ? 'satisfied' : 'violated'}">${clause.status}</div>
                        </div>
                    `;
                });
            }
            html += '</div>';
            
            // Dependency constraints
            html += `<div class="tab-content" id="dependency-tab">`;
            if (dependencyClauses.length > 0) {
                html += '<h4>Dependency Implications (if package selected, dependencies must be satisfied):</h4>';
                dependencyClauses.forEach(clause => {
                    html += `
                        <div class="clause-item ${clause.satisfied ? 'clause-satisfied' : 'clause-violated'}">
                            <div class="clause-formula">Term ${clause.index}: ${clause.originalFormula}</div>
                            <div class="clause-status ${clause.satisfied ? 'satisfied' : 'violated'}">${clause.status}</div>
                        </div>
                    `;
                });
            }
            html += '</div>';
            
            content.innerHTML = html;
            
            // Setup tab functionality
            const tabs = content.querySelectorAll('.tab');
            const tabContents = content.querySelectorAll('.tab-content');
            
            tabs.forEach(tab => {
                tab.addEventListener('click', () => {
                    // Remove active class from all tabs and contents
                    tabs.forEach(t => t.classList.remove('active'));
                    tabContents.forEach(tc => tc.classList.remove('active'));
                    
                    // Add active class to clicked tab and corresponding content
                    tab.classList.add('active');
                    const tabId = tab.getAttribute('data-tab') + '-tab';
                    document.getElementById(tabId).classList.add('active');
                });
            });
            
            modal.style.display = 'block';
        } catch (error) {
            console.error('Error showing boolean hints:', error);
            this.showError('Failed to generate boolean hints.');
        }
    }

    showSolutions() {
        try {
            const booleanSolver = new BooleanSolver(this.game.dependencyGraph, this.game.rootPackage);
            const solutions = booleanSolver.allSolutions(5);
            
            const modal = document.getElementById('solution-modal');
            const content = document.getElementById('solution-content');
            
            if (solutions.length === 0) {
                content.innerHTML = '<p class="status-error">The constraints are unsatisfiable. No valid solution exists for this scenario.</p>';
            } else {
                let html = `
                    <p>Showing ${solutions.length} solution(s):</p>
                    <div style="margin-top: 1rem;">
                `;
                
                solutions.forEach((solution, index) => {
                    const formatted = Array.from(solution)
                        .sort()
                        .map(pkg => {
                            const [name, version] = this.game.parsePackageNode(pkg);
                            return `${name} v${version}`;
                        });
                    
                    html += `<div style="margin-bottom: 1rem; padding: 1rem; background-color: #f8f9fa; border-radius: 6px;">
                        <strong>Solution ${index + 1}:</strong> ${formatted.join(', ')}
                    </div>`;
                });
                
                html += `</div>
                    <div class="info-box" style="margin-top: 1rem;">
                        <strong>ℹ️ Note:</strong> Here, we show 5 possible solutions at max. Feel free to find more solutions.
                    </div>
                `;
                
                content.innerHTML = html;
            }
            
            modal.style.display = 'block';
        } catch (error) {
            console.error('Error showing solutions:', error);
            this.showError('Failed to generate solutions.');
        }
    }

    showVersionConflict() {
        const modal = document.getElementById('conflict-modal');
        modal.style.display = 'block';
    }

    showError(message) {
        alert('Error: ' + message);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PackageGameApp();
});
