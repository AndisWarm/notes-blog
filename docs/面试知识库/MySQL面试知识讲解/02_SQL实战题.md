# 02 SQL 实战题

本章是手写 SQL 题合集，每题都给出：题目分析 → 参考答案 → 讲解思路 → 易错点。建议先自己写一遍再看答案。

---

## 题1：求不存在 01 课程但存在 02 课程的学生的成绩

### 题目
有学生表、课程成绩表，求**不存在 01 课程但存在 02 课程**的学生的成绩。

### 表结构假设

```sql
-- 学生表
CREATE TABLE student (
  id INT PRIMARY KEY,
  name VARCHAR(20)
);

-- 课程成绩表（一个学生可以有多行，每行是一门课的成绩）
CREATE TABLE score (
  stu_id INT,
  course_id VARCHAR(10),   -- '01' '02' ...
  score DECIMAL(5,1),
  PRIMARY KEY (stu_id, course_id)
);
```

### 参考答案

```sql
-- 解法一：NOT EXISTS + EXISTS（语义最清晰）
SELECT s.*
FROM student s
JOIN score sc ON sc.stu_id = s.id AND sc.course_id = '02'
WHERE NOT EXISTS (
  SELECT 1 FROM score sc2
  WHERE sc2.stu_id = s.id AND sc2.course_id = '01'
);

-- 解法二：NOT IN（注意 NULL 陷阱，子查询加 IS NOT NULL 才安全）
SELECT s.*
FROM student s
JOIN score sc ON sc.stu_id = s.id AND sc.course_id = '02'
WHERE s.id NOT IN (
  SELECT stu_id FROM score WHERE course_id = '01'
);
```

### 解题思路拆解

题目拆成两个条件：
1. **存在 02 课程** → 通过 JOIN score 表且 course_id = '02' 实现
2. **不存在 01 课程** → 反查：该学生在 score 表里没有 course_id = '01' 的行

"不存在"在 SQL 里最地道的表达是 `NOT EXISTS`（或 NOT IN），因为 SQL 没有"直接说没有"的语法，只能通过反证法：`WHERE NOT EXISTS (子查询能查出该生选过01课)`。

### 易错点
- 忘记 JOIN '02' 的条件，导致把"选过 02 的学生"查成"所有学生"再过滤，结果错
- `NOT IN` 子查询结果里有 NULL 时全部不返回（见 01 章第 11 节），务必加 `IS NOT NULL`
- 题目要求"成绩"，如果只返回学生 id 而没带出成绩列，漏答

---

## 题2：查询总分排名在 5-10 名的学生 id 及对应的总分

### 题目
给定学生表 `studentscore (stuid, subject_id, score)`，查询**总分排名在 5-10 名**的学生 id 及对应的总分。

### 表结构

```sql
CREATE TABLE studentscore (
  stuid INT,
  subject_id VARCHAR(10),
  score DECIMAL(5,1)
);
```

### 参考答案

```sql
-- 解法一：先算总分排名，再取 5-10 名
SELECT stuid, total_score
FROM (
  SELECT stuid, SUM(score) AS total_score,
         ROW_NUMBER() OVER (ORDER BY SUM(score) DESC) AS rn
  FROM studentscore
  GROUP BY stuid
) t
WHERE rn BETWEEN 5 AND 10;
```

### 涉及考点：窗口函数 ROW_NUMBER()

这是 MySQL 8.0 的语法。`ROW_NUMBER() OVER (ORDER BY 总分 DESC)` 给每一行按总分从高到低编号 1、2、3……

- `RANK()`：并列会**跳过**名次（1,1,3）
- `DENSE_RANK()`：并列**不跳**名次（1,1,2）
- `ROW_NUMBER()`：即使并列也强制给不同序号（1,2,3），**没有并列**

题目说"排名 5-10 名"，如果担心并列，可以用 `DENSE_RANK()` 保证同一总分同一名次：

```sql
SELECT stuid, total_score
FROM (
  SELECT stuid, SUM(score) AS total_score,
         DENSE_RANK() OVER (ORDER BY SUM(score) DESC) AS rk
  FROM studentscore
  GROUP BY stuid
) t
WHERE rk BETWEEN 5 AND 10;
```

### 没有窗口函数怎么办？（MySQL 5.7 及之前的写法）

用**自连接**模拟排名：数一数"总分比我高的人有多少个"：

```sql
SELECT a.stuid, a.total_score
FROM (
  SELECT stuid, SUM(score) AS total_score
  FROM studentscore GROUP BY stuid
) a
JOIN (
  SELECT stuid, SUM(score) AS total_score
  FROM studentscore GROUP BY stuid
) b ON b.total_score > a.total_score
GROUP BY a.stuid, a.total_score
HAVING COUNT(*) BETWEEN 4 AND 9   -- 比我高的人有4~9个 → 我是第5~10名
ORDER BY a.total_score DESC;
```

### 易错点
- 忘记先 `GROUP BY stuid` 求总分，直接 RANK 每行成绩
- 子查询起的别名 `t` 在 WHERE 里不能用窗口函数（窗口函数只能出现在 SELECT 或 ORDER BY）
- 5-10 名应该是 `BETWEEN 5 AND 10`，写成 `LIMIT 4, 6` 效果类似（跳过4行取6行），但 LIMIT 方案在并列总分时语义不对

---

## 题3：查某个班级下所有学生的选课情况

### 题目
查某个班级下所有学生的选课情况。

### 表结构假设

```sql
-- 班级表
CREATE TABLE class (
  id INT PRIMARY KEY,
  class_name VARCHAR(20)
);

-- 学生表
CREATE TABLE student (
  id INT PRIMARY KEY,
  name VARCHAR(20),
  class_id INT          -- 关联班级
);

-- 选课表（学生和课程的多对多关系）
CREATE TABLE student_course (
  stu_id INT,
  course_id INT,
  PRIMARY KEY (stu_id, course_id)
);

-- 课程表
CREATE TABLE course (
  id INT PRIMARY KEY,
  course_name VARCHAR(50)
);
```

### 参考答案

```sql
SELECT s.id AS stu_id, s.name AS stu_name,
       c.course_name
FROM student s
LEFT JOIN student_course sc ON sc.stu_id = s.id
LEFT JOIN course c ON c.id = sc.course_id
WHERE s.class_id = 3;    -- 假设查 3 班
```

结果示例（没选课的学生 course_name 为 NULL，正好体现"选课情况"）：

| stu_id | stu_name | course_name |
|--------|----------|-------------|
| 1 | 张三 | 数学 |
| 1 | 张三 | 语文 |
| 2 | 李四 | NULL |

### 为什么用 LEFT JOIN 而不是 INNER JOIN？

题目说"**所有**学生的选课情况"——重点是"所有学生"，包括没选课的学生。INNER JOIN 会把没选课的学生**过滤掉**，LEFT JOIN 以学生表为主表，没选课的就显示 NULL，这才叫"所有学生的选课情况"。

### 举一反三：看某学生选了哪些课 vs 某课程有哪些学生

```sql
-- 某学生（id=1）的选课情况
SELECT c.course_name
FROM student_course sc
JOIN course c ON c.id = sc.course_id
WHERE sc.stu_id = 1;

-- 某课程（id=5）选了哪些学生
SELECT s.name
FROM student_course sc
JOIN student s ON s.id = sc.stu_id
WHERE sc.course_id = 5;
```

### 多对多关系补充
学生和课程是**多对多**：一个学生选多门课、一门课被多个学生选。多对多在关系型数据库里必须拆成三张表：学生表 + 课程表 + **中间表**（student_course，只存两个外键）。这是建表题的高频考点。

---

## 题4：如何用 MySQL 实现一个可重入的锁？

### 题目背景
分布式环境下，多个服务实例要抢同一份资源，需要一把"跨进程的锁"。MySQL 可以充当这把锁，面试问的是**实现思路**，重点是"可重入"。

### 什么是可重入？
同一个客户端（同一个线程/连接）**拿到锁之后，再请求一次还能拿到**，不会把自己锁死。比如方法 A 里调方法 B，两个方法都要加同一把锁，可重入锁允许 B 顺利拿到锁。

### 实现方案一：基于唯一索引 + 计数（推荐，最简洁）

建一张锁表，利用**唯一索引**保证同一把锁只有一行，加锁=插入/更新，释放=删除：

```sql
CREATE TABLE reentrant_lock (
  lock_key   VARCHAR(64) PRIMARY KEY,   -- 锁的名字，唯一
  owner_id   VARCHAR(64) NOT NULL,      -- 谁持有（连接id/线程id）
  ref_count  INT NOT NULL DEFAULT 0,    -- 重入次数
  expire_at  DATETIME NOT NULL          -- 过期时间，防死锁
);
```

**加锁**（原子操作，靠唯一键冲突实现互斥）：

```sql
-- 拿到锁 = 成功插入这一行（如果 lock_key 已存在则插入失败 → 锁被占用）
INSERT INTO reentrant_lock (lock_key, owner_id, ref_count, expire_at)
VALUES ('order_123', 'conn-1', 1, DATE_ADD(NOW(), INTERVAL 30 SECOND))
ON DUPLICATE KEY UPDATE
  ref_count = IF(owner_id = 'conn-1', ref_count + 1, ref_count),
  expire_at = IF(owner_id = 'conn-1', DATE_ADD(NOW(), INTERVAL 30 SECOND), expire_at);

-- 判断是否加锁成功：检查影响行数，或再查一次
-- owner_id 相同 → 重入成功（ref_count + 1），owner_id 不同 → 失败（别人的锁）
```

**释放锁**（必须校验 owner 是自己，防止释放别人的锁）：

```sql
-- 重入次数减到 0 就删行，否则减一
UPDATE reentrant_lock
SET ref_count = ref_count - 1
WHERE lock_key = 'order_123' AND owner_id = 'conn-1';

DELETE FROM reentrant_lock
WHERE lock_key = 'order_123' AND owner_id = 'conn-1' AND ref_count <= 0;
```

**心跳续期**（防止持有期间进程挂了，锁永远不释放）：持有者定期执行续期 update，超过 expire_at 没续期的锁，其他请求可以抢走。

### 实现方案二：GET_LOCK() / RELEASE_LOCK()（MySQL 内置，最简单）

```sql
SELECT GET_LOCK('order_123', 10);   -- 尝试加锁，最多等10秒；返回1成功，0超时
-- ... 临界区代码 ...
SELECT RELEASE_LOCK('order_123');   -- 释放锁
```

特点：
- 按**连接**维度加锁，同一连接内可重入（再调 GET_LOCK 同一名字会直接成功，但要调用次数匹配才释放）
- 连接断开自动释放锁（不会死锁）
- 缺点：锁属于"这个数据库连接"，连接池复用时锁的语义容易混乱

### 方案三：悲观锁（SELECT ... FOR UPDATE）

```sql
BEGIN;
SELECT * FROM resource WHERE id = 1 FOR UPDATE;  -- 锁定这行
-- 业务处理...
COMMIT;  -- 提交后自动释放
```

可重入性：**同一事务内**再查同一行 FOR UPDATE 会直接成功（行锁本身支持同事务重入）。但跨事务就不行了。

### 面试回答模板

1. 先说清楚需求：互斥（唯一）+ 防死锁（过期时间）+ 可重入（记录 owner 和计数）
2. 给出唯一索引方案的表结构，讲加锁/释放的 SQL
3. 强调三个细节：**owner 校验**（不能释放别人的锁）、**过期续期**（防进程崩溃死锁）、**原子性**（加锁用一个 SQL 完成，不能先 SELECT 再 INSERT）
4. 可补充：MySQL 锁只能满足小规模分布式锁需求，大规模场景一般用 Redis（Redisson）或 ZooKeeper，面试最后提一句"生产环境我更倾向 Redis 分布式锁，MySQL 方案用于轻量场景"是加分项。

### 易错点
- 忘记加过期时间 → 进程崩溃锁永不释放（死锁）
- 释放时不校验 owner → 锁被别人的请求误删
- 用"先查后插"实现加锁 → 并发下两个请求都查到不存在，都插入，重复（必须靠唯一索引原子挡）