#! /usr/bin/env python 
# -*- coding: utf-8 -*-
def wrapper(func):
	def do_wrapper():
		print "before func"
		return func()
	return do_wrapper

@wrapper
def test123():
	print "test 123..."	

test123()

class TestClass:

	test = "ttttttt"

	#另一种写法，不过调用方式也不同
	def register2(self,func):
		print "register2"
		def do_register():
			print "register2:"+str(func)
			return func
		return do_register

	
	def register(self,p1="123",p2="456"):
		print "register"
		print locals()
		def do_register(func):
			print self.test
			print "register"+str(func)
			return func
		return do_register

print "------------"

t = TestClass()

@t.register()
def test456():
	print "test456"


print "------------"

@t.register2
def test789():
	print "test789"



