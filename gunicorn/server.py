#-*- coding:utf-8 -*- 
from flask import Flask,jsonify,request,abort,render_template
import sys,logging,os
from threading import current_thread
import os
from time import sleep
app = Flask(__name__,root_path=".")
app.jinja_env.globals.update(zip=zip)
logger = logging.getLogger("WebServer")
import random

randint = random.random()
@app.route("/")
def index():
    pid = os.getpid()
    print(randint)
    return render_template('index.html',pid=pid)

@app.route('/test',methods=['GET'])
def test():

    pid = os.getpid()
    print(randint)
    print(pid)
    aa = ['a2','a1']
    bb = ['b2','b1']
    return render_template('test.html',aa=aa,bb=bb,randint=randint,pid=pid)


def startup():
    logging.basicConfig(
        format='%(asctime)s : %(levelname)s : %(message)s',
        level=logging.DEBUG,
        handlers=[logging.StreamHandler()])
    logger.debug('子进程:%s,父进程:%s,线程:%r', os.getpid(), os.getppid(), current_thread())
    logger.debug("初始化TF各类参数")
    logger.debug('web目录:%s', app.root_path)

startup()

