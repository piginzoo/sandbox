r = open("ruitu.cn.txt","r",encoding="utf-8")
file = open("ruitu.ok.txt","w",encoding="utf-8")
lines = r.readlines()

for i,line in enumerate(lines):
    line = line.strip()

    if len(line)>8:
        index = line.find("；")
        if index ==-1:
            index = line.find(";")

        if index!=-1:
            line = line[0:index]

    if line=="":
        if i!=0 and lines[i-1].strip()!="":
            file.write("\n")
    else:
        file.write(line)
        file.write("\n")
file.close()
# python filter.py