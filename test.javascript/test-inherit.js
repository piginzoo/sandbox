function Parent(){
	this.name = ["切云：qiecloud.com"];
}

function Child(){
}

Child.prototype = new Parent();

var c1 = new Child();
var c2 = new Child();
console.log(c1.name);
console.log(c2.name);
c1.name.push("chuang");
console.log(c1.name);
console.log(c2.name);


var person = new Object();
person.name = "Nicholas";
person.age = 29;
person.job = "Software Engineer";
person.sayName = function(){
	console.log(this.name);
};

var person = {
	name: "Nicholas",
	age: 29,
	job: "Software Engineer",
	sayName: function(){
		console.log(this.name);
	}
};
