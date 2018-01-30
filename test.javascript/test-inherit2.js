function SuperType(){
	this.property = true;
}

SuperType.prototype.getSuperValue = function(){
	return this.property;
};

function SubType(){
	this.subproperty = false;
}
//继承了SuperType
SubType.prototype = new SuperType();
SubType.prototype.getSubValue = function (){
	return this.subproperty;
};

var instance = new SubType();
console.log(instance.getSuperValue()); //true





function SuperType(){
	this.colors = ["red", "blue", "green"];
}
function SubType(){
	//继承了SuperType
	SuperType.call(this);
}
var instance1 = new SubType();
instance1.colors.push("black");
alert(instance1.colors); //"red,blue,green,black"
var instance2 = new SubType();
alert(instance2.colors); //"red,blue,green"


function SuperType(name){
	this.name = name;
}
function SubType(name){
	//继承了SuperType，同时还传递了参数
	SuperType.call(this, name);
	//实例属性
	this.age = 29;
}
var instance = new SubType("切云qiecloud.com");
alert(instance.name); //"Nicholas";
alert(instance.age); //29




function SuperType(name){
	this.name = name;
	this.colors = ["red", "blue", "green"];
}
SuperType.prototype.sayName = function(){
	alert(this.name);
};
function SubType(name, age){
	//继承属性
	SuperType.call(this, name);
	this.age = age;
}

//继承方法
SubType.prototype = new SuperType();
SubType.prototype.constructor = SubType;
SubType.prototype.sayAge = function(){
	alert(this.age);
};

var instance1 = new SubType("切云：qiecloud.com", 29);
instance1.colors.push("black");
alert(instance1.colors); //"red,blue,green,black"
instance1.sayName(); //"Nicholas";
instance1.sayAge(); //29
var instance2 = new SubType("qie", 27);
alert(instance2.colors); //"red,blue,green"
instance2.sayName(); //"Greg";
instance2.sayAge(); //27


function createFunctions(){
	var result = new Array();
	for (var i=0; i < 10; i++){
		
		var f = function(num){
			return function(){
				return num;
			};
		};

		result[i] = f(i);
	}
	return result;
}

function createFunctions(){
	var result = new Array();
	for (var i=0; i < 10; i++){
		result[i] = function(){
			return i;
		};
	}
	return result;
}


function createComparisonFunction(propertyName) {
	return function(object1, object2){
		var value1 = object1[propertyName];
		var value2 = object2[propertyName];
		if (value1 < value2){
			return -1;
		} else if (value1 > value2){
			return 1;
		} else {
			return 0;
		}
	};
}


var name = "The Window";
var object = {
		name : "My Object",
		getNameFunc : function(){
			return function(){
				return this.name;
			};
		}
	};
alert(object.getNameFunc()()); 
//"The Window"（在非严格模式下）

var name = "The Window";
var f = function(){
			return function(){
				return this.name;
			};
		}
	};
alert(f()()); 




var name = "The Window";
var object = {
	name : "My Object",
	getNameFunc : function(){
	var that = this;
		return function(){
			return that.name;
		};
	}
};
alert(object.getNameFunc()()); //"My Object"

