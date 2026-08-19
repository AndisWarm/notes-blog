# 01 SQL 基础与数据类型

本章覆盖：NoSQL vs SQL、三大范式、连表查询、避免重复插入、CHAR/VARCHAR、int(1)/int(10)、Text、IP 存储、外键、IN/EXISTS、常用函数、SQL 执行顺序。

---

## 1. NoSQL 和 SQL 的区别？

### 一句话回答
SQL（关系型数据库）用**表**存数据、强调**关系**和**一致性**；NoSQL（非关系型数据库）用键值/文档/列/图存数据，强调**灵活**和**扩展性**。

### 展开讲

**SQL 数据库**（MySQL、PostgreSQL、Oracle）：
- 数据存在一张张**表**里，表之间有**关系**（比如"订单表"通过 user_id 关联"用户表"）
- 必须先设计好表结构（列的类型、约束），再往里存数据
- 用 **SQL 语言**查询，支持多表联查、事务（ACID）
- 好处：数据规范、不会乱、支持复杂查询
- 代价：表结构改起来麻烦，水平扩展（加机器）难

**NoSQL 数据库**（Redis、MongoDB、Elasticsearch、HBase）：
- 数据存在**键值对**、**文档**（类似 JSON）、**列族**、**图**里
- 不需要预先定义结构，想存啥存啥（比如 MongoDB 里两条文档字段可以不一样）
- 好处：写入快、灵活、天然适合分布式扩展
- 代价：一般不支持事务（或支持得很弱）、复杂关联查询能力差

### 比喻
- SQL 像**Excel 表格**：行列整齐、有公式校验，但要合并多个表很费劲
- NoSQL 像**抽屉里的一堆便签**：想写什么写什么、找起来快，但便签之间没有关联

### 怎么选
- 需要事务（钱、订单）、复杂查询（报表）→ SQL
- 高并发读写、数据结构不固定（日志、缓存、评论）→ NoSQL
- 实际项目常常**混用**：MySQL 存核心数据，Redis 做缓存

---

## 2. 数据库三大范式是什么？

### 一句话回答
三大范式是**设计表结构的规范**，目的是减少数据冗余（重复存储），核心是"每张表只做一件事，每个字段只存一个值"。

### 第一范式（1NF）：列不可再分

每一列都必须是**原子值**，不能再拆。

❌ 违反（一列存了多个信息）：

| id | 姓名 | 联系方式 |
|----|------|----------|
| 1 | 张三 | 13800000000, 北京 |

✅ 符合（拆成多列）：

| id | 姓名 | 电话 | 地址 |
|----|------|------|------|
| 1 | 张三 | 13800000000 | 北京 |

### 第二范式（2NF）：在 1NF 基础上，非主键列必须完全依赖主键

适用于**联合主键**：如果一个表的主键是 (A, B)，那么其他列不能只依赖 A 或只依赖 B，必须依赖 A+B 整体。

举例，订单明细表主键是 (订单号, 商品号)：

❌ 违反：把"商品名称"放进来——商品名称只依赖"商品号"，和"订单号"没关系，会导致同一商品存了多份名称（冗余）。

✅ 正确做法：拆成"订单明细表（订单号+商品号+数量）"和"商品表（商品号+商品名称）"两张表。

### 第三范式（3NF）：在 2NF 基础上，非主键列不能依赖其他非主键列

也就是：**非主键列之间不能有传递依赖**。

❌ 违反：

| 学生id | 学生姓名 | 班级id | 班主任 |
|--------|----------|--------|--------|
| 1 | 张三 | 3班 | 王老师 |

"班主任"依赖"班级id"，而"班级id"不是主键 → 一个班有 50 个学生就存了 50 遍王老师。

✅ 正确做法：学生表只留"班级id"，班主任放到班级表里。

### 面试常问：范式是不是越高越好？

不是。范式越高，表拆得越细，查询时要**多表 JOIN**，反而变慢。实际开发经常"**反范式**"：在查询频繁的场景故意存冗余字段（比如订单表直接存商品名称快照），用空间换速度。三大范式是理论基准，实际以"查得快 + 改得动"为准。

---

## 3. MySQL 怎么连表查询？

### 一句话回答
用 JOIN 关键字把多张表按关联条件拼成一张大表来查，有 INNER JOIN（内连接）、LEFT/RIGHT JOIN（外连接）、CROSS JOIN（交叉连接）。

### 核心概念
连表本质：**把两行的字段按条件拼成一行**。假设有两张表：

学生表 student：

| id | name |
|----|------|
| 1 | 张三 |
| 2 | 李四 |

选课表 course：

| id | stu_id | course_name |
|----|--------|-------------|
| 1 | 1 | 数学 |
| 2 | 1 | 语文 |
| 3 | 2 | 数学 |

### 内连接 INNER JOIN：只返回两表都匹配上的行

```sql
SELECT s.name, c.course_name
FROM student s
INNER JOIN course c ON s.id = c.stu_id;
```

结果（张三有2门课，李四有1门课）：

| name | course_name |
|------|-------------|
| 张三 | 数学 |
| 张三 | 语文 |
| 李四 | 数学 |

### 左连接 LEFT JOIN：以左表为主，右表没匹配就补 NULL

```sql
SELECT s.name, c.course_name
FROM student s
LEFT JOIN course c ON s.id = c.stu_id;
```

结果（张三、李四都在，没选课的会显示 NULL）：

| name | course_name |
|------|-------------|
| 张三 | 数学 |
| 张三 | 语文 |
| 李四 | 数学 |

### 右连接 RIGHT JOIN：以右表为主（和 LEFT JOIN 对称，实际用得少）

### 交叉连接 CROSS JOIN：笛卡尔积，所有行两两组合

```sql
SELECT * FROM student CROSS JOIN course;
-- 2 行 × 3 行 = 6 行结果
```

### 三张表以上连表
依次 JOIN 就行，每次连接得到的结果继续参与下一次连接：

```sql
SELECT s.name, c.course_name, t.teacher_name
FROM student s
JOIN course c ON s.id = c.stu_id
JOIN teacher t ON c.teacher_id = t.id;
```

### 面试注意
- JOIN 时一定要带 **ON 条件**，否则变成笛卡尔积，数据量爆炸
- 连表查慢的常见原因：ON 的字段没建索引
- `USING(col)` 可以简写 `ON 两表.列名相同` 的情况，但用得少

---

## 4. MySQL 如何避免重复插入数据？

### 背景
用户点了两次提交、接口被重试，就会插入两条一模一样的记录。解决思路分三层：**约束防**、**语法防**、**逻辑防**。

### 方案一：唯一索引 / 唯一约束（最推荐，数据库兜底）

```sql
-- 建表时给"业务上不允许重复"的字段加 UNIQUE
CREATE TABLE user (
  id INT PRIMARY KEY AUTO_INCREMENT,
  phone VARCHAR(20) UNIQUE,   -- 手机号不能重复
  name VARCHAR(50)
);
```

插入重复手机号时，MySQL 直接报错拒绝。**唯一索引是防止重复的终极保险**，无论应用层怎么出 bug 都挡得住。

### 方案二：INSERT IGNORE（重复则静默忽略，不报错）

```sql
INSERT IGNORE INTO user (phone, name) VALUES ('13800000000', '张三');
-- 若 phone 已存在：不插入也不报错，影响行数为 0
```

### 方案三：ON DUPLICATE KEY UPDATE（重复则更新）

```sql
INSERT INTO user (phone, name) VALUES ('13800000000', '张三')
ON DUPLICATE KEY UPDATE name = VALUES(name);
-- 不存在就插入，存在就把 name 更新掉（常用于"计数器+1"场景）
```

### 方案四：REPLACE INTO（重复则先删后插）

```sql
REPLACE INTO user (phone, name) VALUES ('13800000000', '张三');
-- 存在则先 DELETE 再 INSERT（注意：id 会变，要慎用）
```

### 方案五：应用层逻辑判断（最弱，只能作为辅助）

先 `SELECT` 查一遍再插入。有并发问题：两个请求同时查都不存在，然后同时插入，还是重复了。所以**不能只靠它**。

### 面试回答套路
"我会在业务字段上建**唯一索引**做兜底，插入时根据需求选择 `INSERT IGNORE` 或 `ON DUPLICATE KEY UPDATE`，应用层再配合幂等校验（比如用订单号去重）"

---

## 5. CHAR 和 VARCHAR 有什么区别？

### 一句话回答
CHAR 是**定长**字符串，存多少就固定占多少空间（不足补空格）；VARCHAR 是**变长**字符串，实际多长占多长，另外加 1~2 字节记录长度。

### 对比表

| 对比项 | CHAR | VARCHAR |
|--------|------|---------|
| 长度定义 | CHAR(10) = 固定 10 字符 | VARCHAR(10) = 最多 10 字符 |
| 存储 | 不足长度用空格补齐 | 存实际内容 + 长度前缀 |
| 存储空间 | 固定（一般不用额外字节） | 按内容长度 + 1~2 字节长度前缀 |
| 读取 | 需要去掉末尾空格 | 直接读 |
| 速度 | 略快（长度固定，定位容易） | 略慢 |
| 适用 | 长度基本固定的：手机号、身份证、md5 | 长度不固定的：姓名、地址、评论 |

### 重要细节
- 定义时的数字 `CHAR(10)` / `VARCHAR(10)` 都表示**字符数**，不是字节数
- CHAR 超过定义长度会报错或截断（取决于 SQL 模式）
- 查询 CHAR 时 MySQL 会自动去掉尾部空格：`WHERE name = 'abc'` 能匹配到存储为 `'abc   '` 的记录
- VARCHAR 存储时**不会**去掉尾部空格（会原样保留）

### 怎么选
- 手机号、身份证号、MD5、UUID 这种长度固定的 → CHAR
- 用户名、地址、内容这种长短不一的 → VARCHAR
- 8.0 之前 VARCHAR 最大 255 字节需要 1 字节长度前缀，超过要 2 字节；8.0 后统一按内容长度计算

---

## 6. VARCHAR 后面代表字节还是字符？

### 答案
**字符**（character），不是字节。

`VARCHAR(10)` 表示最多存 **10 个字符**。

具体占多少字节取决于字符集：
- 纯英文（ASCII 字符集）：1 字符 = 1 字节
- UTF-8：英文字母 1 字符 = 1 字节，中文 1 字符 = **3 字节**（emoji 是 4 字节）

所以 `VARCHAR(10)` 在 UTF-8 下最多能存 10 个汉字 = 30 字节。

### 面试延伸：VARCHAR 的最大长度是多少？

- VARCHAR 本身最大 **65535 字节**（这是行内所有 VARCHAR 列的总限制）
- 实际能写多少字符，要看字符集和整行其他列占的字节
- 一个纯 VARCHAR(65535) 的 UTF-8 表实际只能定义到 VARCHAR(21844) 左右（65535 / 3 向下取整，还要留长度前缀字节）

### 对比记忆
- CHAR(10)：10 字符，不足补空格
- VARCHAR(10)：最多 10 字符
- 两者括号里都是**字符数**

---

## 7. int(1) 和 int(10) 在 MySQL 有什么不同？

### 答案
**没有任何区别**（除了展示宽度，而且展示宽度在 8.0 已废弃）。

INT 在 MySQL 里固定占 **4 字节**，取值范围固定：
- 有符号：-2147483648 ~ 2147483647（约 -21亿 ~ 21亿）
- 无符号：0 ~ 4294967295

括号里的数字（显示宽度）**不影响存储空间，也不影响取值范围**，只影响"如果配合 ZEROFILL 属性，前面补多少个 0"：

```sql
CREATE TABLE t (a INT(4) ZEROFILL);
INSERT INTO t VALUES (12);
SELECT * FROM t;  -- 输出 0012（补到4位）
```

`INT(4)` 存 123456 照样存得下。**MySQL 8.0 已经移除了显示宽度特性**，int(1) 和 int(10) 完全等价。

### 面试延伸
- 真正区分整数大小的是类型本身：TINYINT(1字节)、SMALLINT(2)、MEDIUMINT(3)、INT(4)、BIGINT(8)
- 面试问"int(1) 是不是只能存一位数"→ 不是，这是最常见的误区

---

## 8. Text 数据类型可以无限大吗？

### 答案
不能。TEXT 有固定上限（64KB 起步），且**在磁盘上按内容长度存储**，不是无限大。

### TEXT 家族

| 类型 | 最大长度 | 字节数 |
|------|----------|--------|
| TINYTEXT | 255 字节 | 1 |
| TEXT | 65535 字节（64KB） | 2 |
| MEDIUMTEXT | 约 16MB | 3 |
| LONGTEXT | 约 4GB | 4 |

（前面数字表示记录长度所需的字节数）

### 实际使用注意
- TEXT 不能有默认值（8.0 之前），不能直接建普通索引（要建前缀索引）
- 数据超过 64KB 存不进 TEXT，要用 MEDIUMTEXT/LONGTEXT
- 大文本一般不会全量查出来（避免 `SELECT *`），而是分页截取
- 超大内容（几 MB 以上）通常建议存**文件系统/对象存储**（OSS），数据库只存文件路径——因为 MySQL 一行数据过大时，行会溢出到额外页，IO 变慢

### 对比：BLOB
BLOB 和 TEXT 差不多，区别是 BLOB 存**二进制**（图片、文件），TEXT 存**字符**。实际项目很少用 BLOB 存文件，都是存路径。

---

## 9. IP 地址如何在数据库里存储？

### 答案
正规做法：用**整数（INT UNSIGNED）**存储，用 `INET_ATON()` / `INET_NTOA()` 两个函数互相转换；图省事也可以存 VARCHAR(15)，但要接受"查得慢、占空间"的代价。

### 为什么推荐 INT？

IP 本质是 4 个 0~255 的数字，如 `192.168.1.1`。

- VARCHAR(15) 存：需要 15 字节（实际 ~7-15），且比较大小是字符串比较（`192.168.1.10` 和 `192.168.1.9` 的字符串排序会乱：'10' < '9'）
- INT UNSIGNED 存：固定 4 字节，**数值比较天然就是正确的 IP 顺序**，还能直接做范围查询（`WHERE ip BETWEEN ... AND ...`）

### 用法

```sql
-- 写入：IP 转整数
INSERT INTO log (ip) VALUES (INET_ATON('192.168.1.1'));

-- 查询：整数转回 IP
SELECT INET_NTOA(ip) FROM log;

-- 范围查询（查找某网段的所有记录）
SELECT INET_NTOA(ip) FROM log
WHERE ip BETWEEN INET_ATON('192.168.1.0') AND INET_ATON('192.168.1.255');
```

### IPv6
`INET6_ATON()` / `INET6_NTOA()` 支持 IPv6，返回二进制（16 字节），存 `BINARY(16)`。

### 面试答法
"IP 用 INT UNSIGNED 存，通过 INET_ATON/INET_NTOA 转换，省空间（4字节 vs 15字节）且数值比较符合 IP 大小顺序，方便做网段范围查询。注意要加 UNSIGNED，否则超过 21亿 的 IP 存不下。"

---

## 10. 说一下外键约束

### 一句话回答
外键（FOREIGN KEY）是表与表之间的**关系约束**：子表的某列必须引用父表的主键，保证"引用的东西必须真实存在"，MySQL 里只有 InnoDB 引擎支持。

### 基本用法

```sql
CREATE TABLE orders (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  amount DECIMAL(10,2),
  FOREIGN KEY (user_id) REFERENCES users(id)   -- 外键：必须存在于 users.id
);
```

效果：
- 往 orders 插 user_id=999，但 users 表没有 999 → **插入失败**
- 删除 users 里有订单的用户 → 默认**拒绝删除**（防止删了父表数据，子表变孤儿）

### ON DELETE / ON UPDATE 行为（级联规则）

```sql
FOREIGN KEY (user_id) REFERENCES users(id)
ON DELETE CASCADE   -- 父记录删除时，子记录跟着删
ON UPDATE CASCADE   -- 父主键更新时，子记录跟着更新
```

| 选项 | 含义 |
|------|------|
| RESTRICT（默认） | 有子记录引用时，禁止删除/更新父记录 |
| CASCADE | 父记录删/改，子记录同步删/改 |
| SET NULL | 父记录删/改，子记录外键列置 NULL |
| NO ACTION | 同 RESTRICT |

### 面试重点：生产环境为什么不推荐外键？

大厂面试几乎必问，标准回答：
1. **性能**：每次插入/更新子表都要去查父表做校验，多一次 IO；高并发下是热点竞争
2. **分布式/分库分表**：数据分散在多台机器，外键校验跨库做不了
3. **写入变慢**：删除父表时要检查子表，锁的范围可能扩大
4. **线上修改困难**：加外键会锁表，大表上改结构是灾难

所以实际开发中常见做法：**逻辑外键**——表结构不建 FOREIGN KEY，但在应用层代码里保证数据一致性，索引照建。面试时能说清"约束靠应用层+唯一索引兜底"就是加分项。

---

## 11. MySQL 的关键字 IN 和 EXISTS

### 一句话回答
IN 是"**值在集合里**"，EXISTS 是"**子查询有没有结果**"。小表 IN 快，大表 EXISTS 更稳，但 MySQL 优化器经常自动转换，实际差距没那么大。

### 基本用法

```sql
-- IN：c.id 出现在子查询结果集合中
SELECT * FROM course WHERE id IN (SELECT course_id FROM score);

-- EXISTS：子查询能查出至少一行就返回该主表记录
SELECT * FROM course c
WHERE EXISTS (SELECT 1 FROM score s WHERE s.course_id = c.id);
```

### 区别对比

| 对比项 | IN | EXISTS |
|--------|----|--------|
| 语义 | 值 ∈ 集合 | 是否存在满足条件的行 |
| 子查询内容 | 返回一列值 | 只看有没有行（SELECT 1 即可） |
| 子查询含 NULL 时的坑 | 结果含 NULL 时 IN 判断可能"静默不匹配" | 不受 NULL 影响 |
| 大数据量 | 子查询结果集过大时可能撑爆内存 | 逐行驱动，内存友好 |

### 经典误区
`IN` 和 `NOT IN` 当子查询结果含 **NULL** 时，`NOT IN` 会**永远返回空**（因为 `x NOT IN (1, NULL)` 的语义是 `x != 1 AND x != NULL`，而 `x != NULL` 结果是 UNKNOWN，不是 TRUE）。

```sql
-- 如果子查询里有 NULL，这条会查不出任何数据！
SELECT * FROM course WHERE id NOT IN (SELECT course_id FROM score WHERE course_id IS NOT NULL);
-- 解决：子查询加 IS NOT NULL，或用 NOT EXISTS
```

### 面试答法
"两者都能做子查询关联，IN 适合子查询结果集小的情况，EXISTS 适合主表小、子查询大的情况；NOT IN 有 NULL 陷阱，推荐用 NOT EXISTS 替代。MySQL 8.0 的优化器越来越智能，很多场景会自动改写，所以别死记'谁一定快'，关键看执行计划。"

---

## 12. MySQL 中的一些基本函数，你知道哪些？

### 分类记忆：字符串、数值、日期、聚合、条件、加密

### 1. 字符串函数

| 函数 | 作用 | 例子 |
|------|------|------|
| CONCAT(a, b) | 拼接 | CONCAT('a','b') → 'ab' |
| LENGTH(str) | 字节数 | LENGTH('你好') → 6（UTF-8） |
| CHAR_LENGTH(str) | 字符数 | CHAR_LENGTH('你好') → 2 |
| SUBSTRING(str, pos, len) | 截取 | SUBSTRING('hello',2,3) → 'ell' |
| REPLACE(str, a, b) | 替换 | REPLACE('abc','b','X') → 'aXc' |
| UPPER / LOWER | 转大写/小写 | UPPER('abc') → 'ABC' |
| TRIM / LTRIM / RTRIM | 去空格 | TRIM('  a  ') → 'a' |
| LEFT / RIGHT | 取左/右侧字符 | LEFT('abc',2) → 'ab' |
| LPAD / RPAD | 补位 | LPAD('5',3,'0') → '005' |

### 2. 数值函数

| 函数 | 作用 | 例子 |
|------|------|------|
| ROUND(x, n) | 四舍五入 | ROUND(3.14159, 2) → 3.14 |
| CEIL / FLOOR | 向上/向下取整 | CEIL(3.1)→4, FLOOR(3.9)→3 |
| ABS | 绝对值 | ABS(-5) → 5 |
| MOD(a, b) | 取余 | MOD(10, 3) → 1 |
| POW(x, y) | 幂 | POW(2, 10) → 1024 |
| RAND() | 随机数 0~1 | RAND() |

### 3. 日期函数（面试高频）

```sql
NOW()          -- 当前时间 2026-08-15 10:30:00
CURDATE()      -- 当前日期 2026-08-15
CURTIME()      -- 当前时间 10:30:00
DATE(now)      -- 取日期部分
YEAR(now) / MONTH(now) / DAY(now) / HOUR(now)
DATEDIFF(d1, d2)        -- 相差天数
DATE_ADD(now, INTERVAL 1 DAY)  -- 日期+1天
DATE_SUB(now, INTERVAL 1 MONTH) -- 日期减1月
DATE_FORMAT(now, '%Y-%m-%d %H:%i:%s')  -- 格式化输出
UNIX_TIMESTAMP(now)     -- 转时间戳
FROM_UNIXTIME(ts)       -- 时间戳转日期
```

### 4. 聚合函数（配合 GROUP BY 用）

```sql
COUNT(*)      -- 行数
COUNT(col)    -- 该列非 NULL 的行数（注意区别！）
SUM(col)      -- 求和
AVG(col)      -- 平均值（自动忽略 NULL）
MAX(col) / MIN(col)
GROUP_CONCAT(col)  -- 分组内拼接，如 '数学,语文,英语'
```

### 5. 条件函数

```sql
IF(条件, 值1, 值2)              -- IF(score >= 60, '及格', '不及格')
IFNULL(a, b)                    -- a 为 NULL 则返回 b
CASE WHEN ... THEN ... ELSE ... END
-- 例子：CASE WHEN score >= 90 THEN 'A' WHEN score >= 60 THEN 'B' ELSE 'C' END
```

### 6. 加密函数

```sql
MD5('abc')      -- 32位哈希（已不推荐存密码）
SHA2('abc', 256) -- SHA-256 哈希
PASSWORD()      -- 已废弃，别用
```

### 面试小心机
问函数时顺手说出几个"坑"是加分项：
- `COUNT(*)` 和 `COUNT(1)` 在现代 MySQL 性能没区别（都是数行数），`COUNT(col)` 才是数非 NULL
- `LENGTH` 是字节、`CHAR_LENGTH` 是字符
- 对索引列用函数（如 `WHERE YEAR(create_time) = 2026`）会让索引**失效**，应写成 `WHERE create_time >= '2026-01-01' AND create_time < '2027-01-01'`

---

## 13. SQL 查询语句的执行顺序是怎么样的？

### 一句话回答
**FROM → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT**，书写顺序和逻辑执行顺序不一致。

### 完整顺序表（面试必背）

```sql
SELECT DISTINCT 列          -- 6. 投影列
FROM 表                     -- 1. 确定数据来源
JOIN 表 ON 条件             -- 2. 连表（JOIN 先于 ON 之前的 WHERE）
WHERE 过滤条件              -- 3. 行级过滤
GROUP BY 分组列             -- 4. 分组
HAVING 分组后过滤            -- 5. 对分组结果过滤
ORDER BY 排序列             -- 7. 排序
LIMIT 数量                  -- 8. 截取
```

### 执行顺序背后的逻辑

1. **FROM/JOIN**：先决定"从哪些表拿数据"，JOIN 生成中间大表
2. **WHERE**：在中间结果上**逐行**过滤，**此时还不能用聚合函数和别名**
3. **GROUP BY**：按列分组，每组一行
4. **HAVING**：对**分组后**的结果过滤（可以用聚合函数，如 `HAVING COUNT(*) > 2`）
5. **SELECT**：计算并投影要返回的列（别名在这一步才生成）
6. **DISTINCT**：去重
7. **ORDER BY**：排序（所以 ORDER BY 可以用别名）
8. **LIMIT**：最后截取行数

### 为什么 WHERE 不能用聚合函数？

因为执行顺序里 WHERE 在 GROUP BY **之前**，此时还没有分组，无法计算 SUM/COUNT 等。所以"筛选分组"必须用 HAVING：

```sql
-- 错误：WHERE 里用聚合
SELECT class_id, COUNT(*) FROM student WHERE COUNT(*) > 5 GROUP BY class_id;

-- 正确：HAVING 过滤分组
SELECT class_id, COUNT(*) FROM student GROUP BY class_id HAVING COUNT(*) > 5;
```

### 为什么 WHERE 不能使用 SELECT 里的别名？

因为 SELECT 在 WHERE **之后**才执行，别名还没生成：

```sql
-- 错误
SELECT name AS n FROM student WHERE n = '张三';
-- 正确
SELECT name AS n FROM student WHERE name = '张三';
-- ORDER BY 可以用别名（执行顺序靠后）
SELECT name AS n FROM student ORDER BY n;
```

### 一个综合例子

```sql
SELECT class_id, COUNT(*) AS cnt, AVG(score) AS avg_score
FROM student_score
WHERE score IS NOT NULL          -- 先过滤行
GROUP BY class_id                -- 再分组
HAVING COUNT(*) >= 10            -- 过滤"人数>=10"的班级
ORDER BY avg_score DESC          -- 按平均分排序
LIMIT 5;                         -- 取前5
```