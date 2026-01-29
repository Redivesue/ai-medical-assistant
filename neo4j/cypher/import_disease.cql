// 从 JSON/CSV 导入疾病、症状、药品、食物的示例脚本占位
// 具体实现可参考 red_spider_base/build_medicalgraph.py

// 示例：匹配已存在的节点并创建关系
// MATCH (d:Disease {name: '感冒'}), (s:Symptom {name: '发热'})
// MERGE (d)-[:has_symptom {name: '症状'}]->(s);
