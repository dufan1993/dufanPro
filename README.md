# 测试用例展示系统

这是一个基于Flask和Bootstrap的简洁Web应用，用于展示`testcase.json`文件中的测试用例。

## 功能特点

- 使用Flask作为后端框架
- 使用Bootstrap 5作为前端UI框架
- 动态展示testcase.json中的所有测试用例
- 响应式设计，适配不同屏幕尺寸
- 简洁的卡片式布局
- 按类型筛选功能（功能、精度、性能、规格）

## 安装和运行

1. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

2. 运行应用：
   ```
   python app.py
   ```

3. 在浏览器中访问：
   ```
   http://127.0.0.1:5000
   ```

## 项目结构

```
├── app.py              # Flask应用主文件
├── testcase.json       # 测试用例数据文件
├── requirements.txt    # 项目依赖文件
├── templates/
│   └── testcase.html   # HTML模板文件
└── README.md           # 说明文档
```

## API接口

- `GET /` - 返回测试用例展示页面
- `GET /api/testcases` - 返回JSON格式的测试用例数据

## 设计理念

- 保持代码简洁，避免过度设计
- 使用Bootstrap默认样式，减少自定义CSS
- 简化JavaScript逻辑，提高可维护性

## 筛选功能

页面标题右侧提供了一个筛选栏，可以根据测试用例的类型进行筛选：
- 全部：显示所有测试用例
- func：显示功能测试用例
- acc：显示精度测试用例
- performance：显示性能测试用例
- spec：显示规格测试用例

## 自定义

如需修改样式或添加功能，可以编辑`templates/testcase.html`文件。