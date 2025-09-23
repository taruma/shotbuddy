        let currentProject = null;
        let shots = [];
        let savedScrollY = 0;
        let savedRowId = null;
        let tocObserver = null;
        const NEW_SHOT_DROP_TEXT = 'Drop an asset here to create a new shot.';
        document.documentElement.style.setProperty('--new-shot-drop-text', `'${NEW_SHOT_DROP_TEXT}'`);

        // Auto-resize notes textareas to fit content (no scrollbars)
        function autoResize(textarea) {
            if (!textarea) return;
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        }

        // Resize all notes textareas (e.g. after grid becomes visible)
        function autoResizeAllNotes() {
            document.querySelectorAll('.notes-input').forEach(autoResize);
        }

        // Wire auto-resize to all current and future .notes-input elements
        document.addEventListener('input', (e) => {
            if (e.target && e.target.classList && e.target.classList.contains('notes-input')) {
                autoResize(e.target);
            }
        });

        // Theme functions
        function applyTheme(theme) {
            document.body.classList.toggle('light', theme === 'light');
            localStorage.setItem('theme', theme);
            const btn = document.getElementById('theme-toggle');
            if (btn) {
                btn.textContent = theme === 'light' ? '☀️' : '🌙';
            }
        }

        // Menu functions

        async function loadProjectFromManualPath() {
            const input = document.getElementById('manual-path-input');
            const path = input.value.trim();

            if (!path) {
                showNotification("Please enter a full path to a project folder.", "error");
                return;
            }

            try {
                const response = await fetch('/api/project/open', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path })
                });

                const result = await response.json();

                if (result.success) {
                currentProject = result.data;
                showMainInterface();
                loadShots();
                showNotification(`Opened project "${result.data.name}"`);
                } else {
                showNotification(result.error || 'Failed to open project', 'error');
                }
            } catch (error) {
                console.error("Error loading project:", error);
                showNotification("Unexpected error loading project", "error");
            }
        }

        function openCreateProjectModal() {
            const basePath = document.getElementById('manual-path-input').value.trim();
            if (!basePath) {
                showNotification("Please enter a full path to a project folder.", "error");
                return;
            }
            document.getElementById('new-project-name').value = '';
            document.getElementById('create-project-modal').style.display = 'flex';
            document.getElementById('new-project-name').focus();
        }

        function closeCreateProjectModal() {
            document.getElementById('create-project-modal').style.display = 'none';
        }

        async function confirmCreateProject() {
            const basePath = document.getElementById('manual-path-input').value.trim();
            const projectName = document.getElementById('new-project-name').value.trim();

            if (!basePath) {
                showNotification("Please enter a full path to a project folder.", "error");
                return;
            }
            if (!projectName) {
                showNotification("Please enter a project name.", "error");
                return;
            }

            try {
                const response = await fetch('/api/project/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path: basePath, name: projectName })
                });

                const result = await response.json();

                if (result.success) {
                    currentProject = result.data;
                    closeCreateProjectModal();
                    showMainInterface();
                    loadShots();
                    showNotification(`Created project "${result.data.name}"`);
                } else {
                    showNotification(result.error || 'Failed to create project', 'error');
                }
            } catch (error) {
                console.error('Error creating project:', error);
                showNotification('Unexpected error creating project', 'error');
            }
        }

    
        // Initialize app
        document.addEventListener('DOMContentLoaded', function() {
            document.addEventListener('click', handlePromptButtonClick);
            const saved = localStorage.getItem('theme') || 'dark';
            applyTheme(saved);
            document.getElementById('theme-toggle')?.addEventListener('click', () => {
                const next = document.body.classList.contains('light') ? 'dark' : 'light';
                applyTheme(next);
            });
            createTocUI(); // Inject TOC panel and toggle button
            window.addEventListener('resize', positionToc); // Re-position on resize
            checkForProject();
        });

        function handlePromptButtonClick(event) {
            const btn = event.target.closest('.prompt-button');
            if (!btn) {
                return;
            }
            event.stopPropagation();
            const shot = btn.dataset.shot;
            const type = btn.dataset.type;

            // For image/video we set data-current-version and data-max-version.
            // For lipsync we still have only data-version; treat it as both current and max.
            let currentVersion = btn.dataset.currentVersion ? parseInt(btn.dataset.currentVersion, 10) : undefined;
            let maxVersion = btn.dataset.maxVersion ? parseInt(btn.dataset.maxVersion, 10) : undefined;

            if (currentVersion == null || Number.isNaN(currentVersion)) {
                const v = parseInt(btn.dataset.version, 10);
                currentVersion = Number.isNaN(v) ? 1 : v;
            }
            if (maxVersion == null || Number.isNaN(maxVersion)) {
                const v = parseInt(btn.dataset.version, 10);
                maxVersion = Number.isNaN(v) ? currentVersion : v;
            }

            openPromptModal(shot, type, currentVersion, maxVersion);
        }

        async function checkForProject() {
            try {
                const response = await fetch('/api/project/current');
                const result = await response.json();
                
                if (result.success && result.data) {
                    currentProject = result.data;
                    showMainInterface();
                    loadShots();
                } else {
                    showSetupScreen();
                }
            } catch (error) {
                console.error('Error checking project:', error);
                showSetupScreen();
            }
        }

        function showSetupScreen() {
            document.getElementById('setup-screen').style.display = 'flex';
            document.getElementById('main-interface').style.display = 'none';
        }

        function showMainInterface() {
            document.getElementById('setup-screen').style.display = 'none';
            document.getElementById('main-interface').style.display = 'block';
            document.getElementById('project-title').textContent = currentProject.name;
            const input = document.getElementById('manual-path-input');
            if (input && currentProject && currentProject.path) {
                input.value = currentProject.path;
            }
        }

        async function loadShots(rowId = null) {
            captureScroll(rowId);
            document.getElementById('loading').style.display = 'block';
            document.getElementById('shot-grid').style.display = 'none';
            
            try {
                const response = await fetch('/api/shots');
                const result = await response.json();
                
                if (result.success) {
                    shots = result.data;
                    renderShots();
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('shot-grid').style.display = 'block';
                    // Ensure layout is visible before measuring scrollHeight
                    requestAnimationFrame(() => requestAnimationFrame(autoResizeAllNotes));
                    restoreScroll();
                } else {
                    showNotification(result.error || 'Failed to load shots', 'error');
                }
            } catch (error) {
                console.error('Error loading shots:', error);
                showNotification('Error loading shots', 'error');
                document.getElementById('loading').style.display = 'none';
            }
        }

        // --- Table of Shots (TOC) Functions ---

        function createTocUI() {
            const headerControls = document.querySelector('.header-controls');
            if (!headerControls) return;

            // Create TOC toggle button
            const tocToggle = document.createElement('button');
            tocToggle.id = 'toc-toggle';
            tocToggle.className = 'dark-button icon-button';
            tocToggle.title = 'Toggle Table of Shots';
            tocToggle.setAttribute('aria-label', 'Toggle Table of Shots');
            tocToggle.setAttribute('aria-controls', 'shot-toc');
            tocToggle.setAttribute('aria-expanded', 'false');
            tocToggle.textContent = 'TOC';
            tocToggle.addEventListener('click', toggleTocPanel);
            headerControls.appendChild(tocToggle);

            // Create TOC panel container
            const tocPanel = document.createElement('aside');
            tocPanel.id = 'shot-toc';
            tocPanel.className = 'shot-toc';
            tocPanel.setAttribute('role', 'navigation');
            tocPanel.setAttribute('aria-label', 'Table of Shots');
            document.body.appendChild(tocPanel);

            // Initial positioning and mode
            positionToc();
        }

        function positionToc() {
            const toc = document.getElementById('shot-toc');
            const grid = document.querySelector('.shot-grid');
            const menuBar = document.querySelector('.menu-bar');
            const header = document.querySelector('.header');

            if (!toc || !grid) return;

            const gridRect = grid.getBoundingClientRect();
            const menuHeight = menuBar ? menuBar.offsetHeight : 0;
            const headerHeight = header ? header.offsetHeight : 0;
            const topOffset = Math.max(20, menuHeight + headerHeight + 10);
            const availableWidth = window.innerWidth - gridRect.right - 32;

            // Determine mode: docked or drawer
            if (availableWidth >= 260) {
                toc.classList.remove('mode-drawer');
                toc.classList.add('mode-docked');
                toc.style.top = `${topOffset}px`;
                toc.style.bottom = '16px';
                toc.style.display = localStorage.getItem('tocOpen') === 'false' ? 'none' : 'block';
            } else {
                toc.classList.remove('mode-docked');
                toc.classList.add('mode-drawer');
                toc.style.display = 'none'; // Hidden by default in drawer mode
            }
        }

        function toggleTocPanel() {
            const toc = document.getElementById('shot-toc');
            const toggle = document.getElementById('toc-toggle');
            if (!toc || !toggle) return;

            const isOpen = toc.classList.contains('mode-drawer') ? 
                toc.classList.contains('open') : 
                toc.style.display !== 'none';

            if (isOpen) {
                toc.classList.remove('open');
                toc.style.display = 'none';
                toggle.setAttribute('aria-expanded', 'false');
                localStorage.setItem('tocOpen', 'false');
            } else {
                toc.classList.add('open');
                toc.style.display = 'block';
                toggle.setAttribute('aria-expanded', 'true');
                localStorage.setItem('tocOpen', 'true');
            }
        }

        function renderTOC() {
            const toc = document.getElementById('shot-toc');
            if (!toc) return;

            const activeShots = shots.filter(s => !s.archived);
            const archivedShots = shots.filter(s => s.archived);

            // Clear and rebuild
            toc.innerHTML = `
                <div class="toc-header">
                    <span>Table of Shots</span>
                    <button class="dark-button icon-button" onclick="toggleTocPanel()" aria-label="Close TOC">&times;</button>
                </div>
                <input type="text" class="toc-filter" placeholder="Filter shots..." oninput="filterTocItems(this.value)">
                <div class="toc-section">
                    <div class="toc-section-title">Active Shots (${activeShots.length})</div>
                    <ul class="toc-list" id="toc-active-list"></ul>
                </div>
            `;

            const activeList = document.getElementById('toc-active-list');
            activeShots.forEach(shot => {
                const item = document.createElement('li');
                item.className = 'toc-item';
                item.innerHTML = shot.display_name
                    ? `${escapeHtml(shot.display_name)} <span class="shot-code">(${shot.name})</span>`
                    : shot.name;
                item.dataset.target = `shot-row-${shot.name}`;
                item.addEventListener('click', () => scrollToShot(shot.name));
                activeList.appendChild(item);
            });

            if (archivedShots.length > 0) {
                const archivedSection = document.createElement('div');
                archivedSection.className = 'toc-section';
                archivedSection.innerHTML = `
                    <div class="toc-section-title">Archived Shots (${archivedShots.length})</div>
                    <ul class="toc-list" id="toc-archived-list"></ul>
                `;
                toc.appendChild(archivedSection);

                const archivedList = document.getElementById('toc-archived-list');
                archivedShots.forEach(shot => {
                    const item = document.createElement('li');
                    item.className = 'toc-item archived';
                    item.innerHTML = shot.display_name
                        ? `${escapeHtml(shot.display_name)} <span class="shot-code">(${shot.name})</span>`
                        : shot.name;
                    item.dataset.target = `shot-row-${shot.name}`;
                    item.addEventListener('click', () => scrollToShot(shot.name));
                    archivedList.appendChild(item);
                });
            }

            // Set up IntersectionObserver to highlight active item
            setupTocObserver();
        }

        function filterTocItems(query) {
            const items = document.querySelectorAll('.toc-item');
            query = query.toLowerCase();
            items.forEach(item => {
                const match = item.textContent.toLowerCase().includes(query);
                item.style.display = match ? 'block' : 'none';
            });
        }

        function scrollToShot(shotName) {
            const targetId = `shot-row-${shotName}`;
            const el = document.getElementById(targetId);
            if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                // Flash highlight
                el.style.transition = 'background 0.5s';
                el.style.background = '#3a3a5a';
                setTimeout(() => {
                    el.style.background = '';
                }, 1000);
            }
            // Close drawer if in drawer mode
            const toc = document.getElementById('shot-toc');
            if (toc.classList.contains('mode-drawer')) {
                toggleTocPanel();
            }
        }

        function setupTocObserver() {
            if (tocObserver) {
                tocObserver.disconnect();
            }

            tocObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    const targetId = entry.target.id;
                    const tocItem = document.querySelector(`.toc-item[data-target="${targetId}"]`);
                    if (tocItem) {
                        tocItem.classList.toggle('active', entry.isIntersecting);
                    }
                });
            }, { threshold: 0.5 });

            document.querySelectorAll('.shot-row').forEach(row => {
                tocObserver.observe(row);
            });
        }

        function renderShots() {
            const shotList = document.getElementById("shot-list");
            shotList.innerHTML = "";

            const activeShots = shots.filter(s => !s.archived);
            const archivedShots = shots.filter(s => s.archived);

            // Active section container
            const activeContainer = document.createElement("div");
            activeContainer.id = "active-shot-list";

            // Create drop zones for active section
            const finalDropZone = document.createElement("div");
            finalDropZone.className = "drop-between-rows final-drop new-shot-drop-zone";
            finalDropZone.addEventListener("dragover", handleRowDragOver);
            finalDropZone.addEventListener("drop", handleRowDrop);
            finalDropZone.addEventListener("dragleave", handleRowDragLeave);
            const finalBtn = document.createElement("button");
            finalBtn.className = "green-button new-shot-btn inline-new-shot-btn";
            finalBtn.textContent = "New Shot +";
            finalBtn.addEventListener("click", () => {
                addNewShotAfter(finalDropZone.getAttribute("data-after-shot"));
            });
            finalDropZone.appendChild(finalBtn);

            const firstDropZone = document.createElement("div");
            firstDropZone.className = "drop-between-rows first-drop";
            firstDropZone.setAttribute("data-after-shot", "");
            firstDropZone.addEventListener("dragover", handleRowDragOver);
            firstDropZone.addEventListener("drop", handleRowDrop);
            firstDropZone.addEventListener("dragleave", handleRowDragLeave);
            const firstBtn = document.createElement("button");
            firstBtn.className = "green-button new-shot-btn inline-new-shot-btn";
            firstBtn.textContent = "New Shot +";
            firstBtn.addEventListener("click", () => {
                addNewShotAfter(firstDropZone.getAttribute("data-after-shot"));
            });
            firstDropZone.appendChild(firstBtn);

            if (activeShots.length === 0) {
                finalDropZone.classList.add("empty-state");
                finalDropZone.setAttribute("data-after-shot", "");
                activeContainer.appendChild(finalDropZone);
            } else {
                activeContainer.appendChild(firstDropZone);

                activeShots.forEach((shot, index) => {
                    const shotRow = createShotRow(shot);
                    activeContainer.appendChild(shotRow);

                    if (index < activeShots.length - 1) {
                        const dropBetween = document.createElement("div");
                        dropBetween.className = "drop-between-rows";
                        dropBetween.setAttribute("data-after-shot", shot.name);
                        dropBetween.addEventListener("dragover", handleRowDragOver);
                        dropBetween.addEventListener("drop", handleRowDrop);
                        dropBetween.addEventListener("dragleave", handleRowDragLeave);
                        const btn = document.createElement("button");
                        btn.className = "green-button new-shot-btn inline-new-shot-btn";
                        btn.textContent = "New Shot +";
                        btn.addEventListener("click", () => {
                            addNewShotAfter(dropBetween.getAttribute("data-after-shot"));
                        });
                        dropBetween.appendChild(btn);
                        activeContainer.appendChild(dropBetween);
                    }
                });

                finalDropZone.setAttribute("data-after-shot", activeShots[activeShots.length - 1].name);
                activeContainer.appendChild(finalDropZone);
            }

            shotList.appendChild(activeContainer);

            // Archived section
            if (archivedShots.length > 0) {
                const title = document.createElement("div");
                title.className = "section-title";
                title.textContent = "Archived";
                shotList.appendChild(title);

                const archivedContainer = document.createElement("div");
                archivedContainer.id = "archived-shot-list";

                archivedShots.forEach(shot => {
                    const row = createShotRow(shot);
                    archivedContainer.appendChild(row);
                });

            shotList.appendChild(archivedContainer);
            }

            // Initialize auto-resize for all existing .notes-input elements
            document.querySelectorAll('.notes-input').forEach(autoResize);
            restoreScroll();
            initSortable();

            // Render and update TOC
            renderTOC();
            positionToc(); // Re-calculate position in case grid changed
        }

        function initSortable() {
            const activeList = document.getElementById('active-shot-list');
            if (!activeList) return;

            new Sortable(activeList, {
                animation: 150,
                handle: '.shot-name',
                onEnd: async function (evt) {
                    const shotOrder = Array.from(activeList.children)
                        .filter(child => child.classList.contains('shot-row'))
                        .map(child => child.id.replace('shot-row-', ''));

                    try {
                        const response = await fetch('/api/shots/reorder', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ shot_order: shotOrder })
                        });
                        const result = await response.json();
                        if (result.success) {
                            showNotification('Shot order saved');
                            // Re-sync the local shots array with the new order
                            shots.sort((a, b) => shotOrder.indexOf(a.name) - shotOrder.indexOf(b.name));
                        } else {
                            showNotification(result.error || 'Failed to save order', 'error');
                        }
                    } catch (error) {
                        console.error('Error saving shot order:', error);
                        showNotification('Error saving shot order', 'error');
                    }
                }
            });
        }

        // Helper to safely escape HTML
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function createShotRow(shot) {
            const row = document.createElement('div');
            row.className = 'shot-row' + (shot.archived ? ' archived' : '');
            row.id = `shot-row-${shot.name}`;

            const actionLabel = shot.archived ? 'Unarchive' : 'Archive';
            const actionNext = shot.archived ? false : true;
            
            const labelText = shot.display_name
                ? `${escapeHtml(shot.display_name)}<div class="shot-code">(${shot.name})</div>`
                : shot.name;
            
            row.innerHTML = `
                <div class="action-cell">
                    <button class="icon-btn" title="${actionLabel}" aria-label="${actionLabel}" onclick="event.stopPropagation(); archiveShot('${shot.name}', ${actionNext})">
                        ${shot.archived
                            ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="7 14 12 9 17 14"></polyline><line x1="12" y1="9" x2="12" y2="21"></line><rect x="3" y="3" width="18" height="6" rx="2"></rect></svg>'
                            : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line><rect x="3" y="15" width="18" height="6" rx="2"></rect></svg>'}
                    </button>
                </div>
                <div class="shot-name" onclick="editDisplayName(this, '${shot.name}')">${labelText}</div>
                ${createDropZone(shot, 'first_image')}
                ${createDropZone(shot, 'last_image')}
                ${createDropZone(shot, 'video')}
                ${'' /* createLipsyncZone(shot) */}
                <div class="notes-cell">
                    <textarea class="notes-input" 
                              placeholder="Add notes..." 
                              onchange="saveNotes('${shot.name}', this.value)"
                              onblur="saveNotes('${shot.name}', this.value)">${shot.notes || ''}</textarea>
                </div>
            `;
            
            // Set data attribute for display name to avoid quote issues in onclick
            row.querySelector('.shot-name').dataset.displayName = shot.display_name || '';
            
            return row;
        }

        function displayAssetLabel(type) {
            switch (type) {
                case 'first_image': return 'First Frame';
                case 'last_image': return 'Last Frame';
                case 'video': return 'Video';
                default:
                    return type.charAt(0).toUpperCase() + type.slice(1);
            }
        }

        function createDropZone(shot, type) {
            const file = shot[type];
            const currentVersion = (file && (file.current_version || file.max_version)) || 0;
            const maxVersion = (file && file.max_version) || 0;
            const hasFile = maxVersion > 0 || currentVersion > 0;

            if (hasFile) {
                const isVideo = type === 'video';
                const thumbnailUrl = file.thumbnail ? `${file.thumbnail}?v=${Date.now()}` : null;

                let mediaHtml;
                if (isVideo) {
                    const videoStyle = thumbnailUrl ?
                        `background-image: url('${thumbnailUrl}'); background-size: cover; background-position: center;` :
                        'background: #404040;';
                    mediaHtml = `<div class="preview-thumbnail video-thumbnail" style="${videoStyle}"></div>`;
                } else {
                    mediaHtml = thumbnailUrl ?
                        `<img class="preview-thumbnail" src="${thumbnailUrl}" alt="${displayAssetLabel(type)} thumbnail">` :
                        `<div class="preview-thumbnail placeholder"></div>`;
                }

                return `
                    <div class="drop-zone with-caption"
                         ondragover="handleDragOver(event, '${type}')"
                         ondrop="handleDrop(event, '${shot.name}', '${type}')"
                         ondragleave="handleDragLeave(event)">
                        <div class="file-preview">
                            ${mediaHtml}

                            <div class="version-badge"
                                 title="Click to cycle version"
                                 onclick="cycleAssetVersion('${shot.name}', '${type}')">v${String(currentVersion).padStart(3, '0')}</div>
                            <button class="prompt-button"
                                    title="View and edit prompt"
                                    data-shot="${shot.name}"
                                    data-type="${type}"
                                    data-current-version="${currentVersion}"
                                    data-max-version="${maxVersion}">P</button>
                        </div>
                        <input class="asset-caption-input"
                               type="text"
                               placeholder="Add text..."
                               value="${file.caption ? String(file.caption).replace(/&/g,'&').replace(/"/g,'"').replace(/</g,'<').replace(/>/g,'>') : ''}"
                               onblur="saveCaption('${shot.name}', '${type}', this.value)"
                               onchange="saveCaption('${shot.name}', '${type}', this.value)" />
                    </div>
                `;
            } else {
                return `
                    <div class="drop-zone empty"
                         onclick="openFileDialog('${shot.name}', '${type}')"
                         ondragover="handleDragOver(event, '${type}')"
                         ondrop="handleDrop(event, '${shot.name}', '${type}')"
                         ondragleave="handleDragLeave(event)">
                        <div class="drop-placeholder">
                            <div class="text">Add ${displayAssetLabel(type)}</div>
                        </div>
                    </div>
                `;
            }
        }

        function createLipsyncZone(shot) {
            const parts = ['driver', 'target', 'result'];
            let html = '<div class="lipsync-cell">';
            for (const part of parts) {
                const file = shot.lipsync[part];
                const hasFile = file.version > 0;
                const label = part.charAt(0).toUpperCase() + part.slice(1);
                if (hasFile) {
                    const thumbnailUrl = file.thumbnail ? `${file.thumbnail}?v=${Date.now()}` : null;
                    const thumbnailStyle = thumbnailUrl ?
                        `background-image: url('${thumbnailUrl}'); background-size: cover; background-position: center;` :
                        'background: #404040;';
                    html += `
                        <div class="drop-zone lipsync-drop" ondragover="handleDragOver(event, '${part}')" ondrop="handleDrop(event, '${shot.name}', '${part}')" ondragleave="handleDragLeave(event)">
                            <div class="file-preview lipsync-preview">
                                <div class="preview-thumbnail lipsync-thumbnail" data-label="${label}" style="${thumbnailStyle}"></div>
                                <div class="version-badge">v${String(file.version).padStart(3, '0')}</div>
                                <button class="prompt-button" title="View and edit prompt"
                                        data-shot="${shot.name}"
                                        data-type="${part}"
                                        data-version="${file.version}">P</button>
                            </div>
                        </div>`;
                } else {
                    html += `
                        <div class="drop-zone lipsync-drop empty" ondragover="handleDragOver(event, '${part}')" ondrop="handleDrop(event, '${shot.name}', '${part}')" ondragleave="handleDragLeave(event)">
                            <div class="drop-placeholder">
                                <div class="text">${label}</div>
                            </div>
                        </div>`;
                }
            }
            html += '</div>';
            return html;
        }

        async function addNewShot() {
            try {
                const response = await fetch('/api/shots', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                
                const result = await response.json();
                
                if (result.success) {
                    shots.push(result.data);
                    captureScroll(`shot-row-${result.data.name}`);
                    renderShots();
                    restoreScroll();
                    showNotification(`Shot ${result.data.name} created`);
                } else {
                    showNotification(result.error || 'Failed to create shot', 'error');
                }
            } catch (error) {
                console.error('Error creating shot:', error);
                showNotification('Error creating shot', 'error');
            }
        }

        async function addNewShotAfter(afterShot) {
            try {
                const response = await fetch('/api/shots/create-between', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ after_shot: afterShot || null })
                });

                const result = await response.json();

                if (result.success) {
                    const index = afterShot ? shots.findIndex(s => s.name === afterShot) + 1 : 0;
                    shots.splice(index, 0, result.data);
                    captureScroll(`shot-row-${result.data.name}`);
                    renderShots();
                    restoreScroll();
                    showNotification(`Shot ${result.data.name} created`);
                } else {
                    showNotification(result.error || 'Failed to create shot', 'error');
                }
            } catch (error) {
                console.error('Error creating shot:', error);
                showNotification('Error creating shot', 'error');
            }
        }

        // Drag and drop handlers
        function handleDragOver(event, fileType) {
            event.preventDefault();
            event.currentTarget.classList.add('drag-over');
        }

        function handleDragLeave(event) {
            event.currentTarget.classList.remove('drag-over');
        }

        async function handleDrop(event, shotName, expectedType) {
            event.preventDefault();
            event.currentTarget.classList.remove('drag-over');

            const files = event.dataTransfer.files;
            if (files.length === 0) {
                showNotification('No files dropped', 'error');
                return;
            }

            const file = files[0];
            await uploadFile(file, shotName, expectedType);
        }

        async function uploadFile(file, shotName, fileType) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('shot_name', shotName);
            formData.append('file_type', fileType);

            try {
                showNotification('Uploading file...');
                
                const response = await fetch('/api/shots/upload', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    showNotification(`${file.name} uploaded successfully!`);
                    loadShots(`shot-row-${shotName}`); // Refresh and keep scroll
                } else {
                    showNotification(result.error || 'Upload failed', 'error');
                }
            } catch (error) {
                console.error('Upload error:', error);
                showNotification('Upload failed', 'error');
            }
        }

        async function cycleAssetVersion(shotName, assetType) {
            const shot = shots.find(s => s.name === shotName);
            if (!shot || !shot[assetType]) return;

            const info = shot[assetType];
            const maxV = info.max_version || 0;
            if (maxV < 1) return;

            const curr = info.current_version || maxV;
            const next = (curr % maxV) + 1;

            try {
                showNotification('Switching version...');
                const response = await fetch('/api/shots/promote', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ shot_name: shotName, asset_type: assetType, version: next })
                });
                const result = await response.json();
                if (result.success) {
                    const updated = result.data;
                    const idx = shots.findIndex(s => s.name === shotName);
                    if (idx !== -1) {
                        shots[idx] = updated;
                    }
                    captureScroll(`shot-row-${shotName}`);
                    renderShots();
                    restoreScroll();
                } else {
                    showNotification(result.error || 'Failed to switch version', 'error');
                }
            } catch (error) {
                console.error('Promote failed:', error);
                showNotification('Failed to switch version', 'error');
            }
        }

        function showNotification(message, type = 'success') {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = `notification ${type}`;
            notification.classList.add('show');

            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        }

        function captureScroll(rowId = null) {
            savedScrollY = window.pageYOffset;
            savedRowId = rowId;
        }

        function restoreScroll() {
            if (savedRowId) {
                const el = document.getElementById(savedRowId);
                if (el) {
                    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    savedRowId = null;
                    return;
                }
            }
            window.scrollTo({ top: savedScrollY });
            savedRowId = null;
        }

        // Drag and drop handlers for rows
        function handleRowDragOver(event) {
            event.preventDefault();

            // Some browsers do not populate `dataTransfer.files` during
            // `dragover`, so check the types list instead. If it includes
            // "Files", we assume a file is being dragged and show the marker.
            const types = event.dataTransfer.types;
            if (types && Array.from(types).includes('Files')) {
                event.currentTarget.classList.add('drag-over', 'new-shot-drop-zone');
            }
        }

        function handleRowDragLeave(event) {
            event.currentTarget.classList.remove('drag-over', 'new-shot-drop-zone');
        }

        async function handleRowDrop(event) {
            event.preventDefault();
            event.currentTarget.classList.remove('drag-over', 'new-shot-drop-zone');

            const files = event.dataTransfer.files;
            if (files.length === 0) return;

            const afterShot = event.currentTarget.getAttribute('data-after-shot');
            
            try {
                // Create new shot
                const response = await fetch('/api/shots/create-between', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        after_shot: afterShot || null
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    const newShot = result.data;
                    showNotification(`Shot ${newShot.name} created`);
                    
                    // Upload the file to the new shot
                    const file = files[0];
                    const fileType = getFileType(file.name);
                    
                    if (fileType) {
                        await uploadFile(file, newShot.name, fileType);
                    } else {
                        showNotification('Unsupported file type', 'error');
                        loadShots(`shot-row-${newShot.name}`); // Still refresh to show the new shot
                    }
                } else {
                    showNotification(result.error || 'Failed to create shot', 'error');
                }
            } catch (error) {
                console.error('Error creating shot:', error);
                showNotification('Error creating shot', 'error');
            }
        }

        function getFileType(filename) {
            const ext = filename.toLowerCase().split('.').pop();
            const imageExts = ['jpg', 'jpeg', 'png', 'webp'];
            const videoExts = ['mp4', 'mov'];

            if (imageExts.includes(ext)) return 'first_image'; // default image target
            if (videoExts.includes(ext)) return 'video';
            return null;
        }

        function openFileDialog(shotName, fileType) {
            const input = document.createElement('input');
            input.type = 'file';
            if (fileType === 'first_image' || fileType === 'last_image' || fileType === 'image') {
                input.accept = 'image/*';
            } else if (fileType === 'video') {
                input.accept = 'video/*';
            }
            input.style.display = 'none';
            input.addEventListener('change', () => {
                if (input.files && input.files[0]) {
                    uploadFile(input.files[0], shotName, fileType);
                }
                input.remove();
            });
            document.body.appendChild(input);
            input.click();
        }

        async function saveNotes(shotName, notes) {
            try {
                const response = await fetch('/api/shots/notes', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        shot_name: shotName,
                        notes: notes
                    })
                });
                
                const result = await response.json();
                
                if (!result.success) {
                    showNotification(result.error || 'Failed to save notes', 'error');
                }
                // Don't show success notification for notes to avoid spam
            } catch (error) {
                console.error('Error saving notes:', error);
                showNotification('Error saving notes', 'error');
            }
        }
    
async function saveCaption(shotName, assetType, caption) {
    try {
        const response = await fetch('/api/shots/caption', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                shot_name: shotName,
                asset_type: assetType,
                caption: caption
            })
        });
        const result = await response.json();
        if (!result.success) {
            showNotification(result.error || 'Failed to save caption', 'error');
        }
    } catch (error) {
        console.error('Error saving caption:', error);
        showNotification('Error saving caption', 'error');
    }
}
    
function editShotName(element, currentName) {
    const newName = prompt('Enter new shot name', currentName);
    if (!newName || newName === currentName) {
        return;
    }
    renameShot(currentName, newName);
}

async function renameShot(oldName, newName) {
    try {
        const response = await fetch('/api/shots/rename', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ old_name: oldName, new_name: newName })
        });
        const result = await response.json();
        if (result.success) {
            showNotification(`Renamed to ${newName}`);
            loadShots(`shot-row-${newName}`);
        } else {
            showNotification(result.error || 'Rename failed', 'error');
        }
    } catch (error) {
        console.error('Rename failed:', error);
        showNotification('Rename failed', 'error');
    }
}

async function saveDisplayName(shotName, displayName) {
    try {
        const response = await fetch('/api/shots/display-name', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ shot_name: shotName, display_name: displayName })
        });
        const result = await response.json();
        if (result.success) {
            showNotification(`Display name updated`);
            const idx = shots.findIndex(s => s.name === shotName);
            if (idx !== -1) {
                shots[idx] = result.data;
            }
            captureScroll(`shot-row-${shotName}`);
            renderShots();
            restoreScroll();
        } else {
            showNotification(result.error || 'Failed to update display name', 'error');
        }
    } catch (e) {
        console.error('Save display name failed:', e);
        showNotification('Failed to update display name', 'error');
    }
}

// Expose globally for inline onclick
window.saveDisplayName = saveDisplayName;

function editDisplayName(element, shotName) {
    const currentDisplayName = element.dataset.displayName || '';
    const newDisplayName = prompt('Enter display name (leave empty to show only SHXXX)', currentDisplayName);
    if (newDisplayName === null || newDisplayName === currentDisplayName) {
        return;
    }
    // Update data attribute immediately for UI consistency
    element.dataset.displayName = newDisplayName;
    saveDisplayName(shotName, newDisplayName);
}

// Expose globally for inline onclick
window.editDisplayName = editDisplayName;

async function archiveShot(shotName, archived) {
    try {
        const response = await fetch('/api/shots/archive', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ shot_name: shotName, archived })
        });
        const result = await response.json();
        if (result.success) {
            showNotification(archived ? `Archived ${shotName}` : `Unarchived ${shotName}`);
            const idx = shots.findIndex(s => s.name === shotName);
            if (idx !== -1) {
                shots[idx] = result.data;
            }
            captureScroll(`shot-row-${shotName}`);
            renderShots();
            restoreScroll();
        } else {
            showNotification(result.error || 'Failed to update archive state', 'error');
        }
    } catch (e) {
        console.error('Archive toggle failed:', e);
        showNotification('Failed to update archive state', 'error');
    }
}

async function revealFile(relPath) {
            try {
                const response = await fetch('/api/shots/reveal', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ path: relPath })
                });
                const result = await response.json();
                if (!result.success) {
                    showNotification(result.error || 'Failed to reveal file', 'error');
                }
            } catch (e) {
                console.error("Reveal failed:", e);
                showNotification('Reveal failed', 'error');
    }
}

async function fetchPrompt(shotName, assetType, version) {
    try {
        const resp = await fetch(`/api/shots/prompt?shot_name=${encodeURIComponent(shotName)}&asset_type=${assetType}&version=${version}`);
        const data = await resp.json();
        if (data.success) {
            return data.data || '';
        }
    } catch (e) {
        console.error('Failed to load prompt:', e);
    }
    return '';
}

function buildVersionDropdown(versions, currentVersion) {
    const btn = document.getElementById('version-dropdown-btn');
    const menu = document.getElementById('version-dropdown-menu');
    menu.innerHTML = '';
    versions.sort((a, b) => b - a); // descending
    versions.forEach(v => {
        const item = document.createElement('div');
        item.className = 'dropdown-item';
        item.dataset.version = v;
        item.textContent = `v${String(v).padStart(3, '0')}`;
        item.onclick = () => selectPromptVersion(v);
        menu.appendChild(item);
    });
    btn.textContent = `v${String(currentVersion).padStart(3, '0')} \u25BE`;
}

function toggleVersionDropdown() {
    const menu = document.getElementById('version-dropdown-menu');
    menu.classList.toggle('show');
}

async function selectPromptVersion(v) {
    const modal = document.getElementById('prompt-modal');
    const shotName = modal.dataset.shot;
    const assetType = modal.dataset.type;
    const prevVersion = parseInt(modal.dataset.version, 10);
    if (prevVersion && prevVersion !== v) {
        const prevPromptText = document.getElementById('prompt-text').value;
        try {
            await fetch('/api/shots/prompt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    shot_name: shotName,
                    asset_type: assetType,
                    version: prevVersion,
                    prompt: prevPromptText
                })
            });
        } catch (e) {
            console.error('Auto-save failed:', e);
        }
    }
    modal.dataset.version = v;
    const versions = JSON.parse(modal.dataset.versions || '[]');
    buildVersionDropdown(versions, v);
    let prompt = await fetchPrompt(shotName, assetType, v);

    const copyBtn = document.getElementById('copy-prompt-btn');
    copyBtn.style.display = 'none';
    modal.dataset.prevPrompt = '';

    if (!prompt && v === parseInt(modal.dataset.assetVersion, 10)) {
        const prevPrompt = await fetchPrompt(shotName, assetType, v - 1);
        if (prevPrompt) {
            modal.dataset.prevPrompt = prevPrompt;
            copyBtn.style.display = 'inline-block';
        }
    }
    document.getElementById('prompt-text').value = prompt;
    toggleVersionDropdown();
}

async function openPromptModal(shotName, assetType, currentVersion, maxVersion) {
    const modal = document.getElementById('prompt-modal');
    modal.dataset.shot = shotName;
    modal.dataset.type = assetType;

    const typeLabel = displayAssetLabel(assetType);
    document.getElementById('prompt-modal-title').textContent = `${shotName} ${typeLabel} Prompt`;
    const versions = Array.from({ length: maxVersion }, (_, i) => i + 1);
    modal.dataset.versions = JSON.stringify(versions);
    modal.dataset.assetVersion = currentVersion;
    buildVersionDropdown(versions, currentVersion);

    let prompt = await fetchPrompt(shotName, assetType, currentVersion);
    const copyBtn = document.getElementById('copy-prompt-btn');
    copyBtn.style.display = 'none';
    modal.dataset.prevPrompt = '';

    if (!prompt && currentVersion > 1) {
        const prevPrompt = await fetchPrompt(shotName, assetType, currentVersion - 1);
        if (prevPrompt) {
            modal.dataset.prevPrompt = prevPrompt;
            copyBtn.style.display = 'inline-block';
        }
    }
    modal.dataset.version = currentVersion;
    document.getElementById('prompt-text').value = prompt;

    modal.style.display = 'flex';
    document.getElementById('prompt-text').focus();
}

function closePromptModal() {
    document.getElementById('prompt-modal').style.display = 'none';
}
function copyToNewPromptVersion() {
    const modal = document.getElementById('prompt-modal');
    const prevPrompt = modal.dataset.prevPrompt || '';
    if (prevPrompt) {
        document.getElementById('prompt-text').value = prevPrompt;
    }
    document.getElementById('copy-prompt-btn').style.display = 'none';
}

async function savePrompt() {
    const modal = document.getElementById('prompt-modal');
    const shotName = modal.dataset.shot;
    const assetType = modal.dataset.type;
    const version = modal.dataset.version;
    const promptText = document.getElementById('prompt-text').value;
    try {
        const response = await fetch('/api/shots/prompt', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ shot_name: shotName, asset_type: assetType, version: parseInt(version, 10), prompt: promptText })
        });
        const result = await response.json();
        if (!result.success) {
            showNotification(result.error || 'Failed to save prompt', 'error');
        } else {
            const shot = shots.find(s => s.name === shotName);
            if (shot) {
                if (assetType === 'first_image' || assetType === 'last_image' || assetType === 'image' || assetType === 'video') {
                    const key = assetType === 'image' ? 'first_image' : assetType; // legacy map
                    if (shot[key]) {
                        shot[key].prompt = promptText;
                    }
                } else if (shot.lipsync && shot.lipsync[assetType]) {
                    shot.lipsync[assetType].prompt = promptText;
                }
            }
        }
    } catch (e) {
        console.error('Error saving prompt:', e);
        showNotification('Error saving prompt', 'error');
    }
    closePromptModal();
}

async function openShotsFolder() {
    if (!currentProject) {
        showNotification('No project open', 'error');
        return;
    }
    try {
        const response = await fetch('/api/shots/open-folder', {
            method: 'POST'
        });
        const result = await response.json();
        if (!result.success) {
            showNotification(result.error || 'Failed to open folder', 'error');
        }
    } catch (e) {
        console.error('Open folder failed:', e);
        showNotification('Failed to open folder', 'error');
    }
}

// Reorder Modal Functions
let reorderSortable = null;

function openReorderModal() {
    const modal = document.getElementById('reorder-modal');
    const list = document.getElementById('reorder-list');
    const filter = document.getElementById('reorder-filter');
    
    if (!modal || !list) return;
    
    // Clear previous content
    list.innerHTML = '';
    filter.value = '';
    
    // Get active shots
    const activeShots = shots.filter(s => !s.archived);
    
    if (activeShots.length === 0) {
        list.innerHTML = '<li class="reorder-item empty">No active shots to reorder</li>';
    } else {
        // Create list items
        activeShots.forEach((shot, index) => {
            const item = document.createElement('li');
            item.className = 'reorder-item';
            item.dataset.name = shot.name;
            item.innerHTML = `
                <span class="badge">${index + 1}</span>
                ${shot.display_name ? `${escapeHtml(shot.display_name)} <span class="shot-code">(${shot.name})</span>` : shot.name}
            `;
            list.appendChild(item);
        });
        
        // Initialize Sortable
        if (reorderSortable) {
            reorderSortable.destroy();
        }
        reorderSortable = new Sortable(list, {
            animation: 150,
            ghostClass: 'reorder-ghost',
            chosenClass: 'reorder-chosen',
            dragClass: 'reorder-drag'
        });
    }
    
    // Show modal
    modal.style.display = 'flex';
}

function closeReorderModal() {
    const modal = document.getElementById('reorder-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

async function saveReorder() {
    const list = document.getElementById('reorder-list');
    if (!list) return;
    
    const items = Array.from(list.querySelectorAll('.reorder-item:not(.empty)'));
    if (items.length === 0) {
        closeReorderModal();
        return;
    }
    
    const activeOrdered = items.map(item => item.dataset.name);
    const archived = shots.filter(s => s.archived).map(s => s.name);
    const shot_order = activeOrdered.concat(archived);
    
    try {
        const response = await fetch('/api/shots/reorder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ shot_order: shot_order })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Update local shots array to match new order
            shots.sort((a, b) => shot_order.indexOf(a.name) - shot_order.indexOf(b.name));
            renderShots();
            closeReorderModal();
            showNotification('Shot order saved');
        } else {
            showNotification(result.error || 'Failed to save order', 'error');
        }
    } catch (error) {
        console.error('Error saving shot order:', error);
        showNotification('Error saving shot order', 'error');
    }
}

// Filter functionality for reorder modal
document.addEventListener('DOMContentLoaded', function() {
    const filter = document.getElementById('reorder-filter');
    if (filter) {
        filter.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            const items = document.querySelectorAll('#reorder-list .reorder-item:not(.empty)');
            
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                item.style.display = text.includes(query) ? 'flex' : 'none';
            });
        });
    }
    
    // Close modal when clicking outside
    document.addEventListener('click', function(event) {
        const modal = document.getElementById('reorder-modal');
        if (modal && event.target === modal) {
            closeReorderModal();
        }
    });
});

// Expose functions globally
window.openReorderModal = openReorderModal;
window.closeReorderModal = closeReorderModal;
window.saveReorder = saveReorder;
