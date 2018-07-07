import java.lang.instrument.IllegalClassFormatException;
import java.lang.instrument.Instrumentation;
import java.security.ProtectionDomain;
import java.lang.instrument.ClassFileTransformer;

public class Hello implements ClassFileTransformer {
  
    @Override  
    public byte[] transform(ClassLoader loader, String className,  
            Class<?> classBeingRedefined, ProtectionDomain protectionDomain,
            byte[] classfileBuffer) throws IllegalClassFormatException {
          
        System.out.println("java.lang.instrument, hello world!");  
        System.out.println("className:"+className);  
        System.out.println("classBeingRedefined:"+classBeingRedefined);  
          
        return null;  
    }  
      
    public static void premain(String args,Instrumentation inst){
        inst.addTransformer(new Hello());  
    }  
  
}  