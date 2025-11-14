document.addEventListener("DOMContentLoaded", () => {

    console.log("Dom loaded correctly");

    const API_URL = "http://127.0.0.1:5000/api";

    let visNetwork = null; // for the main graph
    let bipartiteNetwork = null; // for the user post graphs  

    // === DOM ELEMENTS ===
    const dom = {
        // Basic Graph divs
        initBtn: document.getElementById('init-btn'),
        initData: document.getElementById('init-data'),
        addNodeBtn: document.getElementById('add-node-btn'),
        remNodeBtn: document.getElementById('rem-node-btn'),
        modNode: document.getElementById('mod-node'),
        addEdgeBtn: document.getElementById('add-edge-btn'),
        remEdgeBtn: document.getElementById('rem-edge-btn'),
        modEdgeU: document.getElementById('mod-edge-u'),
        modEdgeV: document.getElementById('mod-edge-v'),
        modEdgeW: document.getElementById('mod-edge-w'),
        recBtn: document.getElementById('rec-btn'),
        recNode: document.getElementById('rec-node'),
        attackBtn: document.getElementById('attack-btn'),
        graphDiv: document.getElementById('graph'),
        recsOutput: document.getElementById('recs-output'),
        recsOutputPre: document.querySelector('#recs-output pre'),
        commOutput: document.getElementById('comm-output'),
        commOutputUl: document.getElementById('comm-list'),
        statusMessage: document.getElementById('status-message'),

        // Post System divs
        activeUserSelect: document.getElementById('active-user-select'),
        postText: document.getElementById('post-text'),
        createPostBtn: document.getElementById('create-post-btn'),
        weightedRecBtn: document.getElementById('weighted-rec-btn'),
        weightedRecsOutput: document.getElementById('weighted-recs-output'),
        weightedRecsOutputPre: document.querySelector('#weighted-recs-output pre'),
        postFeedList: document.getElementById('post-feed-list'),
        // Bipartite graph divs
        postRecBtn: document.getElementById('post-rec-btn'),
        postRecsOutput: document.getElementById('post-recs-output'),
        postRecsOutputPre: document.querySelector('#post-recs-output pre'),
        bipartiteGraphDiv: document.getElementById('bipartite-graph')
    };

    // Initialize inital graph via vis.js
    function initializeGraph() {
        if (!dom.graphDiv) {
            console.error("Graph div NOT FOUND.");
            return;
        }

        const data = {
            nodes: new vis.DataSet([]),
            edges: new vis.DataSet([])
        };
        const options = {
            nodes: { shape: "dot", size: 16, borderWidth: 2 },
            edges: { width: 2, font: { align: "middle" }, color: { color: "#848484", highlight: "#4ecdc4" } },
            physics: { solver: "forceAtlas2Based", stabilization: { iterations: 150 } }
        };

        visNetwork = new vis.Network(dom.graphDiv, data, options);
        console.log("Main Graph Network created.");
    }

    // Bipartite Graph initialization ---
    function initializeBipartiteGraph() {
        if (!dom.bipartiteGraphDiv) {
            console.error("Bipartite graph div NOT FOUND.");
            return;
        }
        console.log("Creating graph for Bipartite user and post");

        const data = {
            nodes: new vis.DataSet([]),
            edges: new vis.DataSet([])
        };
        const options = {
            layout: {
                hierarchical: {
                    direction: "LR", // Left-to-Right layout
                    sortMethod: "directed"
                }
            },
            physics: false,
            edges: {
                arrows: { to: { enabled: false } }
            }
        };

        bipartiteNetwork = new vis.Network(dom.bipartiteGraphDiv, data, options);
        console.log("Bipartite Graph Network created.");
    }

    // Render Graph with new state   
    function renderGraph(state) {
        if (!visNetwork || !state) return;
        console.log("%c[Render Main Graph]", "color: cyan", state);

        const nodes = new vis.DataSet(state.nodes || []);
        const edges = new vis.DataSet(state.edges || []);
        visNetwork.setData({ nodes, edges });

        if (state.community_list && state.community_list.length > 0) {
            dom.commOutputUl.innerHTML = state.community_list
                .map(c => `<li>${c}</li>`).join('');
            dom.commOutput.style.display = "block";
        } else {
            dom.commOutput.style.display = "none";
        }
        
        populateActiveUserDropdown(state.nodes || []);
    }

    // Render Bipartite Graph with new state  
    function renderBipartiteGraph(state) {
        if (!bipartiteNetwork || !state) return;
        console.log("Render Bipartite Graph ");
        
        const nodes = new vis.DataSet(state.nodes || []);
        const edges = new vis.DataSet(state.edges || []);
        bipartiteNetwork.setData({ nodes, edges });
    }

    // Status message showed on top of the page
    function showStatus(msg, error = false) {
        dom.statusMessage.style.display = "block";
        dom.statusMessage.textContent = msg;
        dom.statusMessage.style.background = error ? "#ffebee" : "#e6f7ff";
    }

    // Helper functions for apis
    async function postData(endpoint, payload) {
        try {
            const res = await fetch(`${API_URL}/${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const resJson = await res.json();
            if (!res.ok) throw new Error(resJson.error || "Unknown server error");
            return resJson;
        } catch (e) {
            showStatus("Error: " + e.message, true);
            return null;
        }
    }

    async function getData(endpoint) {
        try {
            const res = await fetch(`${API_URL}/${endpoint}`);
            const resJson = await res.json();
            if (!res.ok) throw new Error(resJson.error || "Unknown server error");
            return resJson;
        } catch (e) {
            showStatus("Error: " + e.message, true);
            return null;
        }
    }

    // Helper function for post system
    function populateActiveUserDropdown(nodes) {
        const selected = dom.activeUserSelect.value;
        dom.activeUserSelect.innerHTML = '<option value="">-- Select User --</option>';
        const sortedNodes = [...nodes].sort((a, b) => a.id - b.id);

        for (const node of sortedNodes) {
            const option = document.createElement('option');
            option.value = node.id;
            option.textContent = `User ${node.id}`;
            dom.activeUserSelect.appendChild(option);
        }
        if (nodes.find(n => n.id == selected)) {
            dom.activeUserSelect.value = selected;
        }
    }

    async function fetchPostFeed() {
        const posts = await getData('posts');
        if (posts) {
            dom.postFeedList.innerHTML = '';
            if (posts.length === 0) {
                dom.postFeedList.innerHTML = '<p>No posts yet. Create one!</p>';
                return;
            }
            for (const post of posts) {
                const postDiv = document.createElement('div');
                postDiv.className = 'post-card';
                postDiv.innerHTML = `
                    <p>${post.text}</p>
                    <div class="post-card-footer">
                        <span>By: <strong>User ${post.creator}</strong> | Likes: ${post.likes}</span>
                        <button class="like-btn" data-post-id="${post.id}">Like</button>
                    </div>
                `;
                dom.postFeedList.appendChild(postDiv);
            }
            addLikeButtonListeners();
        }
    }
    
    // Helper to fetch and render bipartite graph
    async function fetchBipartiteGraph() {
        const state = await getData('bipartite-graph');
        if (state) {
            renderBipartiteGraph(state);
        }
    }

    function addLikeButtonListeners() {
        dom.postFeedList.querySelectorAll('.like-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const postId = e.target.dataset.postId;
                const userId = dom.activeUserSelect.value;

                if (!userId) {
                    showStatus("Please select an 'Active User' from the dropdown first.", true);
                    return;
                }

                showStatus(`User ${userId} liking post ${postId}...`);
                e.target.disabled = true;
                e.target.textContent = "Liking...";

                const state = await postData('post/like', { user: userId, post_id: postId });

                if (state) {
                    renderGraph(state);
                    fetchPostFeed();
                    fetchBipartiteGraph();
                    showStatus(`Like successful! Graph weights updated.`);
                } else {
                    e.target.disabled = false;
                    e.target.textContent = "Like";
                }
            });
        });
    }

    // Event Handler for various buttons do that they hit the respective APIs
    dom.initBtn.addEventListener("click", async () => {
        showStatus("Initializing...");
        const raw = dom.initData.value.trim();
        const state = await postData("init", { edge_data: raw });
        if (state) {
            renderGraph(state);
            fetchPostFeed();
            fetchBipartiteGraph(); // <-- NEW: Fetch on init
            showStatus("Graph initialized. Post feed cleared.");
        }
    });

    dom.addNodeBtn.addEventListener("click", async () => {
        const n = dom.modNode.value;
        if (!n) return;
        const state = await postData("modify", { action: "add_node", data: [n] });
        if (state) renderGraph(state);
        dom.modNode.value = "";
    });

    dom.remNodeBtn.addEventListener("click", async () => {
        const n = dom.modNode.value;
        if (!n) return;
        const state = await postData("modify", { action: "remove_node", data: [n] });
        if (state) renderGraph(state);
        dom.modNode.value = "";
    });

    dom.addEdgeBtn.addEventListener("click", async () => {
        const u = dom.modEdgeU.value;
        const v = dom.modEdgeV.value;
        const w = dom.modEdgeW.value || 1;
        const state = await postData("modify", { action: "change_weight", data: [u, v, w] });
        if (state) renderGraph(state);
    });

    dom.remEdgeBtn.addEventListener("click", async () => {
        const u = dom.modEdgeU.value;
        const v = dom.modEdgeV.value;
        const state = await postData("modify", { action: "remove_edge", data: [u, v] });
        if (state) renderGraph(state);
    });

    dom.recBtn.addEventListener("click", async () => {
        const node = dom.recNode.value;
        if (!node) {
            showStatus("Please enter a Node ID for Jaccard recommendations.", true);
            return;
        }
        const data = await getData(`recommend/${node}`);
        if (data) {
            dom.recsOutputPre.textContent = data.recommendations.join("\n") || "No recommendations found.";
            dom.recsOutput.style.display = "block";
            showStatus(data.message);
        }
    });

    dom.attackBtn.addEventListener("click", async () => {
        showStatus("Running attack simulation...");
        const res = await getData("attack");
        if (res.graph_state) renderGraph(res.graph_state);
        // Chart logic is removed
        showStatus(res.message || "Attack analysis complete.");
    });

    
    dom.createPostBtn.addEventListener("click", async () => {
        const text = dom.postText.value;
        const userId = dom.activeUserSelect.value;

        if (!userId) {
            showStatus("Please select an 'Active User' to post.", true);
            return;
        }
        if (!text) {
            showStatus("Please write something in the post.", true);
            return;
        }

        showStatus("Creating post...");
        const newPost = await postData('post/create', { user: userId, text: text });

        if (newPost) {
            showStatus("Post created!");
            dom.postText.value = '';
            fetchPostFeed();
            fetchBipartiteGraph(); // <-- NEW: Refresh bipartite graph
        }
    });

    dom.weightedRecBtn.addEventListener("click", async () => {
        const userId = dom.recNode.value;
        if (!userId) {
            showStatus("Please select a User ID to get recommendations for.", true);
            return;
        }

        showStatus(`Getting friend recommendations for User ${userId}...`);
        const recs = await getData(`recommend-by-weight/${userId}`);

        if (recs) {
            if (recs.length === 0) {
                dom.weightedRecsOutputPre.textContent = "No recommendations found.";
            } else {
                dom.weightedRecsOutputPre.textContent = recs.map(r => `User ${r.user} (Weight: ${r.weight}, Reason: ${r.reason})`).join("\n");
            }
            dom.weightedRecsOutput.style.display = "block";
            showStatus("Friend recommendation complete.");
        }
    });

    dom.postRecBtn.addEventListener("click", async () => {
        const userId = dom.recNode.value;
        if (!userId) {
            showStatus("Please select a User ID to get recommendations for.", true);
            return;
        }

        showStatus(`Getting post recommendations for User ${userId}...`);
        const data = await getData(`recommend-posts/${userId}`);

        if (data) {
            dom.postRecsOutputPre.textContent = data.recommendations.join("\n") || "No recommendations found.";
            dom.postRecsOutput.style.display = "block";
            showStatus("Post recommendation complete.");
        }
    });

    // Initializations
    initializeGraph();
    initializeBipartiteGraph(); // <-- NEW
    fetchPostFeed();
    fetchBipartiteGraph(); // <-- NEW
    showStatus("Ready. Load a graph to begin.");

});