# https://zhuanlan.zhihu.com/p/144737398
import unittest
import selenium
import time
from appium import webdriver
 
class MyTestCase(unittest.TestCase):

    def setUp(self):
        # super().setUp()
        print('selenium version = ', selenium.__version__)
        desired_caps = {}
        desired_caps['platformName'] = 'Android'
        desired_caps['platformVersion'] = '9.0.0'
        desired_caps['deviceName'] = 'SM_G9600'
        desired_caps['appPackage'] = "com.sankuai.meituan"
        desired_caps['appActivity'] = "com.meituan.android.pt.homepage.activity.MainActivity"
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
 
 
    def testWaimai(self):

        el1 = self.driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value="外卖")
        el1.click()
        el2 = self.driver.find_element(by=AppiumBy.XPATH, value="/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.view.ViewGroup/android.support.v7.widget.RecyclerView/android.widget.RelativeLayout/android.support.v4.view.ViewPager/android.widget.FrameLayout/android.support.v7.widget.RecyclerView/android.widget.FrameLayout[1]/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout[1]/android.widget.FrameLayout")
        el2.click()


    def tearDown(self):
        self.driver.quit()
 
# python test_meituan.py 
if __name__ == '__main__':
    unittest.main()