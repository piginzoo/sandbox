import javassist.*;  
  
import java.io.IOException;  
  
/** 
 * 通过Javassist来为需要实现计算的方法前后各加上一个拦截器， 
 * 依次来实现方法计算的时间 
 * <pre> 
 *     1. 添加的代码不能引用在方法中其他地方定义的局部变量。这种限制使我不能在 Javassist 中使用在源代码中使用的同样方法实现计时代码， 
 *        在这种情况下，我在开始时添加的代码中定义了一个新的局部变量，并在结束处添加的代码中引用这个变量。 
 * 
 *     2. 我 可以在类中添加一个新的成员字段，并使用这个字段而不是局部变量。不过，这是一种糟糕的解决方案， 
 *        在一般性的使用中有一些限制。例如，考虑在一个递归方法中会发生的事情。每次方法调用自身时，上次保存的开始时间值就会被覆盖并且丢失。 
 * 
 *     3. 我可以保持原来方法的代码不变，只改变方法名，然后用原来的方法名增加一个新方法。 
 * </pre> 
 * @author xianglj 
 * @date 2016/7/13 
 * @time 10:07 
 */  
public class JavassistTiming {  
    public static void main(String[] args) {  
        //开始获取class的文件  
        javassist();  
    }  
  
    public static void javassist() {  
        //开始获取class的文件  
        try {  
//            String classFileName = StringBuilderTest.class.getName();  
            String classFileName = "StringBuilderTest";  
            CtClass ctClass = ClassPool.getDefault().getCtClass(classFileName);  
            if(ctClass == null) {  
                System.out.println("Class File (" + classFileName + ") Not Found.....");  
            } else {  
                addTiming(ctClass, "buildString");  
                //为class添加计算时间的过滤器  
                ctClass.writeFile();  
            }  
            Class<?> clazz = ctClass.toClass();  
            StringBuilderTest test = (StringBuilderTest) clazz.newInstance();  
            test.buildString(20000);  
  
        } catch (NotFoundException e) { //类文件没有找到  
            e.printStackTrace();  
        } catch (CannotCompileException e) {  
            e.printStackTrace();  
        } catch (IOException e) {  
            e.printStackTrace();  
        } catch (InstantiationException e) {  
            e.printStackTrace();  
        } catch (IllegalAccessException e) {  
            e.printStackTrace();  
        }  
    }  
  
    /** 
     * 为方法添加拦截器: 
     * <pre> 
     *     构造拦截器方法的正文时使用一个 java.lang.StringBuffer 来累积正文文本(这显示了处理 String 的构造的正确方法， 
     *     与在 StringBuilder 的构造中使用的方法是相对的)。这种变化取决于原来的方法是否有返回值。 
     *     如果它 有返回值，那么构造的代码就将这个值保存在局部变量中，这样在拦截器方法结束时就可以返回它。 
     *     如果原来的方法类型为 void ，那么就什么也不需要保存，也不用在拦截器方法中返回任何内容。 
     * </pre> 
     * @param clazz 方法所属的类 
     * @param method 方法名称 
     */  
    private static void addTiming(CtClass clazz, String method) throws NotFoundException, CannotCompileException {  
  
        //获取方法信息,如果方法不存在，则抛出异常  
        CtMethod ctMethod = clazz.getDeclaredMethod(method);  
        //将旧的方法名称进行重新命名，并生成一个方法的副本，该副本方法采用了过滤器的方式  
        String nname = method + "$impl";  
        ctMethod.setName(nname);  
        CtMethod newCtMethod = CtNewMethod.copy(ctMethod, method, clazz, null);  
  
        /* 
         * 为该方法添加时间过滤器，用来计算时间。 
         * 这就需要我们去判断获取时间的方法是否具有返回值 
         */  
        String type = ctMethod.getReturnType().getName();  
        StringBuffer body = new StringBuffer();  
        body.append("{\n long start = System.currentTimeMillis();\n");  
  
        if(!"void".equals(type)) {  
            body.append(type + " result = ");  
        }  
  
        //可以通过$$将传递给拦截器的参数，传递给原来的方法  
        body.append(nname + "($$);\n");  
  
        //  finish body text generation with call to print the timing  
        //  information, and return saved value (if not void)  
        body.append("System.out.println(\"Call to method " + nname + " took \" + \n (System.currentTimeMillis()-start) + " +  "\" ms.\");\n");  
        if(!"void".equals(type)) {  
            body.append("return result;\n");  
        }  
  
        body.append("}");  
  
        //替换拦截器方法的主体内容，并将该方法添加到class之中  
        newCtMethod.setBody(body.toString());  
        clazz.addMethod(newCtMethod);  
  
        //输出拦截器的代码块  
        System.out.println("拦截器方法的主体:");  
        System.out.println(body.toString());  
    }  
}  