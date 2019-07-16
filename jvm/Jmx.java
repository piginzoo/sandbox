import javax.management.MBeanServer;
import javax.management.ObjectName;
import java.lang.management.ManagementFactory;

class Hello implements HelloMBean {  
    //可读属性 不可写  
    private final String name = "gittudou";  
    private int  DEFUALT_CACHE_SIZE = 200;  
    //可读写属性  
    private int cacheSize = DEFUALT_CACHE_SIZE;  
  
    public void sayHello() {  
        System.out.print("hello jmx");  
    }  
  
    public int add(int x, int y) {  
        return x+y;  
    }  
  
    public String getName() {  
        return this.name;  
    }  
    //使用synchronized 同步控制 防止多个线程同时调用set方法  
    public synchronized void setCacheSize(int size) {  
       this.cacheSize = size;  
        System.out.println("Cache size now "+this.cacheSize);  
    }  
    public int getCacheSize() {  
        return this.cacheSize;  
    }  
}  

public class Jmx {  
    public static  void  main(String args[]) throws  Exception{  
        //获取MBeanServer  如果没有MBean server存在那么下面会自动调用ManagementFactory.createMBeanServer()  
        MBeanServer mBeanServer = ManagementFactory.getPlatformMBeanServer();  
        //包名加 类名 创建一个ObjectName  
        ObjectName name = new ObjectName("git.tudou.manage.jmx.test.essential:type=Hello");  
        //创建一个Hello实例  
        Hello mbean = new Hello();  
        //在MBean server上注册MBean  
        mBeanServer.registerMBean(mbean,name);  
        System.out.println("Waiting forever...");  
        //线程等待 management 操作   
        Thread.sleep(Long.MAX_VALUE);  
    }  
} 