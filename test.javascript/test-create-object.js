function Person(name){
	this.name = name;
	this.hello = function(){
		console.log("hello:"+this.name);
	}
}
var p1 = new Person("qiecloud");
var p2 = new Person("qiecloud");
p1.hello();
console.log(p1.hello==p2.hello);//==>false
console.log(p1.__proto__);
console.log(Object.getPrototypeOf(p1));
console.log(Person.prototype.isPrototypeOf(p1));
//---------------

