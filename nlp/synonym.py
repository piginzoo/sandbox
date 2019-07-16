#-*- coding:utf-8 -*-
import synonyms
print (synonyms.seg("中文近义词工具包"))
print(synonyms.nearby("人脸"))
# print("识别: %r" % (synonyms.nearby("识别")))
# print("NOT_EXIST: %r" % (synonyms.nearby("NOT_EXIST")))

#银管通如何存管/银管通存管模式
sen1 = "银管通如何存管"
sen2 = "银管通存管模式"
sen3 = "我想了解一下银管通"
r = synonyms.compare(sen1, sen2, seg=True)
print("相似度:",r)
r = synonyms.compare(sen1, sen3, seg=True)
print("相似度:",r)
r = synonyms.compare(sen2, sen3, seg=True)
print("相似度:",r)