# Logging 配置说明

## 概述

本项目已为所有Python模块添加了完整的logging功能，用于记录程序执行过程中的关键信息、调试信息、警告和错误。

## Logging 配置

### 日志级别

项目使用以下日志级别：
- **DEBUG**: 详细的调试信息（如数据形状、列名等）
- **INFO**: 关键操作的执行信息（如开始/完成某个步骤）
- **WARNING**: 警告信息（如缺失列、跳过某些分析等）
- **ERROR**: 错误信息（如文件未找到、API调用失败等）

### 日志输出

日志会同时输出到两个位置：
1. **控制台 (stdout)**: 实时查看程序执行状态
2. **日志文件 (bmw_analysis.log)**: 保存完整的日志记录，便于事后分析

### 日志格式

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

示例：
```
2025-11-29 10:30:15,123 - data_loader - INFO - 开始加载数据文件: BMW sales data (2020-2024).xlsx
2025-11-29 10:30:16,456 - analyzer - INFO - 开始基础分析...
```

## 各模块Logging说明

### 1. main.py
- 配置logging系统
- 记录整体流程的开始和结束
- 记录每个步骤的执行状态
- 捕获并记录任何异常

### 2. data_loader.py
- 记录数据文件加载过程
- 记录数据形状和列名标准化
- 记录文件不存在等错误

### 3. analyzer.py
- 记录各种分析函数的执行状态
- 记录数据聚合的结果统计
- 警告缺失的必要列
- 记录AI报告数据摘要的构建过程

### 4. visualizer.py
- 记录每个图表的生成过程
- 统计成功生成的图表数量
- 记录图表生成失败的错误信息

### 5. llm_client.py
- 记录OpenAI客户端初始化状态
- 记录API调用过程
- 记录报告生成和保存的详细信息
- 记录API调用失败的详细错误

## 使用示例

### 运行程序

```bash
python main.py
```

程序运行时会在控制台显示日志，同时写入 `bmw_analysis.log` 文件。

### 查看日志文件

```bash
# 查看完整日志
cat bmw_analysis.log

# 实时跟踪日志
tail -f bmw_analysis.log

# 只查看错误信息
grep "ERROR" bmw_analysis.log

# 只查看警告信息
grep "WARNING" bmw_analysis.log
```

## 调整日志级别

如需修改日志级别，可以在 `main.py` 的 `setup_logging()` 函数中修改：

```python
def setup_logging() -> None:
    """配置日志系统"""
    logging.basicConfig(
        level=logging.DEBUG,  # 改为 DEBUG、INFO、WARNING 或 ERROR
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bmw_analysis.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
```

- `logging.DEBUG`: 显示所有日志（包括详细的调试信息）
- `logging.INFO`: 显示INFO及以上级别（推荐用于生产环境）
- `logging.WARNING`: 只显示警告和错误
- `logging.ERROR`: 只显示错误

## 日志示例输出

```
2025-11-29 10:30:15,123 - __main__ - INFO - ==================================================
2025-11-29 10:30:15,124 - __main__ - INFO - 开始BMW销售数据分析流程
2025-11-29 10:30:15,125 - __main__ - INFO - ==================================================
2025-11-29 10:30:15,126 - __main__ - INFO - 步骤 1/5: 加载数据...
2025-11-29 10:30:15,127 - data_loader - INFO - 开始加载数据文件: BMW sales data (2020-2024).xlsx
2025-11-29 10:30:16,234 - data_loader - INFO - 成功读取Excel文件，原始数据形状: (10000, 15)
2025-11-29 10:30:16,235 - data_loader - INFO - 数据加载完成，最终数据形状: (10000, 15)
2025-11-29 10:30:16,236 - __main__ - INFO - 数据加载成功，共 10000 行数据
2025-11-29 10:30:16,237 - __main__ - INFO - 步骤 2/5: 执行基础分析...
2025-11-29 10:30:16,238 - analyzer - INFO - 开始基础分析...
2025-11-29 10:30:16,345 - analyzer - INFO - 数据完整，无缺失值
2025-11-29 10:30:16,456 - analyzer - INFO - 基础分析完成
...
2025-11-29 10:32:30,789 - visualizer - INFO - ✓ 图表1生成成功: chart_01_year_volume_yoy.png
...
2025-11-29 10:35:45,123 - __main__ - INFO - ==================================================
2025-11-29 10:35:45,124 - __main__ - INFO - 所有分析流程执行完成
2025-11-29 10:35:45,125 - __main__ - INFO - ==================================================
```

## 注意事项

1. 日志文件 `bmw_analysis.log` 会在每次运行时追加内容，不会自动清空
2. 如需清空日志，手动删除该文件即可
3. 所有异常都会记录完整的堆栈信息（`exc_info=True`），便于调试
4. 生产环境建议使用 `INFO` 级别，开发调试时可使用 `DEBUG` 级别

