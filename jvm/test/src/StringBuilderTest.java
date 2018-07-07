/** 
 * 该类并不是对StringBuilder进行解释，而是提供了中方式，方便我们来使用javassist的一些细节 
 * @author xianglj 
 * @date 2016/7/13 
 * @time 9:59 
 */  
public class StringBuilderTest {  
    /** 
     * 假如我们现在需要计算该程序的计算时间: 
     * 则可以标记开始时间(start)和结束时间(end) 
     * 最终的执行时间为(end - start)的值 
     * @param length 
     * @return 
     */  
    public String buildString(int length) {  
        String result = "";  
        for(int i = 0; i<length; i++ ) {  
            result += (i %26 + 'a');  
        }  
        return result;  
    }  
  
    public static void main(String[] args) {  
        /** 
         * class.getName()返回的字符串中，不仅包括了类的名称，同时也包含了该类所在的包名称 
         * <pre> 
         *     格式: 
         *     packagename.classname 
         * </pre> 
         */  
//        System.out.println(StringBuilderTest.class.getName());  
        StringBuilderTest test = new StringBuilderTest();  
        if(null != args) {  
            for(int i = 0, len = args.length; i<len; i++) {  
                String result = test.buildString(Integer.parseInt(args[i]));  
                System.out.println("result:" + result);  
            }  
        }  
    }  
}  