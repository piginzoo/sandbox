console.log("test closure")

var i = 0;
console.log(i instanceof Object);

var a = [1,"2",3];
console.log(a);
console.log(a.toString());
console.log(a.valueOf());

function test(){
	var var1 = 0;
	return function(){
		console.log(var1);
		var1++;
	}
}
var f  = test();
f();
f();
f();
f();
//闭包就是能够读取其他函数内部变量的函数 <JS高编>P179
/**
定义期：
函数的内部属性[[Scope]]
函数的作用域链：函数创建的作用域中对象的集合，它决定了哪些数据能被函数访问

运行期：
执行上下文: 定义了函数执行时的环境. ?是附着在哪个对象上，还是全局的
		每个运行期上下文都有自己的作用域链，用于标识符解析
		被创建时，而它的作用域链初始化为当前运行函数的[[Scope]]所包含的对象
活动对象：该对象包含了函数的所有局部变量、命名参数、参数集合以及this
		此对象会被推入作用域链的前端
		当运行期上下文被销毁，活动对象也随之销毁		
*/
