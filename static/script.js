// API基础URL
const API_BASE = '/api';

// 全局状态
let testCases = [];
let testTasks = [];
let currentEditingTestCaseId = null;
let currentEditingTaskId = null;

// ==================== 初始化 ====================

document.addEventListener('DOMContentLoaded', function() {
    initTabs();
    loadTestCases();
    loadTestTasks();
    setupFilters();
});

// ==================== 标签页切换 ====================

function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // 更新按钮状态
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // 更新面板显示
    document.querySelectorAll('.panel').forEach(panel => {
        panel.classList.remove('active');
    });
    document.getElementById(`${tabName}-panel`).classList.add('active');
}

// ==================== 测试用例管理 ====================

async function loadTestCases() {
    try {
        const response = await fetch(`${API_BASE}/test-cases`);
        testCases = await response.json();
        renderTestCases();
    } catch (error) {
        console.error('加载测试用例失败:', error);
        showError('加载测试用例失败');
    }
}

function renderTestCases() {
    const tbody = document.getElementById('test-cases-table-body');
    
    if (testCases.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading">暂无测试用例</td></tr>';
        return;
    }

    tbody.innerHTML = testCases.map(tc => `
        <tr>
            <td>${tc.id}</td>
            <td>${escapeHtml(tc.name)}</td>
            <td>${escapeHtml(tc.description || '-')}</td>
            <td><span class="priority-badge priority-${tc.priority}">${tc.priority}</span></td>
            <td><span class="status-badge status-${tc.status}">${tc.status}</span></td>
            <td>${tc.created_at || '-'}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-edit" onclick="editTestCase('${tc.id}')">编辑</button>
                    <button class="btn btn-danger" onclick="deleteTestCase('${tc.id}')">删除</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function openTestCaseModal(testCaseId = null) {
    currentEditingTestCaseId = testCaseId;
    const modal = document.getElementById('test-case-modal');
    const title = document.getElementById('test-case-modal-title');
    
    if (testCaseId) {
        title.textContent = '编辑测试用例';
        const testCase = testCases.find(tc => tc.id === testCaseId);
        if (testCase) {
            document.getElementById('test-case-id').value = testCase.id;
            document.getElementById('test-case-name').value = testCase.name;
            document.getElementById('test-case-description').value = testCase.description || '';
            document.getElementById('test-case-priority').value = testCase.priority;
            document.getElementById('test-case-status').value = testCase.status;
            document.getElementById('test-case-steps').value = Array.isArray(testCase.steps) 
                ? testCase.steps.join('\n') 
                : (testCase.steps || '');
            document.getElementById('test-case-expected-result').value = testCase.expected_result || '';
        }
    } else {
        title.textContent = '新建测试用例';
        document.getElementById('test-case-form').reset();
        document.getElementById('test-case-id').value = '';
    }
    
    modal.classList.add('active');
}

function closeTestCaseModal() {
    document.getElementById('test-case-modal').classList.remove('active');
    currentEditingTestCaseId = null;
}

async function saveTestCase() {
    const form = document.getElementById('test-case-form');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const id = document.getElementById('test-case-id').value;
    const steps = document.getElementById('test-case-steps').value
        .split('\n')
        .map(s => s.trim())
        .filter(s => s);

    const data = {
        name: document.getElementById('test-case-name').value,
        description: document.getElementById('test-case-description').value,
        priority: document.getElementById('test-case-priority').value,
        status: document.getElementById('test-case-status').value,
        steps: steps,
        expected_result: document.getElementById('test-case-expected-result').value
    };

    try {
        if (id) {
            // 更新
            await fetch(`${API_BASE}/test-cases/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        } else {
            // 创建
            await fetch(`${API_BASE}/test-cases`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        }
        
        closeTestCaseModal();
        loadTestCases();
        showSuccess(id ? '更新成功' : '创建成功');
    } catch (error) {
        console.error('保存失败:', error);
        showError('保存失败');
    }
}

async function deleteTestCase(id) {
    if (!confirm('确定要删除这个测试用例吗？')) {
        return;
    }

    try {
        await fetch(`${API_BASE}/test-cases/${id}`, {
            method: 'DELETE'
        });
        loadTestCases();
        showSuccess('删除成功');
    } catch (error) {
        console.error('删除失败:', error);
        showError('删除失败');
    }
}

function editTestCase(id) {
    openTestCaseModal(id);
}

// ==================== 测试任务管理 ====================

async function loadTestTasks() {
    try {
        const response = await fetch(`${API_BASE}/test-tasks`);
        testTasks = await response.json();
        renderTestTasks();
    } catch (error) {
        console.error('加载测试任务失败:', error);
        showError('加载测试任务失败');
    }
}

function renderTestTasks() {
    const tbody = document.getElementById('test-tasks-table-body');
    
    if (testTasks.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="loading">暂无测试任务</td></tr>';
        return;
    }

    tbody.innerHTML = testTasks.map(tt => `
        <tr>
            <td>${tt.id}</td>
            <td>${escapeHtml(tt.name)}</td>
            <td>${escapeHtml(tt.description || '-')}</td>
            <td>${Array.isArray(tt.test_case_ids) ? tt.test_case_ids.length : 0}</td>
            <td>${escapeHtml(tt.assignee || '-')}</td>
            <td><span class="status-badge status-${tt.status}">${tt.status}</span></td>
            <td>${tt.due_date || '-'}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-edit" onclick="editTestTask('${tt.id}')">编辑</button>
                    <button class="btn btn-danger" onclick="deleteTestTask('${tt.id}')">删除</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function openTestTaskModal(taskId = null) {
    currentEditingTaskId = taskId;
    const modal = document.getElementById('test-task-modal');
    const title = document.getElementById('test-task-modal-title');
    
    if (taskId) {
        title.textContent = '编辑测试任务';
        const task = testTasks.find(tt => tt.id === taskId);
        if (task) {
            document.getElementById('test-task-id').value = task.id;
            document.getElementById('test-task-name').value = task.name;
            document.getElementById('test-task-description').value = task.description || '';
            document.getElementById('test-task-assignee').value = task.assignee || '';
            document.getElementById('test-task-due-date').value = task.due_date || '';
            document.getElementById('test-task-status').value = task.status;
            document.getElementById('test-task-case-ids').value = Array.isArray(task.test_case_ids) 
                ? task.test_case_ids.join(',') 
                : '';
        }
    } else {
        title.textContent = '新建测试任务';
        document.getElementById('test-task-form').reset();
        document.getElementById('test-task-id').value = '';
    }
    
    modal.classList.add('active');
}

function closeTestTaskModal() {
    document.getElementById('test-task-modal').classList.remove('active');
    currentEditingTaskId = null;
}

async function saveTestTask() {
    const form = document.getElementById('test-task-form');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const id = document.getElementById('test-task-id').value;
    const caseIdsStr = document.getElementById('test-task-case-ids').value;
    const testCaseIds = caseIdsStr
        ? caseIdsStr.split(',').map(id => id.trim()).filter(id => id)
        : [];

    const data = {
        name: document.getElementById('test-task-name').value,
        description: document.getElementById('test-task-description').value,
        assignee: document.getElementById('test-task-assignee').value,
        due_date: document.getElementById('test-task-due-date').value,
        status: document.getElementById('test-task-status').value,
        test_case_ids: testCaseIds
    };

    try {
        if (id) {
            // 更新
            await fetch(`${API_BASE}/test-tasks/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        } else {
            // 创建
            await fetch(`${API_BASE}/test-tasks`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        }
        
        closeTestTaskModal();
        loadTestTasks();
        showSuccess(id ? '更新成功' : '创建成功');
    } catch (error) {
        console.error('保存失败:', error);
        showError('保存失败');
    }
}

async function deleteTestTask(id) {
    if (!confirm('确定要删除这个测试任务吗？')) {
        return;
    }

    try {
        await fetch(`${API_BASE}/test-tasks/${id}`, {
            method: 'DELETE'
        });
        loadTestTasks();
        showSuccess('删除成功');
    } catch (error) {
        console.error('删除失败:', error);
        showError('删除失败');
    }
}

function editTestTask(id) {
    openTestTaskModal(id);
}

// ==================== 筛选功能 ====================

function setupFilters() {
    // 测试用例筛选
    const testCaseSearch = document.getElementById('test-case-search');
    const testCaseStatusFilter = document.getElementById('test-case-status-filter');
    const testCasePriorityFilter = document.getElementById('test-case-priority-filter');

    [testCaseSearch, testCaseStatusFilter, testCasePriorityFilter].forEach(element => {
        if (element) {
            element.addEventListener('input', filterTestCases);
        }
    });

    // 测试任务筛选
    const testTaskSearch = document.getElementById('test-task-search');
    const testTaskStatusFilter = document.getElementById('test-task-status-filter');

    [testTaskSearch, testTaskStatusFilter].forEach(element => {
        if (element) {
            element.addEventListener('input', filterTestTasks);
        }
    });
}

function filterTestCases() {
    const searchTerm = document.getElementById('test-case-search').value.toLowerCase();
    const statusFilter = document.getElementById('test-case-status-filter').value;
    const priorityFilter = document.getElementById('test-case-priority-filter').value;

    const filtered = testCases.filter(tc => {
        const matchSearch = !searchTerm || 
            tc.name.toLowerCase().includes(searchTerm) ||
            (tc.description && tc.description.toLowerCase().includes(searchTerm));
        const matchStatus = !statusFilter || tc.status === statusFilter;
        const matchPriority = !priorityFilter || tc.priority === priorityFilter;
        
        return matchSearch && matchStatus && matchPriority;
    });

    renderFilteredTestCases(filtered);
}

function renderFilteredTestCases(filteredCases) {
    const tbody = document.getElementById('test-cases-table-body');
    
    if (filteredCases.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading">没有找到匹配的测试用例</td></tr>';
        return;
    }

    tbody.innerHTML = filteredCases.map(tc => `
        <tr>
            <td>${tc.id}</td>
            <td>${escapeHtml(tc.name)}</td>
            <td>${escapeHtml(tc.description || '-')}</td>
            <td><span class="priority-badge priority-${tc.priority}">${tc.priority}</span></td>
            <td><span class="status-badge status-${tc.status}">${tc.status}</span></td>
            <td>${tc.created_at || '-'}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-edit" onclick="editTestCase('${tc.id}')">编辑</button>
                    <button class="btn btn-danger" onclick="deleteTestCase('${tc.id}')">删除</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function filterTestTasks() {
    const searchTerm = document.getElementById('test-task-search').value.toLowerCase();
    const statusFilter = document.getElementById('test-task-status-filter').value;

    const filtered = testTasks.filter(tt => {
        const matchSearch = !searchTerm || 
            tt.name.toLowerCase().includes(searchTerm) ||
            (tt.description && tt.description.toLowerCase().includes(searchTerm));
        const matchStatus = !statusFilter || tt.status === statusFilter;
        
        return matchSearch && matchStatus;
    });

    renderFilteredTestTasks(filtered);
}

function renderFilteredTestTasks(filteredTasks) {
    const tbody = document.getElementById('test-tasks-table-body');
    
    if (filteredTasks.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="loading">没有找到匹配的测试任务</td></tr>';
        return;
    }

    tbody.innerHTML = filteredTasks.map(tt => `
        <tr>
            <td>${tt.id}</td>
            <td>${escapeHtml(tt.name)}</td>
            <td>${escapeHtml(tt.description || '-')}</td>
            <td>${Array.isArray(tt.test_case_ids) ? tt.test_case_ids.length : 0}</td>
            <td>${escapeHtml(tt.assignee || '-')}</td>
            <td><span class="status-badge status-${tt.status}">${tt.status}</span></td>
            <td>${tt.due_date || '-'}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-edit" onclick="editTestTask('${tt.id}')">编辑</button>
                    <button class="btn btn-danger" onclick="deleteTestTask('${tt.id}')">删除</button>
                </div>
            </td>
        </tr>
    `).join('');
}

// ==================== 工具函数 ====================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showSuccess(message) {
    // 简单的成功提示（可以替换为更美观的toast组件）
    alert(message);
}

function showError(message) {
    // 简单的错误提示（可以替换为更美观的toast组件）
    alert('错误: ' + message);
}

// 点击模态框外部关闭
window.onclick = function(event) {
    const testCaseModal = document.getElementById('test-case-modal');
    const testTaskModal = document.getElementById('test-task-modal');
    
    if (event.target === testCaseModal) {
        closeTestCaseModal();
    }
    if (event.target === testTaskModal) {
        closeTestTaskModal();
    }
}
