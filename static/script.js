// API基础URL
const API_BASE = '/api';

// 全局状态
let testCases = [];
let testTasks = [];
let filteredTestCases = null;
let filteredTestTasks = null;

// ==================== 初始化 ====================

document.addEventListener('DOMContentLoaded', function() {
    initTabs();
    loadTestCases();
    loadTestTasks();
    setupFilters();
    initToast();
});

// ==================== Toast通知 ====================

function initToast() {
    if (!document.getElementById('toast-container')) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function showSuccess(message) {
    showToast(message, 'success');
}

function showError(message) {
    showToast(message, 'error');
}

// ==================== 标签页切换 ====================

function initTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            switchTab(btn.getAttribute('data-tab'));
        });
    });
}

function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    document.querySelectorAll('.panel').forEach(panel => panel.classList.remove('active'));
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

function renderTestCases(cases = null) {
    const data = cases || filteredTestCases || testCases;
    const tbody = document.getElementById('test-cases-table-body');
    
    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state">暂无数据</td></tr>';
        return;
    }

    tbody.innerHTML = data.map(tc => `
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
    const modal = document.getElementById('test-case-modal');
    const title = document.getElementById('test-case-modal-title');
    const form = document.getElementById('test-case-form');
    
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
        form.reset();
        document.getElementById('test-case-id').value = '';
    }
    
    modal.classList.add('active');
}

function closeTestCaseModal() {
    document.getElementById('test-case-modal').classList.remove('active');
}

async function saveTestCase() {
    const form = document.getElementById('test-case-form');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const id = document.getElementById('test-case-id').value;
    const data = {
        name: document.getElementById('test-case-name').value,
        description: document.getElementById('test-case-description').value,
        priority: document.getElementById('test-case-priority').value,
        status: document.getElementById('test-case-status').value,
        steps: document.getElementById('test-case-steps').value
            .split('\n')
            .map(s => s.trim())
            .filter(s => s),
        expected_result: document.getElementById('test-case-expected-result').value
    };

    try {
        const url = id ? `${API_BASE}/test-cases/${id}` : `${API_BASE}/test-cases`;
        const method = id ? 'PUT' : 'POST';
        
        await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        closeTestCaseModal();
        loadTestCases();
        showSuccess(id ? '更新成功' : '创建成功');
    } catch (error) {
        console.error('保存失败:', error);
        showError('保存失败');
    }
}

async function deleteTestCase(id) {
    if (!confirm('确定要删除这个测试用例吗？')) return;

    try {
        await fetch(`${API_BASE}/test-cases/${id}`, { method: 'DELETE' });
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

function renderTestTasks(tasks = null) {
    const data = tasks || filteredTestTasks || testTasks;
    const tbody = document.getElementById('test-tasks-table-body');
    
    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty-state">暂无数据</td></tr>';
        return;
    }

    tbody.innerHTML = data.map(tt => `
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
    const modal = document.getElementById('test-task-modal');
    const title = document.getElementById('test-task-modal-title');
    const form = document.getElementById('test-task-form');
    
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
        form.reset();
        document.getElementById('test-task-id').value = '';
    }
    
    modal.classList.add('active');
}

function closeTestTaskModal() {
    document.getElementById('test-task-modal').classList.remove('active');
}

async function saveTestTask() {
    const form = document.getElementById('test-task-form');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const id = document.getElementById('test-task-id').value;
    const caseIdsStr = document.getElementById('test-task-case-ids').value;
    
    const data = {
        name: document.getElementById('test-task-name').value,
        description: document.getElementById('test-task-description').value,
        assignee: document.getElementById('test-task-assignee').value,
        due_date: document.getElementById('test-task-due-date').value,
        status: document.getElementById('test-task-status').value,
        test_case_ids: caseIdsStr ? caseIdsStr.split(',').map(id => id.trim()).filter(id => id) : []
    };

    try {
        const url = id ? `${API_BASE}/test-tasks/${id}` : `${API_BASE}/test-tasks`;
        const method = id ? 'PUT' : 'POST';
        
        await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        closeTestTaskModal();
        loadTestTasks();
        showSuccess(id ? '更新成功' : '创建成功');
    } catch (error) {
        console.error('保存失败:', error);
        showError('保存失败');
    }
}

async function deleteTestTask(id) {
    if (!confirm('确定要删除这个测试任务吗？')) return;

    try {
        await fetch(`${API_BASE}/test-tasks/${id}`, { method: 'DELETE' });
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

// ==================== 筛选功能（简化版） ====================

function setupFilters() {
    // 测试用例筛选
    const search = document.getElementById('test-case-search');
    const statusFilter = document.getElementById('test-case-status-filter');
    const priorityFilter = document.getElementById('test-case-priority-filter');
    
    [search, statusFilter, priorityFilter].forEach(el => {
        if (el) el.addEventListener('input', filterTestCases);
    });

    // 测试任务筛选
    const taskSearch = document.getElementById('test-task-search');
    const taskStatusFilter = document.getElementById('test-task-status-filter');
    
    [taskSearch, taskStatusFilter].forEach(el => {
        if (el) el.addEventListener('input', filterTestTasks);
    });
}

function filterTestCases() {
    const searchTerm = document.getElementById('test-case-search').value.toLowerCase();
    const statusFilter = document.getElementById('test-case-status-filter').value;
    const priorityFilter = document.getElementById('test-case-priority-filter').value;

    filteredTestCases = testCases.filter(tc => {
        const matchSearch = !searchTerm || 
            tc.name.toLowerCase().includes(searchTerm) ||
            (tc.description && tc.description.toLowerCase().includes(searchTerm));
        const matchStatus = !statusFilter || tc.status === statusFilter;
        const matchPriority = !priorityFilter || tc.priority === priorityFilter;
        return matchSearch && matchStatus && matchPriority;
    });

    renderTestCases(filteredTestCases);
}

function filterTestTasks() {
    const searchTerm = document.getElementById('test-task-search').value.toLowerCase();
    const statusFilter = document.getElementById('test-task-status-filter').value;

    filteredTestTasks = testTasks.filter(tt => {
        const matchSearch = !searchTerm || 
            tt.name.toLowerCase().includes(searchTerm) ||
            (tt.description && tt.description.toLowerCase().includes(searchTerm));
        const matchStatus = !statusFilter || tt.status === statusFilter;
        return matchSearch && matchStatus;
    });

    renderTestTasks(filteredTestTasks);
}

// ==================== 工具函数 ====================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 点击模态框外部关闭
window.onclick = function(event) {
    const modals = ['test-case-modal', 'test-task-modal'];
    modals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (event.target === modal) {
            modal.classList.remove('active');
        }
    });
}
