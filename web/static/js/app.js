/* ============================================================
   文档处理工具 — 前端交互
   ============================================================ */

(function () {
    'use strict';

    // ============================================================
    //  Utility Helpers
    // ============================================================

    const API = {
        async post(url, data) {
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
                throw new Error(err.error || `请求失败 (${res.status})`);
            }
            return res.json();
        },
        async get(url) {
            const res = await fetch(url);
            if (!res.ok) throw new Error(`请求失败 (${res.status})`);
            return res.json();
        },
    };

    function showLoading(text) {
        document.getElementById('loadingText').textContent = text || '处理中...';
        document.getElementById('loadingOverlay').classList.add('active');
    }

    function hideLoading() {
        document.getElementById('loadingOverlay').classList.remove('active');
    }

    function toast(message, type) {
        type = type || 'info';
        const container = document.getElementById('toastContainer');
        const el = document.createElement('div');
        el.className = `toast ${type}`;
        el.textContent = message;
        container.appendChild(el);
        setTimeout(() => {
            el.classList.add('removing');
            setTimeout(() => el.remove(), 300);
        }, 3000);
    }

    function formatSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / 1048576).toFixed(1) + ' MB';
    }

    function formatTime(timestamp) {
        if (!timestamp) return '';
        const d = new Date(timestamp * 1000);
        return d.toLocaleString('zh-CN');
    }

    function escHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    // ============================================================
    //  Tab Switching
    // ============================================================

    const tabBtns = document.querySelectorAll('.tab-btn');
    const panels = {
        rename: document.getElementById('panel-rename'),
        check: document.getElementById('panel-check'),
        sort: document.getElementById('panel-sort'),
    };

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tool = btn.dataset.tool;
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            Object.keys(panels).forEach(k => panels[k].classList.toggle('active', k === tool));
        });
    });

    // ============================================================
    //  Toast & Loading helpers (exposed to inline)
    // ============================================================

    window._toast = toast;
    window._loading = { show: showLoading, hide: hideLoading };

    // ============================================================
    //  Directory Browser
    // ============================================================

    let explorerTarget = null;
    let explorerCurrentPath = '';
    const explorerModal = document.getElementById('explorerModal');
    const explorerList = document.getElementById('explorerList');
    const explorerCurrent = document.getElementById('explorerCurrent');
    const explorerPathInput = document.getElementById('explorerPathInput');

    // Open explorer
    document.querySelectorAll('.browse-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            explorerTarget = document.getElementById(btn.dataset.target);
            explorerCurrentPath = explorerTarget.value.trim() || '';
            openExplorer(explorerCurrentPath);
        });
    });

    async function openExplorer(path) {
        explorerModal.classList.add('active');
        explorerList.innerHTML = '<div class="loading">加载中...</div>';
        explorerCurrent.textContent = path || '请选择目录';
        explorerPathInput.value = path || '';

        try {
            const data = await API.post('/api/explorer/list', { path });
            renderExplorer(data);
        } catch (e) {
            explorerList.innerHTML = `<div class="loading" style="color:var(--danger)">❌ ${escHtml(e.message)}</div>`;
        }
    }

    function renderExplorer(data) {
        explorerCurrentPath = data.path;
        explorerCurrent.textContent = data.path || '(根目录)';

        if (!data.items || data.items.length === 0) {
            explorerList.innerHTML = '<div class="loading">(空目录)</div>';
            return;
        }

        const html = data.items.map(item => {
            let icon = '📁';
            if (item.type === 'parent') icon = '📂';
            else if (item.type === 'drive') icon = '💿';
            else if (item.type === 'file') icon = '📄';

            return `<div class="explorer-item" data-path="${escHtml(item.path)}" data-type="${item.type}">
                <span class="item-icon">${icon}</span>
                <span class="item-name">${escHtml(item.name)}</span>
                <span class="item-path">${escHtml(item.path)}</span>
            </div>`;
        }).join('');

        explorerList.innerHTML = html;

        // Click to navigate
        explorerList.querySelectorAll('.explorer-item').forEach(el => {
            el.addEventListener('click', async () => {
                const path = el.dataset.path;
                const type = el.dataset.type;
                if (type === 'file') {
                    // Select file
                    explorerPathInput.value = path;
                } else if (type === 'parent' || type === 'dir' || type === 'drive') {
                    // Navigate into directory
                    explorerList.innerHTML = '<div class="loading">加载中...</div>';
                    explorerCurrent.textContent = path;
                    try {
                        const data = await API.post('/api/explorer/list', { path });
                        renderExplorer(data);
                    } catch (e) {
                        explorerList.innerHTML = `<div class="loading" style="color:var(--danger)">❌ ${escHtml(e.message)}</div>`;
                    }
                }
            });
        });
    }

    // Explorer Go button
    document.getElementById('explorerGoBtn').addEventListener('click', async () => {
        const path = explorerPathInput.value.trim();
        if (path) openExplorer(path);
    });

    // Explorer path input - Enter to go
    explorerPathInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') document.getElementById('explorerGoBtn').click();
    });

    // Explorer select button
    document.getElementById('explorerSelect').addEventListener('click', () => {
        if (explorerTarget && explorerCurrentPath) {
            explorerTarget.value = explorerCurrentPath;
        }
        explorerModal.classList.remove('active');
    });

    // Explorer cancel / close
    document.getElementById('explorerCancel').addEventListener('click', () => {
        explorerModal.classList.remove('active');
    });
    document.getElementById('explorerClose').addEventListener('click', () => {
        explorerModal.classList.remove('active');
    });
    explorerModal.addEventListener('click', (e) => {
        if (e.target === explorerModal) explorerModal.classList.remove('active');
    });

    // ============================================================
    //  RENAME TOOL
    // ============================================================

    const renamePath = document.getElementById('renamePath');
    const renameScanBtn = document.getElementById('renameScanBtn');
    const renameTableBody = document.getElementById('renameTableBody');
    const renamePreviewBtn = document.getElementById('renamePreviewBtn');
    const renameExecuteBtn = document.getElementById('renameExecuteBtn');
    const renameResult = document.getElementById('renameResult');

    let renameFiles = [];

    // Scan folder
    renameScanBtn.addEventListener('click', async () => {
        const path = renamePath.value.trim();
        if (!path) { toast('请输入文件夹路径', 'warning'); return; }

        showLoading('正在扫描文件夹...');
        try {
            const data = await API.post('/api/rename/scan', { folder_path: path });
            renameFiles = data.files;
            renderRenameTable(data.files);
            activateStep('panel-rename', 2);
            toast(`找到 ${data.count} 个文件`, 'success');
        } catch (e) {
            toast(e.message, 'error');
        } finally {
            hideLoading();
        }
    });

    function renderRenameTable(files) {
        if (!files || files.length === 0) {
            renameTableBody.innerHTML = '<tr><td colspan="8" class="empty-msg">未找到支持的文件</td></tr>';
            return;
        }

        try {
            const sepEl = document.getElementById('renameSeparator');
            const sep = sepEl ? (sepEl.value || ' ') : ' ';

            renameTableBody.innerHTML = files.map((f, i) => {
                return `<tr>
                    <td>${i + 1}</td>
                    <td title="${escHtml(f.name)}">${escHtml(f.name)}</td>
                    <td>${escHtml(f.ext)}</td>
                    <td><input type="text" class="sub-input sub1" data-ext="${escHtml(f.ext)}" data-original="${escHtml(f.name)}" value="" placeholder="子名1" style="width:100%"></td>
                    <td><input type="text" class="sub-input sub2" data-ext="${escHtml(f.ext)}" data-original="${escHtml(f.name)}" value="" placeholder="子名2" style="width:100%"></td>
                    <td><input type="text" class="sub-input sub3" data-ext="${escHtml(f.ext)}" data-original="${escHtml(f.name)}" value="" placeholder="子名3" style="width:100%"></td>
                    <td><input type="text" class="sep-input" value="${escHtml(sep)}" style="width:100%;text-align:center" maxlength="5"></td>
                    <td><span class="generated-name" style="font-size:13px;color:var(--gray-600)">${escHtml(f.name)}</span></td>
                </tr>`;
            }).join('');

            renameTableBody.querySelectorAll('.sub-input, .sep-input').forEach(inp => {
                inp.addEventListener('input', updateGeneratedNames);
                inp.addEventListener('keydown', renameInputKeydown);
            });

            const sepEl2 = document.getElementById('renameSeparator');
            if (sepEl2) sepEl2.addEventListener('input', updateGeneratedNames);
        } catch (e) {
            console.error('renderRenameTable error:', e);
            toast('渲染表格出错: ' + e.message, 'error');
        }
    }

    function renameInputKeydown(e) {
        if (e.key === 'Enter') {
            const all = renameTableBody.querySelectorAll('.sub-input, .sep-input');
            const idx = Array.from(all).indexOf(e.target);
            if (idx >= 0 && idx < all.length - 1) all[idx + 1].focus();
        }
    }

    function updateGeneratedNames() {
        try {
            const rows = renameTableBody.querySelectorAll('tr');
            const sepEl = document.getElementById('renameSeparator');
            const globalSep = sepEl ? (sepEl.value || ' ') : ' ';

            rows.forEach(tr => {
                const sub1 = tr.querySelector('.sub1');
                const nameSpan = tr.querySelector('.generated-name');
                if (!sub1 || !nameSpan) return;

                const ext = sub1.dataset.ext;
                const original = sub1.dataset.original;

                const sub2 = tr.querySelector('.sub2');
                const sub3 = tr.querySelector('.sub3');
                const sepInp = tr.querySelector('.sep-input');
                const sep = sepInp ? (sepInp.value || globalSep) : globalSep;

                const subs = [];
                [sub1, sub2, sub3].forEach(s => {
                    if (!s) return;
                    const val = s.value.trim();
                    if (val) subs.push(val);
                });

                nameSpan.textContent = subs.length > 0 ? subs.join(sep) + ext : original;
            });
        } catch (e) {
            console.error('updateGeneratedNames error:', e);
        }
    }

    function getRenameRules() {
        const rows = renameTableBody.querySelectorAll('tr');
        const rules = [];
        rows.forEach(tr => {
            const nameSpan = tr.querySelector('.generated-name');
            const original = tr.querySelector('.sub1');
            if (!nameSpan || !original) return;
            const newName = nameSpan.textContent;
            rules.push({
                original: original.dataset.original,
                new_name: newName || original.dataset.original,
            });
        });
        return rules;
    }

    // Preview
    renamePreviewBtn.addEventListener('click', async () => {
        const path = renamePath.value.trim();
        if (!path) { toast('请先扫描文件夹', 'warning'); return; }

        const rules = getRenameRules();
        const validRules = rules.filter(r => r.new_name);
        if (validRules.length === 0) { toast('请先填写新文件名', 'warning'); return; }

        showLoading('正在生成预览...');
        try {
            const data = await API.post('/api/rename/execute', { folder_path: path, rules, dry_run: true });
            renderRenameResult(data);
            activateStep('panel-rename', 3);
            activateStep('panel-rename', 2); // keep step 2 active too
            toast(`预览完成，${data.success} 个文件可重命名`, 'info');
        } catch (e) {
            toast(e.message, 'error');
        } finally {
            hideLoading();
        }
    });

    // Execute
    renameExecuteBtn.addEventListener('click', async () => {
        const path = renamePath.value.trim();
        if (!path) { toast('请先扫描文件夹', 'warning'); return; }

        const rules = getRenameRules();
        const validRules = rules.filter(r => r.new_name);
        if (validRules.length === 0) { toast('请先填写新文件名', 'warning'); return; }

        if (!confirm(`确认要重命名 ${validRules.length} 个文件吗？\n\n重命名操作将复制文件到 "result" 文件夹。`)) return;

        showLoading('正在执行重命名...');
        try {
            const data = await API.post('/api/rename/execute', { folder_path: path, rules, dry_run: false });
            renderRenameResult(data);
            activateStep('panel-rename', 3);
            activateStep('panel-rename', 2);
            if (data.error === 0) {
                toast(`重命名完成！成功 ${data.success} 个`, 'success');
            } else {
                toast(`重命名完成：成功 ${data.success}，失败 ${data.error}`, data.error > 0 ? 'warning' : 'success');
            }
        } catch (e) {
            toast(e.message, 'error');
        } finally {
            hideLoading();
        }
    });

    function renderRenameResult(data) {
        const dryRun = data.dry_run;
        const statusLabel = dryRun ? '预览' : '结果';

        let statsHtml = `
            <div class="result-stats">
                <span class="stat-item success">✅ 成功: ${data.success}</span>
                <span class="stat-item skip">⏭️ 跳过: ${data.skip}</span>
                <span class="stat-item error">❌ 失败: ${data.error}</span>
                <span class="stat-item info">📊 总计: ${data.total}</span>
            </div>`;

        let tableRows = data.details.map((d, i) => {
            let badge = '';
            if (d.status === 'success' || d.status === 'preview-ok') badge = '<span style="color:var(--success)">✅</span>';
            else if (d.status === 'skip') badge = '<span style="color:var(--warning)">⏭️</span>';
            else badge = '<span style="color:var(--danger)">❌</span>';
            const msg = d.message ? ` <span style="color:var(--gray-400);font-size:12px">(${escHtml(d.message)})</span>` : '';
            return `<tr><td>${i+1}</td><td>${escHtml(d.original)}</td><td>${escHtml(d.new_name)}</td><td>${badge} ${d.status}${msg}</td></tr>`;
        }).join('');

        renameResult.innerHTML = statsHtml + `
            <div class="result-table-wrap">
                <table class="data-table">
                    <thead><tr><th>#</th><th>原文件名</th><th>新文件名</th><th>状态</th></tr></thead>
                    <tbody>${tableRows || '<tr><td colspan="4" class="empty-msg">无数据</td></tr>'}</tbody>
                </table>
            </div>
            ${dryRun ? '<p style="margin-top:10px;font-size:13px;color:var(--gray-400)">💡 这是试运行预览，未实际执行。确认无误后点击"执行重命名"。</p>' : ''}`;
    }

    // ============================================================
    //  CHECK TOOL
    // ============================================================

    const checkPath = document.getElementById('checkPath');
    const checkScanBtn = document.getElementById('checkScanBtn');
    const checkTableBody = document.getElementById('checkTableBody');
    const checkExecuteBtn = document.getElementById('checkExecuteBtn');
    const checkClearBtn = document.getElementById('checkClearBtn');
    const checkResult = document.getElementById('checkResult');
    const checkStats = document.getElementById('checkStats');
    const checkComStatus = document.getElementById('checkComStatus');
    const checkGlobalRegex = document.getElementById('checkGlobalRegex');
    const checkApplyGlobal = document.getElementById('checkApplyGlobal');

    let checkFiles = [];

    // Scan folder
    checkScanBtn.addEventListener('click', async () => {
        const path = checkPath.value.trim();
        if (!path) { toast('请输入文件夹路径', 'warning'); return; }

        showLoading('正在扫描文件夹...');
        try {
            const data = await API.post('/api/check/scan', { folder_path: path });
            checkFiles = data.files;

            // COM status
            if (!data.com_available) {
                checkComStatus.innerHTML = '⚠️ win32com 不可用，检查功能需要安装 pywin32 并确保 WPS 或 Word 可用';
                checkComStatus.style.color = 'var(--danger)';
            } else {
                checkComStatus.innerHTML = '✅ WPS COM 接口可用';
                checkComStatus.style.color = 'var(--success)';
            }

            renderCheckTable(data.files);
            activateStep('panel-check', 2);
            toast(`找到 ${data.count} 个 Word 文件`, 'success');
        } catch (e) {
            toast(e.message, 'error');
        } finally {
            hideLoading();
        }
    });

    function renderCheckTable(files) {
        if (!files || files.length === 0) {
            checkTableBody.innerHTML = '<tr><td colspan="3" class="empty-msg">未找到 Word 文件</td></tr>';
            return;
        }
        checkTableBody.innerHTML = files.map((f, i) => `
            <tr>
                <td>${i + 1}</td>
                <td>${escHtml(f.name)}</td>
                <td><input type="text" class="editable-input regex-input" data-file="${escHtml(f.name)}" placeholder="输入正则表达式" style="font-family:monospace"></td>
            </tr>
        `).join('');
    }

    // Apply global regex to all
    checkApplyGlobal.addEventListener('click', () => {
        const globalRegex = checkGlobalRegex.value.trim();
        if (!globalRegex) { toast('请先输入全局正则表达式', 'warning'); return; }
        checkTableBody.querySelectorAll('.regex-input').forEach(inp => {
            inp.value = globalRegex;
            inp.classList.add('changed');
        });
        toast('已应用到所有文件', 'info');
    });

    // Execute check
    checkExecuteBtn.addEventListener('click', async () => {
        const path = checkPath.value.trim();
        if (!path) { toast('请先扫描文件夹', 'warning'); return; }

        // Collect patterns
        const patterns = {};
        checkTableBody.querySelectorAll('.regex-input').forEach(inp => {
            const val = inp.value.trim();
            if (val) patterns[inp.dataset.file] = val;
        });

        if (Object.keys(patterns).length === 0) { toast('请填写至少一个正则表达式', 'warning'); return; }

        showLoading('正在检查文档，请稍候...');
        try {
            const data = await API.post('/api/check/execute', { folder_path: path, patterns });
            renderCheckResult(data);
            activateStep('panel-check', 3);
            toast(`检查完成，共 ${data.results.length} 条匹配`, 'success');
        } catch (e) {
            toast(e.message, 'error');
        } finally {
            hideLoading();
        }
    });

    function renderCheckResult(data) {
        const stats = data.stats || {};
        checkStats.innerHTML = `
            <div class="result-stats">
                <span class="stat-item success">✅ 有匹配: ${stats.success}</span>
                <span class="stat-item skip">⏭️ 无匹配/跳过: ${stats.skip}</span>
                <span class="stat-item error">❌ 错误: ${stats.error}</span>
                <span class="stat-item info">📄 文件总数: ${stats.total}</span>
            </div>`;

        const results = data.results || [];
        const debug = data.debug || [];
        if (results.length === 0) {
            let debugHtml = '';
            if (debug.length > 0) {
                debugHtml = '<div style="margin-top:12px;padding:12px;background:var(--gray-50);border-radius:var(--radius);font-size:13px;font-family:monospace;white-space:pre-wrap;color:var(--gray-600);max-height:200px;overflow:auto">' + escHtml(debug.join('\n')) + '</div>';
            }
            checkResult.innerHTML = '<div class="empty-msg" style="text-align:center;padding:30px;color:var(--gray-400)">未找到匹配内容</div>' + debugHtml;
            return;
        }

        let rows = results.map((r, i) => `
            <tr>
                <td>${i + 1}</td>
                <td>${escHtml(r.file)}</td>
                <td>${r.page ? '<span class="stat-item info" style="padding:2px 8px;font-size:12px">第' + r.page + '页</span>' : '-'}</td>
                <td style="font-family:monospace;font-size:13px;max-width:400px;word-break:break-all">${escHtml(r.text)}</td>
            </tr>
        `).join('');

        checkResult.innerHTML = `
            <div class="result-table-wrap">
                <table class="data-table">
                    <thead><tr><th>#</th><th>文件名</th><th>页码</th><th>匹配内容</th></tr></thead>
                    <tbody>${rows}</tbody>
                </table>
                <div style="padding:8px 14px;font-size:13px;color:var(--gray-400);border-top:1px solid var(--gray-200)">
                    共 ${results.length} 条匹配结果
                </div>
            </div>`;
    }

    // Clear results
    checkClearBtn.addEventListener('click', () => {
        checkResult.innerHTML = '';
        checkStats.innerHTML = '';
        toast('结果已清空', 'info');
    });

    // ============================================================
    //  SORT TOOL
    // ============================================================

    const sortRefPath = document.getElementById('sortRefPath');
    const sortTargetPath = document.getElementById('sortTargetPath');
    const sortRefLoadBtn = document.getElementById('sortRefLoadBtn');
    const sortTargetLoadBtn = document.getElementById('sortTargetLoadBtn');
    const sortRefInfo = document.getElementById('sortRefInfo');
    const sortTargetInfo = document.getElementById('sortTargetInfo');
    const sortRefColumn = document.getElementById('sortRefColumn');
    const sortMatchColumn = document.getElementById('sortMatchColumn');
    const sortRefColumnRow = document.getElementById('sortRefColumnRow');
    const sortTargetColumnRow = document.getElementById('sortTargetColumnRow');
    const sortFuzzy = document.getElementById('sortFuzzy');
    const sortKeepUnmatched = document.getElementById('sortKeepUnmatched');
    const sortExecuteBtn = document.getElementById('sortExecuteBtn');
    const sortResult = document.getElementById('sortResult');
    const sortStats = document.getElementById('sortStats');

    let sortRefColumns = [];
    let sortTargetColumns = [];
    let sortResultId = null;

    // Load reference file columns
    sortRefLoadBtn.addEventListener('click', async () => {
        const path = sortRefPath.value.trim();
        if (!path) { toast('请输入参照文件路径', 'warning'); return; }

        showLoading('读取参照文件...');
        try {
            const data = await API.post('/api/sort/columns', { file_path: path });
            sortRefColumns = data.columns;
            populateSelect(sortRefColumn, data.columns);
            sortRefColumnRow.hidden = false;
            sortRefInfo.textContent = `✅ 已读取，共 ${data.columns.length} 列`;
            activateStep('panel-sort', 2);
            toast('参照文件读取成功', 'success');
        } catch (e) {
            toast(e.message, 'error');
        } finally {
            hideLoading();
        }
    });

    // Load target file columns
    sortTargetLoadBtn.addEventListener('click', async () => {
        const path = sortTargetPath.value.trim();
        if (!path) { toast('请输入目标文件路径', 'warning'); return; }

        showLoading('读取目标文件...');
        try {
            const data = await API.post('/api/sort/columns', { file_path: path });
            sortTargetColumns = data.columns;
            populateSelect(sortMatchColumn, data.columns);
            sortTargetColumnRow.hidden = false;
            sortTargetInfo.textContent = `✅ 已读取，共 ${data.columns.length} 列`;
            toast('目标文件读取成功', 'success');
        } catch (e) {
            toast(e.message, 'error');
        } finally {
            hideLoading();
        }
    });

    function populateSelect(select, options) {
        select.innerHTML = options.map((opt, i) =>
            `<option value="${escHtml(opt)}">${escHtml(opt)}</option>`
        ).join('');
    }

    // Execute sort
    sortExecuteBtn.addEventListener('click', async () => {
        const refFile = sortRefPath.value.trim();
        const targetFile = sortTargetPath.value.trim();
        const refColumn = sortRefColumn.value;
        const matchColumn = sortMatchColumn.value;

        if (!refFile || !targetFile) { toast('请先选择参照文件和目标文件', 'warning'); return; }
        if (!refColumn || !matchColumn) { toast('请选择参照列和匹配列', 'warning'); return; }

        showLoading('正在执行排序...');
        try {
            const data = await API.post('/api/sort/execute', {
                ref_file: refFile,
                target_file: targetFile,
                ref_column: refColumn,
                match_column: matchColumn,
                fuzzy: sortFuzzy.checked,
                keep_unmatched: sortKeepUnmatched.checked,
            });
            sortResultId = data.result_id;
            renderSortResult(data);
            activateStep('panel-sort', 3);
            toast(`排序完成！共 ${data.total_rows} 行`, 'success');
        } catch (e) {
            toast(e.message, 'error');
        } finally {
            hideLoading();
        }
    });

    function renderSortResult(data) {
        sortStats.innerHTML = `
            <div class="result-stats">
                <span class="stat-item info">📊 共 ${data.total_rows} 行</span>
                <span class="stat-item info">📋 ${data.columns.length} 列</span>
                ${data.truncated ? '<span class="stat-item warning">⚠️ 仅显示前 200 行</span>' : ''}
            </div>`;

        // Download button
        const downloadLink = document.createElement('a');
        downloadLink.href = `/api/sort/download/${sortResultId}`;
        downloadLink.className = 'download-btn';
        downloadLink.textContent = '⬇️ 下载 Excel 文件';
        downloadLink.style.marginBottom = '12px';
        downloadLink.style.display = 'inline-block';

        if (data.data && data.data.length > 0) {
            // Render table
            const cols = data.columns;
            const thead = cols.map(c => `<th>${escHtml(c)}</th>`).join('');
            const rows = data.data.map((row, i) => {
                const tds = cols.map(c => {
                    const val = row[c] !== undefined && row[c] !== null ? String(row[c]) : '';
                    return `<td title="${escHtml(val)}">${escHtml(val)}</td>`;
                }).join('');
                return `<tr><td>${i + 1}</td>${tds}</tr>`;
            }).join('');

            sortResult.innerHTML = '';
            sortResult.appendChild(downloadLink);
            sortResult.insertAdjacentHTML('beforeend', `
                <div class="result-table-wrap">
                    <table class="data-table">
                        <thead><tr><th>#</th>${thead}</tr></thead>
                        <tbody>${rows || '<tr><td colspan="' + (cols.length + 1) + '" class="empty-msg">无数据</td></tr>'}</tbody>
                    </table>
                </div>`);
        } else {
            sortResult.innerHTML = '';
            sortResult.appendChild(downloadLink);
            sortResult.insertAdjacentHTML('beforeend', '<div style="padding:20px;text-align:center;color:var(--gray-400)">排序结果为空</div>');
        }
    }

    // ============================================================
    //  Step Activation Helper
    // ============================================================

    function activateStep(panelId, stepNum) {
        const panel = document.getElementById(panelId);
        if (!panel) return;
        const steps = panel.querySelectorAll('.step');
        steps.forEach(s => {
            const num = parseInt(s.dataset.step, 10);
            s.classList.toggle('active', num === stepNum);
            if (num < stepNum) s.classList.add('completed');
        });
    }

    // ============================================================
    //  Keyboard shortcuts: Enter to execute main action
    // ============================================================

    // Enter on path inputs triggers scan
    renamePath.addEventListener('keydown', (e) => { if (e.key === 'Enter') renameScanBtn.click(); });
    checkPath.addEventListener('keydown', (e) => { if (e.key === 'Enter') checkScanBtn.click(); });

    console.log('🔧 文档处理工具已加载');
})();
