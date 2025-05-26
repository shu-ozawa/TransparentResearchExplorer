import apiService from './apiService.js';

let networkData = {
    queries: {}, // Stores query data
    papers: {},  // Stores paper data
    connections: [], // Stores connection data for drawConnections
    researchGoal: '', // Stores the research goal from AI interpretation
};

// Maps API query IDs to static HTML element IDs
const queryIdToHtmlId = {};

// Maps API paper IDs to static HTML element IDs
const paperIdToHtmlId = {};

function getNodeCenter(elementId) {
    const element = document.getElementById(elementId);
    if (!element) {
        console.error(`Element with ID ${elementId} not found for getNodeCenter.`);
        return null;
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
    drawConnections();
    addHoverEffects();
}

async function initializeNetwork(naturalLanguageQuery = "深層学習を使った画像認識の最新手法") {
    try {
        const searchResponse = await apiService.searchResearchTree(naturalLanguageQuery);
        console.log("Search response:", searchResponse);

        // Clear previous data
        networkData.queries = {};
        networkData.papers = {};
        networkData.connections = [];
        networkData.researchGoal = searchResponse.research_goal;
        
        // Update research goal display if exists
        const goalElement = document.querySelector('.research-goal');
        if (goalElement) {
            goalElement.textContent = networkData.researchGoal;
        }

        let paperHtmlIdCounter = 1;

        searchResponse.query_nodes.forEach((queryNode, index) => {
            const queryHtmlId = `query${index + 1}`;

            if (!document.getElementById(queryHtmlId)) {
                console.warn(`HTML element ${queryHtmlId} not found. Skipping query:`, queryNode.query);
                return;
            }
            
            const queryId = `query-${index}`; // Generate a unique ID for the query
            queryIdToHtmlId[queryId] = queryHtmlId;
            networkData.queries[queryId] = {
                id: queryId,
                name: queryNode.query,
                description: queryNode.description,
                htmlId: queryHtmlId,
                papers: {}
            };

            // Update query display in HTML
            const queryTextElement = document.querySelector(`#${queryHtmlId} .query-text`);
            if (queryTextElement) {
                queryTextElement.textContent = queryNode.query;
            }
            const queryTitleElement = document.querySelector(`#${queryHtmlId} .query-title`);
            if (queryTitleElement) {
                queryTitleElement.textContent = `📚 検索クエリ ${index+1}: ${queryNode.description}`;
            }

            // Connection from human-input to this query
            networkData.connections.push({
                from: 'human-input',
                to: queryId,
                toType: 'query',
                lineId: `line-input-${queryHtmlId}`,
            });

            // Process papers for this query
            queryNode.papers.forEach((paper, paperIndex) => {
                const paperHtmlId = `paper${paperHtmlIdCounter}`;
                if (!document.getElementById(paperHtmlId)) {
                    console.warn(`HTML element ${paperHtmlId} not found. Skipping paper:`, paper.title);
                    return;
                }

                const paperId = paper.arxiv_id;
                paperIdToHtmlId[paperId] = paperHtmlId;
                networkData.papers[paperId] = {
                    ...paper,
                    htmlId: paperHtmlId,
                    queryMatch: queryNode.description
                };
                networkData.queries[queryId].papers[paperId] = networkData.papers[paperId];

                // Update paper display in HTML
                const paperElement = document.getElementById(paperHtmlId);
                paperElement.querySelector('.paper-title').textContent = paper.title;
                paperElement.querySelector('.paper-authors').textContent = paper.authors.join(', ');
                paperElement.querySelector('.paper-date').textContent = new Date(paper.published_date).toLocaleDateString();
                
                const relevanceBadge = paperElement.querySelector('.relevance-badge');
                if (paper.relevance_score !== undefined) {
                    relevanceBadge.textContent = paper.relevance_score.toFixed(2);
                    if (paper.relevance_score >= 0.95) relevanceBadge.className = 'relevance-badge high';
                    else if (paper.relevance_score >= 0.85) relevanceBadge.className = 'relevance-badge medium';
                    else relevanceBadge.className = 'relevance-badge low';
                } else {
                    relevanceBadge.textContent = "N/A";
                    relevanceBadge.className = 'relevance-badge';
                }

                // Connection from query to this paper
                networkData.connections.push({
                    from: queryId,
                    fromType: 'query',
                    to: paperId,
                    toType: 'paper',
                    lineId: `line-${queryHtmlId}-${paperHtmlId}`,
                });

                paperHtmlIdCounter++;
            });
        });

        console.log("Final networkData for rendering:", networkData);
        renderNetwork();

    } catch (error) {
        console.error("Error initializing network:", error);
        const container = document.querySelector('.network-container');
        if (container) {
            container.innerHTML = '<p style="color:red; text-align:center;">研究ネットワークデータの読み込みに失敗しました。後でもう一度お試しください。</p>';
        }
    }
}

function showPaperDetail(htmlPaperId) {
    const paperId = Object.keys(paperIdToHtmlId).find(id => paperIdToHtmlId[id] === htmlPaperId);
    if (!paperId || !networkData.papers[paperId]) {
        console.error(`Paper data not found for HTML ID: ${htmlPaperId}`);
        return;
    }

    const paper = networkData.papers[paperId];
    const sidebar = document.querySelector('.paper-detail-sidebar');
    
    if (sidebar) {
        const content = `
            <div class="paper-detail-content">
                <button onclick="closeSidebar()" class="close-button">×</button>
                <h2>${paper.title}</h2>
                <p class="authors">${paper.authors.join(', ')}</p>
                <p class="date">公開日: ${new Date(paper.published_date).toLocaleDateString()}</p>
                <div class="relevance">
                    <span class="relevance-label">関連性スコア:</span>
                    <span class="relevance-score ${paper.relevance_score >= 0.95 ? 'high' : paper.relevance_score >= 0.85 ? 'medium' : 'low'}">
                        ${paper.relevance_score ? paper.relevance_score.toFixed(2) : 'N/A'}
                    </span>
                </div>
                <div class="relevance-explanation">
                    <h3>関連性の説明:</h3>
                    <p>${paper.relevance_explanation || '説明なし'}</p>
                </div>
                <div class="query-match">
                    <h3>マッチした検索クエリ:</h3>
                    <p>${paper.queryMatch}</p>
                </div>
                <div class="abstract">
                    <h3>要約:</h3>
                    <p>${paper.abstract}</p>
                </div>
                <div class="categories">
                    <h3>カテゴリ:</h3>
                    <p>${paper.categories.join(', ')}</p>
                </div>
                <div class="actions">
                    <a href="${paper.url}" target="_blank" class="action-button">PDFを表示</a>
                </div>
            </div>
        `;
        
        sidebar.innerHTML = content;
        sidebar.classList.add('active');
    }
}

function closeSidebar() {
    const sidebar = document.querySelector('.paper-detail-sidebar');
    if (sidebar) {
        sidebar.classList.remove('active');
    }
}

function addHoverEffects() {
    const nodes = document.querySelectorAll('.network-node');
    
    nodes.forEach(node => {
        node.addEventListener('mouseenter', () => {
            const nodeId = node.id;
            const lines = document.querySelectorAll('.connection-line');
            
            lines.forEach(line => {
                const lineId = line.id;
                const parts = lineId.split('-');
                if (parts.includes(nodeId)) {
                    line.classList.add('active');
                }
            });
        });
        
        node.addEventListener('mouseleave', () => {
            const lines = document.querySelectorAll('.connection-line');
            lines.forEach(line => {
                line.classList.remove('active');
            });
        });
    });
}

// Export functions that need to be accessible globally
window.initializeNetwork = initializeNetwork;
window.showPaperDetail = showPaperDetail;
window.closeSidebar = closeSidebar;
