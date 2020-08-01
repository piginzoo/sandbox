import re
rex = re.compile(' ')
def ignore_symbol(sentence):
    ignore_symbol = "＠＃＄％＾＆＊（）－＿＋＝｛｝［］｜＼＜＞，．。；：､？／×·■﹑@#$%^&*()-_+={}[]|\<>,.。;:、?/x..、"
    result = ""
    # 先去除空格
    sentence = rex.sub('', sentence)
    for one in sentence:
        i = ignore_symbol.find(one)
        if i != -1: continue
        result += one
    return result