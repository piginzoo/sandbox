//console.log('test');

var test1 = {
	testm1 : function(){
		console.log("testm1");
	}
}
var test2  = {}
var test3  = new Object();
console.log(typeof(test2));
console.log(typeof(test3));
console.log(typeof(test1));
console.log(typeof(test1.testm1));

var string1 = "string1";
var string2 = new String("string2");
console.log(typeof(string1));
console.log(typeof(string2));
console.log(string1.length);
console.log(string2.length);

console.log((new Boolean(false))?true:false);//结果为true

var num1 = 1;
var num = num1 + "a";
console.log(num);

var arr1 = ['']

function testargs(){
	for(var i = 0, len = arguments.length; i < len; i++){
		var arg = arguments[i];
		console.log(arg);
	}
}

testargs(100,200,300);
testargs("1","2","3",4);


var test = "test global";
function test_variable_scope(){
	console.log(test);//<---打印undefine
	var test = "test variable";
	console.log(test);
}
function test_variable_scope2(){
	console.log(test);//<---打印 test global
	//var test = "test variable";
	console.log(test);
}
test_variable_scope();
test_variable_scope2();


var obj1 = {
	name: "name1"
}
var obj2 = {
	name: "name2"
}
function printName(){ 
	console.log(this.name); 
}
console.log(printName);
printName.call(obj1);
printName.call(obj2);



function testcurry0(){
	return function(){
		console.log("i am curry");
	}
}
function testcurry1(c1){
	return function(c1){
		console.log(c1);
	}
}
function testcurry2(c1){
	return function(c1){
		return console.log;
	}
}
var curry_func = testcurry0();
curry_func();
curry_func = testcurry1("c1");
curry_func();
curry_func = testcurry2("c2");
curry_func("c2");


var arr1=[1,3,5,7,9,11];
var arr2=[2,4,6,8,10];
console.log(arr1.concat(arr2));
console.log(arr1.concat(arr2).join("|"));
console.log(arr1.pop()+"/"+arr1);
console.log(arr1.shift()+"/"+arr1);
console.log(arr1.push(111)+"/"+arr1);
console.log(arr1.unshift(-111)+"/"+arr1);
console.log(arr1.sort()+"/"+arr1);
console.log(arr2.splice(1,1)+"/"+arr2);//del 4
console.log(arr2.splice(1,0,4)+"/"+arr2);//insert 4,要求第二个参数为0
console.log(arr2.splice(1,2,40,60,80,100)+"/"+arr2);//replace


function Person(name){
	this.name = name;
	this.test= function(){};
}
var p1 = new Person("liuc");
console.log(Person.__proto__);
console.log(p1.__proto__);
console.log(p1.test);
var base={
	base1:function(){},
	base2:function(){}
}
console.log(base.__proto__);
var child={
	__proto__:base
}
console.log(child.__proto__);
console.log(child.base1);

var adder = function(num){ 
	return function(y){
		return num + y; 
	}
}
var inc = adder(1);
var dec = adder(-1);
console.log(inc(99));
console.log(dec(99));