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

def remove_pos(poses, pos):
    for __pos in poses:
        if (__pos==pos).all():
            poses.remove(__pos)
            return pos