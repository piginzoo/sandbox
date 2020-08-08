import jieba

print(list(jieba.cut("标准保费（元）加费（元）")))
print(list(jieba.cut("保障金额（元）保险期间")))
print(list(jieba.cut("保障合同成立日：2007年07月06日保险期合同生效日：2008年01月01日")))