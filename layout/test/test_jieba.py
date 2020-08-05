import jieba

print(list(jieba.cut("标准保费（元）加费（元）")))
print(list(jieba.cut("保障金额（元）保险期间")))