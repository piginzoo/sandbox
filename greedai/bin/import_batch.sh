neo4j stop 
rm -rf /Users/piginzoo/software/neo4j-community-3.3.5/data/databases/greedyai 
rm /Users/piginzoo/software/neo4j-community-3.3.5/conf/neo4j.conf
cp /Users/piginzoo/software/neo4j-community-3.3.5/conf/neo4j.conf.origin /Users/piginzoo/software/neo4j-community-3.3.5/conf/neo4j.conf
py neo4j_data_converter.py 
neo4j start
bin/import.sh
neo4j stop
rm /Users/piginzoo/software/neo4j-community-3.3.5/conf/neo4j.conf
cp /Users/piginzoo/software/neo4j-community-3.3.5/conf/neo4j.conf.greedyai /Users/piginzoo/software/neo4j-community-3.3.5/conf/neo4j.conf
neo4j start
