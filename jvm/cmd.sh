 javac -cp lib/javassist-3.16.1-GA.jar test/src/*.java  -d out
 jar cvfm test.jar MANIFEST.MF -C out/ .
 java -javaagent:test.jar Example
 java -classpath ../out:../lib/javassist-3.16.1-GA.jar JavassistTiming