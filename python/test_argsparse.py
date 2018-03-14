#-*- coding:utf-8 -*-  
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--bank",help="--bank 银行名称(jianhang|renfa|nonghang)")
    parser.add_argument("--image",help="--image 图片名称(位于data/validate/<银行代号>/)")
    parser.add_argument("--test",type=int,help="--test 需要测试的图片数量")

    args = parser.parse_args()

    if args.bank == None:
    	parser.print_help()
    	exit()

    if args.test == None and args == None:
    	parser.print_help()
    	exit()

    if args.image != None:
    	print(args.bank+args.image)
    	exit()

    if args.test != None:
    	print(args.bank+str(args.test))
    	
    