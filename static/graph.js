document.addEventListener("DOMContentLoaded", () => {

    console.log("%c[graph.js] DOM Loaded – Initializing...", "color: green");

    const API_URL = "http://127.0.0.1:5000/api";

    // === GLOBAL STATE ===
    let visNetwork = null;
    let resilienceChart = null;

    // === DOM ELEMENTS ===
    const dom = {
        // Original
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
        chartCanvas: document.getElementById('resilience-chart'),
        recsOutput: document.getElementById('recs-output'),
        recsOutputPre: document.querySelector('#recs-output pre'),
        commOutput: document.getElementById('comm-output'),
        commOutputUl: document.getElementById('comm-list'), // <-- Corrected this ID
        statusMessage: document.getElementById('status-message'),

        // --- NEW ---
        activeUserSelect: document.getElementById('active-user-select'),
        postText: document.getElementById('post-text'),
        createPostBtn: document.getElementById('create-post-btn'),
        weightedRecBtn: document.getElementById('weighted-rec-btn'),
        weightedRecsOutput: document.getElementById('weighted-recs-output'),
        weightedRecsOutputPre: document.querySelector('#weighted-recs-output pre'),
        postFeedList: document.getElementById('post-feed-list')
    };

    // =======================================================
    // VISUAL GRAPH INITIALIZATION
    // =======================================================
    function initializeGraph() {
        if (!dom.graphDiv) {
            console.error("Graph div NOT FOUND.");
            return;
        }
        console.log("[graph.js] Creating vis.Network...");

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
        console.log("%cVis Network created.", "color: lightgreen");
    }

    // =======================================================
    // RENDER GRAPH WITH NEW STATE
    // =======================================================
    function renderGraph(state) {
        if (!state) return;
        console.log("%c[Render Graph]", "color: cyan", state);

        const nodes = new vis.DataSet(state.nodes || []);
        const edges = new vis.DataSet(state.edges || []);
        visNetwork.setData({ nodes, edges });

        // === communities ===
        if (state.community_list && state.community_list.length > 0) {
            dom.commOutputUl.innerHTML = state.community_list
                .map(c => `<li>${c}</li>`).join('');
            dom.commOutput.style.display = "block";
        } else {
            dom.commOutput.style.display = "none";
        }

        // --- NEW: Update the active user dropdown ---
        populateActiveUserDropdown(state.nodes || []);
    }

    // =======================================================
    // STATUS MESSAGE
    // =======================================================
    function showStatus(msg, error = false) {
        dom.statusMessage.style.display = "block";
        dom.statusMessage.textContent = msg;
        dom.statusMessage.style.background = error ? "#ffebee" : "#e6f7ff";
    }

    // =======================================================
    // API HELPERS
    // =======================================================
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

    // =======================================================
    // --- NEW: POST SYSTEM HELPERS ---
    // =======================================================

    /**
     * Updates the "Active User" dropdown with nodes from the graph
     */
    function populateActiveUserDropdown(nodes) {
        const selected = dom.activeUserSelect.value;
        dom.activeUserSelect.innerHTML = '<option value="">-- Select User --</option>';

        // Sort nodes by ID
        const sortedNodes = [...nodes].sort((a, b) => a.id - b.id);

        for (const node of sortedNodes) {
            const option = document.createElement('option');
            option.value = node.id;
            option.textContent = `User ${node.id}`;
            dom.activeUserSelect.appendChild(option);
        }
        // Re-select the previously active user if they still exist
        if (nodes.find(n => n.id == selected)) {
            dom.activeUserSelect.value = selected;
        }
    }

    /**
     * Fetches all posts from the server and renders them
     */
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
            // Add listeners to the new buttons
            addLikeButtonListeners();
        }
    }

    /**
     * Adds event listeners to all "Like" buttons in the feed
     */
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
                    // The server returns the new graph state!
                    renderGraph(state);
                    // Also refresh the post feed to update like counts
                    fetchPostFeed();
                    showStatus(`Like successful! Graph weights updated.`);
                } else {
                    // Error was already shown by postData
                    // We can re-enable the button if the error was "already liked"
                    e.target.disabled = false;
                    e.target.textContent = "Like";
                }
            });
        });
    }

    // =======================================================
    // --- EVENT HANDLERS (ORIGINAL) ---
    // =======================================================

    // INIT GRAPH
    dom.initBtn.addEventListener("click", async () => {
        showStatus("Initializing...");
        const raw = dom.initData.value.trim();
        const state = await postData("init", { edge_data: raw });
        if (state) {
            renderGraph(state);
            fetchPostFeed(); // <-- NEW: Fetch posts on init
            showStatus("Graph initialized. Post feed cleared.");
        }
    });

    // ADD NODE
    dom.addNodeBtn.addEventListener("click", async () => {
        const n = dom.modNode.value;
        if (!n) return;
        const state = await postData("modify", { action: "add_node", data: [n] });
        if (state) renderGraph(state);
        dom.modNode.value = "";
    });

    // REMOVE NODE
    dom.remNodeBtn.addEventListener("click", async () => {
        const n = dom.modNode.value;
        if (!n) return;
        const state = await postData("modify", { action: "remove_node", data: [n] });
        if (state) renderGraph(state);
        dom.modNode.value = "";
    });

    // ADD / CHANGE EDGE
    dom.addEdgeBtn.addEventListener("click", async () => {
        const u = dom.modEdgeU.value;
        const v = dom.modEdgeV.value;
        const w = dom.modEdgeW.value || 1;
        const state = await postData("modify", { action: "change_weight", data: [u, v, w] });
        if (state) renderGraph(state);
    });

    // REMOVE EDGE
    dom.remEdgeBtn.addEventListener("click", async () => {
        const u = dom.modEdgeU.value;
        const v = dom.modEdgeV.value;
        const state = await postData("modify", { action: "remove_edge", data: [u, v] });
        if (state) renderGraph(state);
    });

    // JACCARD RECOMMENDATIONS
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

    // ATTACK SIMULATION
    dom.attackBtn.addEventListener("click", async () => {
        showStatus("Running attack simulation...");
        const res = await getData("attack");
        if (res.graph_state) renderGraph(res.graph_state);
        // ... (Chart rendering logic would go here if you add it) ...
        showStatus(res.message || "Attack analysis complete.");
    });

    // =======================================================
    // --- NEW: EVENT HANDLERS (SOCIAL) ---
    // =======================================================

    // CREATE POST
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
            fetchPostFeed(); // Refresh the feed
        }
    });

    // WEIGHTED RECOMMENDATIONS
    dom.weightedRecBtn.addEventListener("click", async () => {
        const userId = dom.recNode.value;
        if (!userId) {
            showStatus("Please select an 'Active User' to get recommendations for.", true);
            return;
        }

        showStatus(`Getting weighted recommendations for User ${userId}...`);
        const recs = await getData(`recommend-by-weight/${userId}`);

        if (recs) {
            if (recs.length === 0) {
                dom.weightedRecsOutputPre.textContent = "No friends found with weight > 50.";
            } else {
                dom.weightedRecsOutputPre.textContent = recs.map(r => `User ${r.user} (Weight: ${r.weight})`).join("\n");
            }
            dom.weightedRecsOutput.style.display = "block";
            showStatus("Weighted recommendation complete.");
        }
    });

    // =======================================================
    // FIRST LOAD
    // =======================================================
    initializeGraph();
    fetchPostFeed(); // Fetch any existing posts on load
    showStatus("Ready. Load a graph to begin.");

});