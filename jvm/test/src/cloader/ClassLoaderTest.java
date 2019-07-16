public class ClassLoaderTest {

    public static void main(String[] args) {
        // TODO Auto-generated method stub

        ClassLoader cl = HelloWorld.class.getClassLoader();

        System.out.println("ClassLoader is:"+cl.toString());
		System.out.println("ClassLoader\'s parent is:"+cl.getParent().toString());        
		System.out.println("ClassLoader\'s grand father is:"+cl.getParent().getParent().toString());

    }

}