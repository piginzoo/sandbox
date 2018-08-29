# 贪心科技的项目实践

    项目地址：http://greedyai.com/course/19/task/49/show

## 1.解析文件
    没啥难度，就是体力活，用的是BeautifulSoup
    然后调用Tushare工具来获取，官网为 http://tushare.org/index.html，并可以从官网下载Tushare工具包。 
    下载完之后，在python里即可以调用股票行业和概念信息。
    
## 2.转成neo4j需要的格式
    参考：https://neo4j.com/docs/operations-manual/current/tutorial/import-tool/
    很容易理解，就是按照neo4j需要的格式准备即可

## 任务6： 利用已经构建好的知识图谱，并通过编写cypher语句回答以下几个问题

(1)  有多少个公司目前是属于 “ST”类型的？ 
    match p=(:ST) return count(*)

(2) “600519” 公司的所有独立董事人员中，有多少人同时也担任别的公司的独立董事职位？
    MATCH (s:Stock {code:'600519'})-[r]-(e:Executive) 
    where r.executive="独立董事"
    return count(r)

(3) 有多少公司既属于环保行业，又有外资背景？
    MATCH (s:Stock)-[r1]-(i:Industry),(s:Stock)-[r2]-(c:Concept) 
    where i.c_name="环保行业" and c.c_name="外资背景"
    return s

(4) 对于有锂电池概念的所有公司，独立董事中女性人员比例是多少？
    MATCH (s:Stock)-[r2]-(c:Concept),(s:Stock)-[r1]-(e:Executive) 
    where c.c_name="锂电池" and e.executive="独立董事"
    return s,e        




 