import apiService from './apiService.js';

let networkData = {
    queries: {}, // Stores query data, e.g., { queryId: { name: "...", papers: { paperId1: {...}, paperId2: {...} } } }
    papers: {},  // Stores paper data, e.g., { paperId: { title: "...", authors: [...], ... } }
    connections: [] // Stores connection data for drawConnections
};

// Maps API query IDs to static HTML element IDs
const queryIdToHtmlId = {
    // This will be populated in initializeNetwork based on fetched data
    // e.g. fetchedQueryId1: 'query1', fetchedQueryId2: 'query2'
};

// Maps API paper IDs to static HTML element IDs
const paperIdToHtmlId = {
    // This will be populated in initializeNetwork based on fetched data
    // e.g. fetchedPaperId1: 'paper1', fetchedPaperId2: 'paper2', ...
};


function getNodeCenter(elementId) {
    const element = document.getElementById(elementId);
    if (!element) {
        console.error(`Element with ID ${elementId} not found for getNodeCenter.`);
        return null; // Return null or a default position
    }
    const rect = element.getBoundingClientRect();
    const containerRect = document.querySelector('.network-graph').getBoundingClientRect();
    
    return {
        x: rect.left + rect.width / 2 - containerRect.left,
        y: rect.top + rect.height / 2 - containerRect.top
    };
}

function drawConnections() {
    console.log("Drawing connections with data:", networkData.connections);
    networkData.connections.forEach(conn => {
        const fromHtmlId = conn.fromType === 'query' ? queryIdToHtmlId[conn.from] : (conn.fromType === 'paper' ? paperIdToHtmlId[conn.from] : conn.from);
        const toHtmlId = conn.toType === 'query' ? queryIdToHtmlId[conn.to] : (conn.toType === 'paper' ? paperIdToHtmlId[conn.to] : conn.to);

        if (!fromHtmlId) {
            console.error(`HTML ID for 'from' node ${conn.from} (type: ${conn.fromType}) not found.`);
            return;
        }
        if (!toHtmlId) {
            console.error(`HTML ID for 'to' node ${conn.to} (type: ${conn.toType}) not found.`);
            return;
        }

        const fromCenter = getNodeCenter(fromHtmlId);
        const toCenter = getNodeCenter(toHtmlId);
        const line = document.getElementById(conn.lineId);
        
        if (line && fromCenter && toCenter) {
            const midX = (fromCenter.x + toCenter.x) / 2;
            const midY = (fromCenter.y + toCenter.y) / 2;
            const controlOffset = 50;
            
            const path = `M ${fromCenter.x} ${fromCenter.y} Q ${midX + (Math.random() - 0.5) * controlOffset} ${midY - controlOffset} ${toCenter.x} ${toCenter.y}`;
            line.setAttribute('d', path);
            if (conn.style) {
                Object.assign(line.style, conn.style);
            }
        } else {
            if (!line) console.error(`Line element with ID ${conn.lineId} not found.`);
            if (!fromCenter) console.error(`Center for 'from' node ${fromHtmlId} could not be calculated.`);
            if (!toCenter) console.error(`Center for 'to' node ${toHtmlId} could not be calculated.`);
        }
    });
}

function renderNetwork() {
    // Ensure DOM elements are ready if manipulating them based on data
    // For now, this just calls drawing and effects
    drawConnections();
    addHoverEffects();
}

async function initializeNetwork() {
    try {
        const queryTree = await apiService.fetchQueryTreeData();
        console.log("Fetched query tree:", queryTree);

        // Clear previous data
        networkData.queries = {};
        networkData.papers = {};
        networkData.connections = [];
        
        // Assuming queryTree is an array of query nodes.
        // Example: [{ id: "queryId1", name: "Query 1 text", children: [...] }, ...]
        // Or if it's the whole tree structure: { root: { id: ..., name: ..., children: [...] } }
        // For now, let's assume it's an array of top-level queries.
        // The backend currently returns a flat list of queries.
        // We'll map them to 'query1' and 'query2' based on order for now.

        const queries = queryTree.queries || []; // Adjust based on actual API response structure

        let paperHtmlIdCounter = 1; // For assigning paper1, paper2, etc.

        for (let i = 0; i < queries.length; i++) {
            const query = queries[i];
            const queryHtmlId = `query${i + 1}`; // Assigns query1, query2

            if (!document.getElementById(queryHtmlId)) {
                console.warn(`HTML element ${queryHtmlId} not found. Skipping query:`, query.name);
                continue;
            }
            
            queryIdToHtmlId[query.id] = queryHtmlId;
            networkData.queries[query.id] = {
                id: query.id,
                name: query.name, // query.name is the actual query string
                htmlId: queryHtmlId,
                papers: {}
            };

            // Update the query text in the HTML
            const queryTextElement = document.querySelector(`#${queryHtmlId} .query-text`);
            if (queryTextElement) {
                queryTextElement.textContent = query.name;
            }
            const queryTitleElement = document.querySelector(`#${queryHtmlId} .query-title`);
             if (queryTitleElement) {
                // Example: "📚 AI Query 1: Reviews & Surveys" -> "📚 AI Query 1: [Actual Query Name from API]"
                // Or simply set it to query.name or a summarized version if too long
                queryTitleElement.textContent = `📚 AI Query ${i+1}: ${query.display_name || query.name.substring(0,30)+'...'}`;
            }


            // Connection from human-input to this query
            networkData.connections.push({
                from: 'human-input',
                to: query.id,
                toType: 'query',
                lineId: `line-input-${queryHtmlId}`, // e.g., line-input-query1
            });

            try {
                const searchResults = await apiService.searchPapers(query.name); // Use query.name (actual query string)
                console.log(`Fetched papers for query "${query.name}":`, searchResults);
                const papers = searchResults.papers || [];

                for (let j = 0; j < papers.length; j++) {
                    const paper = papers[j];
                    const paperHtmlId = `paper${paperHtmlIdCounter}`;

                    if (!document.getElementById(paperHtmlId)) {
                        console.warn(`HTML element ${paperHtmlId} not found. Skipping paper:`, paper.title);
                        continue; // Skip if no more HTML placeholders
                    }
                    
                    paperIdToHtmlId[paper.id] = paperHtmlId;
                    networkData.papers[paper.id] = { ...paper, htmlId: paperHtmlId, queryMatch: query.display_name || query.name }; // Store full paper object
                    networkData.queries[query.id].papers[paper.id] = networkData.papers[paper.id];
                    
                    // Update paper node in HTML
                    const paperElement = document.getElementById(paperHtmlId);
                    paperElement.querySelector('.paper-title').textContent = paper.title;
                    paperElement.querySelector('.paper-authors').textContent = paper.authors.join(', ');
                    paperElement.querySelector('.paper-date').textContent = paper.publication_date || new Date(paper.published).toLocaleDateString(); // Adjust field name
                    // Score might need to be fetched separately or be part of paper object
                    const relevanceBadge = paperElement.querySelector('.relevance-badge');
                    if (paper.score) { // Assuming score is part of paper object now
                        relevanceBadge.textContent = paper.score.toFixed(2);
                        if (paper.score >= 0.95) relevanceBadge.className = 'relevance-badge high';
                        else if (paper.score >= 0.85) relevanceBadge.className = 'relevance-badge medium';
                        else relevanceBadge.className = 'relevance-badge low'; // Add a 'low' class if needed
                    } else {
                         relevanceBadge.textContent = "N/A"; // Or fetch score
                         relevanceBadge.className = 'relevance-badge'; // Default class
                    }

                    // Connection from query to this paper
                    networkData.connections.push({
                        from: query.id,
                        fromType: 'query',
                        to: paper.id,
                        toType: 'paper',
                        lineId: `line-${queryHtmlId}-${paperHtmlId}`, // e.g., line-query1-paper1
                    });
                    paperHtmlIdCounter++;
                    if (paperHtmlIdCounter > 4) break; // Max 4 papers in current HTML
                }
            } catch (error) {
                console.error(`Error fetching papers for query "${query.name}":`, error);
            }
            if (paperHtmlIdCounter > 4 && i < queries.length -1) {
                 console.warn("Reached max paper elements in HTML, subsequent queries might not display papers.");
            }
        }
        
        // Add cross-connections if logic exists (e.g. paper relevant to multiple queries)
        // This part is complex with dynamic data and static HTML.
        // For now, we'll keep the original cross-connections if they map to loaded papers.
        // Example: if paper1 (from query1) and paper3 (from query2) are loaded.
        // This needs to be more robust if the API indicates cross-relevance.
        const p1 = Object.keys(paperIdToHtmlId).find(pid => paperIdToHtmlId[pid] === 'paper1');
        const p3 = Object.keys(paperIdToHtmlId).find(pid => paperIdToHtmlId[pid] === 'paper3');
        const q1 = Object.keys(queryIdToHtmlId).find(qid => queryIdToHtmlId[qid] === 'query1');
        const q2 = Object.keys(queryIdToHtmlId).find(qid => queryIdToHtmlId[qid] === 'query2');

        if (p1 && q2) {
             networkData.connections.push({
                from: q2, fromType: 'query', to: p1, toType: 'paper', lineId: 'line-q2-p1', style: { opacity: "0.3" }
            });
        }
        if (p3 && q1) {
            networkData.connections.push({
                from: q1, fromType: 'query', to: p3, toType: 'paper', lineId: 'line-q1-p3', style: { opacity: "0.3" }
            });
        }


        console.log("Final networkData for rendering:", networkData);
        renderNetwork();

    } catch (error) {
        console.error("Error initializing network:", error);
        // Display a user-friendly error message on the page if possible
        const container = document.querySelector('.network-container');
        if (container) {
            container.innerHTML = '<p style="color:red; text-align:center;">Failed to load research network data. Please try again later.</p>';
        }
    }
}


function addHoverEffects() {
    const nodes = document.querySelectorAll('.network-node');
    
    nodes.forEach(node => {
        node.addEventListener('mouseenter', () => {
            // Highlight connected lines
            const nodeId = node.id;
            const lines = document.querySelectorAll('.connection-line');
            
            lines.forEach(line => {
                const lineId = line.id;
                // Check if lineId is related to the current nodeId
                // Example: nodeId = 'paper1', lineId = 'line-query1-paper1' or 'line-q2-p1'
                // Example: nodeId = 'query1', lineId = 'line-input-query1' or 'line-query1-paper1'
                const parts = lineId.split('-');
                if (parts.includes(nodeId)) { // Simplified check
                    line.classList.add('active');
                }
            });
        });
        
        node.addEventListener('mouseleave', () => {
            // Remove highlights
            const lines = document.querySelectorAll('.connection-line');
            lines.forEach(line => line.classList.remove('active'));
        });
    });
}

function showPaperDetail(htmlPaperId) { // htmlPaperId is 'paper1', 'paper2', etc.
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('sidebar-content');
    
    // Find the actual paper ID from the htmlPaperId
    const paperId = Object.keys(paperIdToHtmlId).find(key => paperIdToHtmlId[key] === htmlPaperId);
    
    if (!paperId || !networkData.papers[paperId]) {
        console.error(`Paper data not found for HTML ID ${htmlPaperId} (mapped to ${paperId}).`);
        content.innerHTML = '<p>Paper details not available.</p>';
        sidebar.classList.add('open');
        return;
    }
    
    const paper = networkData.papers[paperId];
    
    content.innerHTML = `
        <div class="paper-detail-header">
            <h2 class="detail-title">${paper.title}</h2>
        </div>
        
        <div class="detail-metadata">
            <div class="metadata-grid">
                <div class="metadata-item">
                    <span class="metadata-label">Authors</span>
                    <span class="metadata-value">${paper.authors.join(', ')}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Publication Date</span>
                    <span class="metadata-value">${paper.publication_date || new Date(paper.published).toLocaleDateString()}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Relevance Score</span>
                    <span class="metadata-value">${paper.score ? paper.score.toFixed(2) : 'N/A'}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Categories</span>
                    <span class="metadata-value">${(paper.categories || []).join(', ')}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Found by Query</span>
                    <span class="metadata-value">${paper.queryMatch || 'N/A'}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">ArXiv Link</span>
                    <span class="metadata-value"><a href="${paper.url || paper.id}" target="_blank" style="color: #c8a882;">View Paper</a></span>
                </div>
            </div>
        </div>
        
        <div class="abstract-section">
            <h3 class="abstract-header">Abstract</h3>
            <div class="abstract-text">${paper.abstract}</div>
        </div>
        
        <div class="ai-analysis">
            <h3 class="analysis-header">AI Relevance Analysis</h3>
            <div class="analysis-text">${paper.ai_reasoning || paper.aiReasoning || 'N/A'}</div>
        </div>
    `;
    
    sidebar.classList.add('open');
}

function closeSidebar() {
    document.getElementById('sidebar').classList.remove('open');
}

// Initialize the network
document.addEventListener('DOMContentLoaded', function() {
    initializeNetwork();
});

// Redraw on window resize
window.addEventListener('resize', () => {
    // Debounce or throttle this if it becomes performance intensive
    setTimeout(renderNetwork, 100); 
});

// Close sidebar with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeSidebar();
    }
});

// Expose functions to global scope if they are called from HTML attributes (onclick)
window.showPaperDetail = showPaperDetail;
window.closeSidebar = closeSidebar;

// Expose for testing
window.networkData = networkData;
window.paperIdToHtmlId = paperIdToHtmlId;
