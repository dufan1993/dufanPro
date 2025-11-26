"""
测试系统后端API
提供测试用例管理和测试任务管理的RESTful API
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__, static_folder='static')
CORS(app)

# 数据存储文件
TEST_CASES_FILE = 'data/test_cases.json'
TEST_TASKS_FILE = 'data/test_tasks.json'

# 确保数据目录存在
os.makedirs('data', exist_ok=True)
os.makedirs('static', exist_ok=True)


def load_json_file(filename, default=[]):
    """加载JSON文件"""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default


def save_json_file(filename, data):
    """保存JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ==================== 测试用例管理 API ====================

@app.route('/api/test-cases', methods=['GET'])
def get_test_cases():
    """获取所有测试用例"""
    test_cases = load_json_file(TEST_CASES_FILE)
    return jsonify(test_cases)


@app.route('/api/test-cases', methods=['POST'])
def create_test_case():
    """创建新测试用例"""
    data = request.json
    test_cases = load_json_file(TEST_CASES_FILE)
    
    # 生成ID
    new_id = str(max([int(tc.get('id', 0)) for tc in test_cases] + [0]) + 1)
    
    test_case = {
        'id': new_id,
        'name': data.get('name', ''),
        'description': data.get('description', ''),
        'priority': data.get('priority', '中'),
        'status': data.get('status', '待执行'),
        'steps': data.get('steps', []),
        'expected_result': data.get('expected_result', ''),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    test_cases.append(test_case)
    save_json_file(TEST_CASES_FILE, test_cases)
    return jsonify(test_case), 201


@app.route('/api/test-cases/<test_case_id>', methods=['PUT'])
def update_test_case(test_case_id):
    """更新测试用例"""
    data = request.json
    test_cases = load_json_file(TEST_CASES_FILE)
    
    for i, tc in enumerate(test_cases):
        if tc['id'] == test_case_id:
            test_cases[i].update({
                'name': data.get('name', tc['name']),
                'description': data.get('description', tc['description']),
                'priority': data.get('priority', tc['priority']),
                'status': data.get('status', tc['status']),
                'steps': data.get('steps', tc['steps']),
                'expected_result': data.get('expected_result', tc['expected_result']),
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            save_json_file(TEST_CASES_FILE, test_cases)
            return jsonify(test_cases[i])
    
    return jsonify({'error': '测试用例未找到'}), 404


@app.route('/api/test-cases/<test_case_id>', methods=['DELETE'])
def delete_test_case(test_case_id):
    """删除测试用例"""
    test_cases = load_json_file(TEST_CASES_FILE)
    test_cases = [tc for tc in test_cases if tc['id'] != test_case_id]
    save_json_file(TEST_CASES_FILE, test_cases)
    return jsonify({'message': '删除成功'}), 200


# ==================== 测试任务管理 API ====================

@app.route('/api/test-tasks', methods=['GET'])
def get_test_tasks():
    """获取所有测试任务"""
    test_tasks = load_json_file(TEST_TASKS_FILE)
    return jsonify(test_tasks)


@app.route('/api/test-tasks', methods=['POST'])
def create_test_task():
    """创建新测试任务"""
    data = request.json
    test_tasks = load_json_file(TEST_TASKS_FILE)
    
    # 生成ID
    new_id = str(max([int(tt.get('id', 0)) for tt in test_tasks] + [0]) + 1)
    
    test_task = {
        'id': new_id,
        'name': data.get('name', ''),
        'description': data.get('description', ''),
        'test_case_ids': data.get('test_case_ids', []),
        'status': data.get('status', '待执行'),
        'assignee': data.get('assignee', ''),
        'due_date': data.get('due_date', ''),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    test_tasks.append(test_task)
    save_json_file(TEST_TASKS_FILE, test_tasks)
    return jsonify(test_task), 201


@app.route('/api/test-tasks/<task_id>', methods=['PUT'])
def update_test_task(task_id):
    """更新测试任务"""
    data = request.json
    test_tasks = load_json_file(TEST_TASKS_FILE)
    
    for i, tt in enumerate(test_tasks):
        if tt['id'] == task_id:
            test_tasks[i].update({
                'name': data.get('name', tt['name']),
                'description': data.get('description', tt['description']),
                'test_case_ids': data.get('test_case_ids', tt['test_case_ids']),
                'status': data.get('status', tt['status']),
                'assignee': data.get('assignee', tt['assignee']),
                'due_date': data.get('due_date', tt['due_date']),
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            save_json_file(TEST_TASKS_FILE, test_tasks)
            return jsonify(test_tasks[i])
    
    return jsonify({'error': '测试任务未找到'}), 404


@app.route('/api/test-tasks/<task_id>', methods=['DELETE'])
def delete_test_task(task_id):
    """删除测试任务"""
    test_tasks = load_json_file(TEST_TASKS_FILE)
    test_tasks = [tt for tt in test_tasks if tt['id'] != task_id]
    save_json_file(TEST_TASKS_FILE, test_tasks)
    return jsonify({'message': '删除成功'}), 200


# ==================== 静态文件服务 ====================

@app.route('/')
def index():
    """返回主页面"""
    return send_from_directory('static', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """提供静态文件服务"""
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
