import pandas as pd

ref_data = {
    '姓名': ['王五', '李四', '张三', '赵六', '陈七']
}
ref_df = pd.DataFrame(ref_data)
ref_df.to_excel('c:/file/川菜人工智能重点研究室/批处理/sort_tool/test/reference.xlsx', index=False)
print("参照文件已创建")

target_data = {
    '姓名': ['张三', '李四', '王五', '赵六', '陈七', '周八'],
    '年龄': [25, 30, 35, 40, 45, 50],
    '城市': ['北京', '上海', '广州', '深圳', '杭州', '成都']
}
target_df = pd.DataFrame(target_data)
target_df.to_excel('c:/file/川菜人工智能重点研究室/批处理/sort_tool/test/target.xlsx', index=False)
print("目标文件已创建")