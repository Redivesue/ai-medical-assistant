// 创建基本索引和约束的示例 Cypher（根据实际需要调整）

// 疾病名称唯一
CREATE CONSTRAINT disease_name_unique IF NOT EXISTS
FOR (d:Disease)
REQUIRE d.name IS UNIQUE;

// 药品名称唯一
CREATE CONSTRAINT drug_name_unique IF NOT EXISTS
FOR (d:Drug)
REQUIRE d.name IS UNIQUE;

// 食物名称唯一
CREATE CONSTRAINT food_name_unique IF NOT EXISTS
FOR (f:Food)
REQUIRE f.name IS UNIQUE;

// 症状名称唯一
CREATE CONSTRAINT symptom_name_unique IF NOT EXISTS
FOR (s:Symptom)
REQUIRE s.name IS UNIQUE;
