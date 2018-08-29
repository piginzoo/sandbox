neo4j-admin import \
--database "greedyai" \
--nodes "neo4jdata/executive.csv" \
--nodes "neo4jdata/stock.csv" \
--nodes "neo4jdata/concept.csv" \
--nodes "neo4jdata/industry.csv"  \
--relationships "neo4jdata/executive_stock.csv" \
--relationships "neo4jdata/stock_industry.csv" \
--relationships "neo4jdata/stock_concept.csv"
