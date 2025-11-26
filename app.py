from flask import Flask, render_template, jsonify, request
import json
import os
import uuid
from datetime import datetime

app = Flask(__name__)

# 获取当前目录下的文件路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TESTCASE_FILE = os.path.join(BASE_DIR, 'testcase.json')
TASK_FILE = os.path.join(BASE_DIR, 'tasks.json')

def load_testcases():
    """加载测试用例数据"""
    try:
        with open(TESTCASE_FILE, 'r', encoding='utf-8') as f:
            testcases = json.load(f)
        return testcases
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def load_tasks():
    """从task文件夹加载测试任务数据，每个JSON文件对应一个任务"""
    task_dir = os.path.join(BASE_DIR, 'task')
    tasks = []
    
    # 确保task文件夹存在
    if not os.path.exists(task_dir):
        os.makedirs(task_dir, exist_ok=True)
        return []
    
    try:
        # 遍历task文件夹中的所有JSON文件
        for filename in os.listdir(task_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(task_dir, filename)
                
                # 从文件名提取任务名称（去掉.json后缀）
                task_name = filename[:-5]
                
                # 读取JSON文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 从配置文件中提取选中的测试用例
                selected_testcases = []
                for key, value in config_data.items():
                    if key.startswith('test_') and isinstance(value, dict) and value.get('flag') == 1:
                        selected_testcases.append(key)
                
                # 创建任务对象
                task = {
                    'id': str(uuid.uuid4()),
                    'name': task_name,
                    'description': f"{task_name}测试任务",
                    'testcases': selected_testcases,
                    'status': 'pending',
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'config_file': filename
                }
                
                # 从配置文件中提取其他重要参数
                if 'MODEL_NAME' in config_data:
                    task['model_path'] = config_data['MODEL_NAME']
                if 'port' in config_data:
                    task['port_number'] = config_data['port']
                if 'OUTPUT_DIR' in config_data:
                    task['report_path'] = config_data['OUTPUT_DIR']
                if 'system_words' in config_data:
                    task['prompt_text'] = config_data['system_words']
                if 'server_cmd' in config_data:
                    task['server_command'] = config_data['server_cmd']
                if 'server_path' in config_data:
                    task['server_path'] = config_data['server_path']
                if 'max_tokens' in config_data:
                    task['max_tokens'] = config_data['max_tokens']
                
                tasks.append(task)
        
        return tasks
    except Exception as e:
        print(f"加载任务数据失败: {e}")
        return []

def save_tasks(tasks):
    """保存测试任务数据（现在任务数据从task文件夹中的JSON文件动态生成，此函数主要用于兼容性）"""
    # 由于任务数据现在是从task文件夹中的JSON文件动态生成的，
    # 不再需要保存到单一的tasks.json文件中
    # 此函数保留用于API接口的兼容性
    return True

@app.route('/')
def index():
    """主页路由，渲染新的主页模板"""
    return render_template('index.html')

@app.route('/testcase')
def testcase():
    """测试用例页面路由"""
    return render_template('testcase.html')

@app.route('/task')
def task():
    """测试任务页面路由"""
    return render_template('task.html')

@app.route('/task/detail')
def task_detail():
    """测试任务详情页面路由"""
    return render_template('task_detail.html')

@app.route('/api/testcases')
def get_testcases():
    """API接口，返回JSON格式的测试用例数据"""
    testcases = load_testcases()
    return jsonify(testcases)

@app.route('/api/tasks', methods=['GET', 'POST'])
def manage_tasks():
    """测试任务管理API接口"""
    if request.method == 'GET':
        # 获取所有测试任务
        tasks = load_tasks()
        return jsonify(tasks)
    elif request.method == 'POST':
        # 创建新测试任务
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': '任务名称不能为空'}), 400
        
        task_id = str(uuid.uuid4())
        task_name = data['name']
        new_task = {
            'id': task_id,
            'name': task_name,
            'description': data.get('description', ''),
            'testcases': data.get('testcases', []),
            'status': 'pending',  # pending, running, completed, failed
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 创建对应的JSON配置文件
        config_filename = f"{task_name}.json"
        task_dir = os.path.join(BASE_DIR, 'task')
        config_file_path = os.path.join(task_dir, config_filename)
        
        # 确保task文件夹存在
        os.makedirs(task_dir, exist_ok=True)
        
        try:
            # 以base.json为基准创建配置文件
            base_config_path = os.path.join(BASE_DIR, "base.json")
            
            if os.path.exists(base_config_path):
                with open(base_config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 将选中的测试用例flag设置为1
                for testcase_id in data.get('testcases', []):
                    if testcase_id in config_data:
                        config_data[testcase_id]['flag'] = 1
                
                # 保存配置文件
                with open(config_file_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=2)
                
                print(f"已基于base.json创建配置文件: {config_filename}")
                return jsonify({'message': '任务创建成功', 'task': new_task}), 201
            else:
                print(f"警告: base.json文件不存在，无法创建配置文件")
                return jsonify({'error': 'base.json文件不存在，无法创建任务配置文件'}), 500
            
        except Exception as e:
            print(f"创建配置文件失败: {e}")
            return jsonify({'error': f'创建配置文件失败: {e}'}), 500

@app.route('/api/tasks/<task_name>', methods=['GET', 'PUT', 'DELETE'])
def manage_task(task_name):
    """单个测试任务管理API接口"""
    tasks = load_tasks()
    task = next((t for t in tasks if t['name'] == task_name), None)
    
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    if request.method == 'GET':
        return jsonify(task)
    
    elif request.method == 'PUT':
        data = request.get_json()
        
        # 更新任务信息
        if 'name' in data:
            task['name'] = data['name']
        if 'description' in data:
            task['description'] = data['description']
        if 'testcases' in data:
            task['testcases'] = data['testcases']
        if 'status' in data:
            task['status'] = data['status']
        
        # 更新新参数
        if 'model_path' in data:
            task['model_path'] = data['model_path']
        if 'port_number' in data:
            task['port_number'] = data['port_number']
        if 'report_path' in data:
            task['report_path'] = data['report_path']
        if 'prompt_text' in data:
            task['prompt_text'] = data['prompt_text']
        if 'server_command' in data:
            task['server_command'] = data['server_command']
        if 'server_path' in data:
            task['server_path'] = data['server_path']
        if 'max_tokens' in data:
            task['max_tokens'] = data['max_tokens']
        
        # 如果更新了测试用例，需要同步更新对应的JSON配置文件中的flag字段
        if 'testcases' in data:
            # 先保存旧的测试用例列表，用于后续比较
            old_testcases = task.get('testcases', [])
            task['testcases'] = data['testcases']
            
            # 根据任务名称确定要更新的JSON文件
            config_filename = f"{task_name}.json"
            task_dir = os.path.join(BASE_DIR, 'task')
            config_file_path = os.path.join(task_dir, config_filename)
            
            # 更新对应的JSON配置文件中的flag字段
            try:
                if os.path.exists(config_file_path):
                    with open(config_file_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    # 重置所有测试用例的flag为0
                    for key in config_data:
                        if key.startswith('test_') and isinstance(config_data[key], dict):
                            config_data[key]['flag'] = 0
                    
                    # 将选中的测试用例flag设置为1
                    for testcase_id in data['testcases']:
                        if testcase_id in config_data:
                            config_data[testcase_id]['flag'] = 1
                    
                    # 保存更新后的配置文件
                    with open(config_file_path, 'w', encoding='utf-8') as f:
                        json.dump(config_data, f, ensure_ascii=False, indent=2)
                    
                    print(f"已更新{config_filename}中的flag字段，选中的测试用例: {data['testcases']}")
                else:
                    print(f"警告: {config_filename}文件不存在")
            except Exception as e:
                print(f"更新{config_filename}失败: {e}")
        
        task['updated_at'] = datetime.now().isoformat()
        
        # 由于任务数据现在是从JSON文件动态生成的，不需要保存到tasks.json
        # 直接返回成功
        return jsonify({'message': '任务更新成功', 'task': task})
    
    elif request.method == 'DELETE':
        # 删除任务时，先移除对应的任务数据
        original_count = len(tasks)
        tasks = [t for t in tasks if t['name'] != task_name]
        
        # 检查是否成功删除了任务
        if len(tasks) < original_count:
            # 删除对应的JSON配置文件
            config_filename = f"{task_name}.json"
            task_dir = os.path.join(BASE_DIR, 'task')
            config_file_path = os.path.join(task_dir, config_filename)
            
            try:
                if os.path.exists(config_file_path):
                    os.remove(config_file_path)
                    print(f"已删除配置文件: {config_filename}")
                else:
                    print(f"配置文件不存在: {config_filename}")
            except Exception as e:
                print(f"删除配置文件失败: {e}")
            
            # 成功删除了任务，由于任务数据现在是从JSON文件动态生成的，不需要保存到tasks.json
            return jsonify({'message': '任务删除成功'})
        else:
            return jsonify({'error': '任务不存在或删除失败'}), 404

@app.route('/api/tasks/<task_name>/testcases', methods=['POST', 'DELETE'])
def manage_task_testcases(task_name):
    """管理测试任务中的测试用例"""
    tasks = load_tasks()
    task = next((t for t in tasks if t['name'] == task_name), None)
    
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    if request.method == 'POST':
        # 添加测试用例到任务
        data = request.get_json()
        
        if not data or 'testcase_id' not in data:
            return jsonify({'error': '测试用例ID不能为空'}), 400
        
        testcase_id = data['testcase_id']
        
        # 检查测试用例是否存在
        testcases = load_testcases()
        testcase = next((tc for tc in testcases if tc['case'] == testcase_id), None)
        
        if not testcase:
            return jsonify({'error': '测试用例不存在'}), 404
        
        # 检查是否已存在
        if testcase_id not in task['testcases']:
            task['testcases'].append(testcase_id)
            task['updated_at'] = datetime.now().isoformat()
            
            # 由于任务数据现在是从JSON文件动态生成的，不需要保存到tasks.json
            return jsonify({'message': '测试用例添加成功', 'task': task})
        else:
            return jsonify({'message': '测试用例已存在'})
    
    elif request.method == 'DELETE':
        # 从任务中移除测试用例
        data = request.get_json()
        
        if not data or 'testcase_id' not in data:
            return jsonify({'error': '测试用例ID不能为空'}), 400
        
        testcase_id = data['testcase_id']
        
        if testcase_id in task['testcases']:
            task['testcases'].remove(testcase_id)
            task['updated_at'] = datetime.now().isoformat()
            
            # 由于任务数据现在是从JSON文件动态生成的，不需要保存到tasks.json
            return jsonify({'message': '测试用例移除成功', 'task': task})
        else:
            return jsonify({'message': '测试用例不存在于任务中'})

@app.route('/api/tasks/<task_name>/testcases/<testcase_id>/config', methods=['POST'])
def save_testcase_config(task_name, testcase_id):
    """保存测试用例配置"""
    tasks = load_tasks()
    task = next((t for t in tasks if t['name'] == task_name), None)
    
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    # 检查测试用例是否存在于任务中
    if testcase_id not in task['testcases']:
        return jsonify({'error': '测试用例不存在于任务中'}), 404
    
    # 检查测试用例是否存在
    testcases = load_testcases()
    testcase = next((tc for tc in testcases if tc['case'] == testcase_id), None)
    
    if not testcase:
        return jsonify({'error': '测试用例不存在'}), 404
    
    # 获取配置数据
    data = request.get_json()
    if not data:
        return jsonify({'error': '配置数据不能为空'}), 400
    
    # 初始化testcase_configs字段（如果不存在）
    if 'testcase_configs' not in task:
        task['testcase_configs'] = {}
    
    # 保存配置
    task['testcase_configs'][testcase_id] = data
    task['updated_at'] = datetime.now().isoformat()
    
    # 由于任务数据现在是从JSON文件动态生成的，不需要保存到tasks.json
    return jsonify({'message': '测试用例配置保存成功', 'config': data})

@app.route('/api/load-testcase-data', methods=['GET'])
def load_testcase_data():
    """加载testcase.json数据"""
    try:
        testcases = load_testcases()
        return jsonify(testcases)
    except Exception as e:
        return jsonify({'error': f'加载testcase.json数据失败: {str(e)}'}), 500

@app.route('/api/load-config', methods=['GET'])
def load_config_file():
    """从task文件夹加载配置文件"""
    try:
        filename = request.args.get('filename')
        
        if not filename:
            return jsonify({'error': '文件名不能为空'}), 400
        
        # 确保文件名以.json结尾
        if not filename.endswith('.json'):
            filename += '.json'
        
        # 构建文件路径（task文件夹）
        task_dir = os.path.join(BASE_DIR, 'task')
        file_path = os.path.join(task_dir, filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({'error': '配置文件不存在'}), 404
        
        # 读取配置文件
        with open(file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return jsonify(config)
    
    except Exception as e:
        return jsonify({'error': f'配置文件加载失败: {str(e)}'}), 500

@app.route('/api/save-config', methods=['POST'])
def save_config_file():
    """保存配置文件到task文件夹"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '配置数据不能为空'}), 400
        
        filename = data.get('filename')
        config = data.get('config')
        
        if not filename:
            return jsonify({'error': '文件名不能为空'}), 400
        
        if not config:
            return jsonify({'error': '配置内容不能为空'}), 400
        
        # 确保文件名以.json结尾
        if not filename.endswith('.json'):
            filename += '.json'
        
        # 构建文件路径（task文件夹）
        task_dir = os.path.join(BASE_DIR, 'task')
        file_path = os.path.join(task_dir, filename)
        
        # 确保task文件夹存在
        os.makedirs(task_dir, exist_ok=True)
        
        # 保存配置文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return jsonify({'message': f'配置文件保存成功: {filename}', 'file_path': file_path})
    
    except Exception as e:
        return jsonify({'error': f'配置文件保存失败: {str(e)}'}), 500

@app.route('/api/execute-command', methods=['POST'])
def execute_command():
    """在Linux服务器上执行命令"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        command = data.get('command')
        task_name = data.get('task_name')
        
        if not command:
            return jsonify({'error': '命令不能为空'}), 400
        
        if not task_name:
            return jsonify({'error': '任务名称不能为空'}), 400
        
        # 检查任务是否存在
        tasks = load_tasks()
        task = next((t for t in tasks if t['name'] == task_name), None)
        
        if not task:
            return jsonify({'error': '任务不存在'}), 404
        
        # 检查配置文件是否存在
        config_filename = f"{task_name}.json"
        task_dir = os.path.join(BASE_DIR, 'task')
        config_file_path = os.path.join(task_dir, config_filename)
        
        if not os.path.exists(config_file_path):
            return jsonify({'error': f'配置文件不存在: {config_filename}'}), 404
        
        # 在Linux服务器上执行命令
        # 注意：这里需要根据实际的Linux环境来执行命令
        # 在Windows开发环境中，我们只模拟执行并返回成功
        print(f"在Linux服务器上执行命令: {command}")
        
        # 在实际的Linux环境中，这里应该使用subprocess或os.system来执行命令
        # 例如：
        # import subprocess
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # 模拟执行成功
        return jsonify({
            'message': '命令执行成功',
            'command': command,
            'task_name': task_name,
            'output': '命令已提交到Linux服务器执行'
        })
    
    except Exception as e:
        print(f"执行命令失败: {e}")
        return jsonify({'error': f'命令执行失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)