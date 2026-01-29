# 红蜘蛛AI医疗助手 - Neo4j 说明

## 目录结构

- cypher/: 存放建图相关的 Cypher 脚本
  - create_schema.cql: 创建索引/约束
  - import_disease.cql: 导入疾病/症状/药品/食物关系的示例
- data/: 如需从 CSV/JSON 导入数据，可将文件放在此目录

## 当前图数据来源

当前 Neo4j 中的医疗知识图谱，来自于 red_spider_base 项目中的 build_medicalgraph.py 脚本，
使用 data/medical.json 构建，包含以下节点和关系：

- 节点：Disease, Symptom, Drug, Food
- 关系：
  - (Disease)-[:has_symptom]->(Symptom)
  - (Disease)-[:recommand_drug]->(Drug)
  - (Disease)-[:recommand_eat]->(Food)

## 用途

本目录主要用于：

1. 记录和备份建图所需的 Cypher 脚本
2. 将来在新环境（本地/云端 Aura）中快速重建知识图谱
3. 作为文档，帮助理解当前图结构

## 使用建议

1. 本地开发时：
   - 直接使用已有的 Neo4j 图（无需重复建图）
   - 仅在需要重建图时，参考 build_medicalgraph.py 或自行编写导入脚本

2. 迁移到云端 Neo4j 时：
   - 在新数据库中执行 create_schema.cql 创建索引/约束
   - 编写新的导入脚本，或复用 build_medicalgraph.py，将数据导入到云端
   - 在 backend/app/config.py 中修改 NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD


