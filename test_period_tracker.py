import cv2
import numpy as np
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Setup WebDriver
service = Service(ChromeDriverManager().install())
options = Options()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--window-size=1920,1080")  # Set fixed window size
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 5)

# Open Login Page (Replace with correct path)
file_path = os.path.abspath("login.html")
driver.get("file://" + file_path)

# Store test results
test_results = []

def log_test(test_name, condition):
    if condition:
        test_results.append(f"✅ {test_name} - Passed")
    else:
        test_results.append(f"❌ {test_name} - Failed")

# ---------------- TEST CASES ----------------

# Test Case 1: Empty Login Fields
driver.find_element(By.ID, "loginButton").click()
time.sleep(1)
message = driver.find_element(By.ID, "message").text
log_test("Empty Login Fields", "Invalid" in message)

# Test Case 2: Incorrect Login
driver.find_element(By.ID, "username").send_keys("wrong_user")
driver.find_element(By.ID, "password").send_keys("wrong_pass")
driver.find_element(By.ID, "loginButton").click()
time.sleep(1)
message = driver.find_element(By.ID, "message").text
log_test("Incorrect Login", "Invalid" in message)

# Test Case 3: Correct Login
driver.find_element(By.ID, "username").clear()
driver.find_element(By.ID, "password").clear()
driver.find_element(By.ID, "username").send_keys("test_user")
driver.find_element(By.ID, "password").send_keys("test_pass")
driver.find_element(By.ID, "loginButton").click()
time.sleep(2)
driver.refresh()
wait.until(EC.presence_of_element_located((By.ID, "prediction")))
log_test("Correct Login", driver.find_element(By.ID, "prediction").is_displayed())

# Test Case 4: Empty Prediction Fields
driver.find_element(By.ID, "predictButton").click()
time.sleep(1)
prediction = driver.find_element(By.ID, "predictionResult").text
log_test("Empty Prediction Fields", "Please enter all details" in prediction)

# Test Case 5: Invalid Cycle Length
driver.find_element(By.ID, "lastPeriod").send_keys("2025-03-01")
driver.find_element(By.ID, "cycleLength").send_keys("15")
driver.find_element(By.ID, "predictButton").click()
time.sleep(1)
prediction = driver.find_element(By.ID, "predictionResult").text
log_test("Invalid Cycle Length", "Cycle length must be between 21 and 35 days." in prediction)

# Test Case 6: Valid Period Prediction
driver.find_element(By.ID, "cycleLength").clear()
driver.find_element(By.ID, "cycleLength").send_keys("28")
driver.find_element(By.ID, "predictButton").click()
time.sleep(1)
prediction = driver.find_element(By.ID, "predictionResult").text
log_test("Valid Period Prediction", "Next period" in prediction)

# Test Case 7: UI Comparison
screenshot_path = "actual_ui.png"
if os.path.exists(screenshot_path):
    os.remove(screenshot_path)
driver.save_screenshot(screenshot_path)

expected_path = "expected_ui.png"
if not os.path.exists(expected_path):
    test_results.append("❌ UI Comparison - Expected UI image not found!")
else:
    expected_img = cv2.imread(expected_path)
    actual_img = cv2.imread(screenshot_path)
    if expected_img is None or actual_img is None:
        test_results.append("❌ UI Comparison - One of the images failed to load!")
    else:
        expected_img = cv2.resize(expected_img, (actual_img.shape[1], actual_img.shape[0]))
        expected_gray = cv2.cvtColor(expected_img, cv2.COLOR_BGR2GRAY)
        actual_gray = cv2.cvtColor(actual_img, cv2.COLOR_BGR2GRAY)
        difference = cv2.absdiff(expected_gray, actual_gray)
        cv2.imwrite("diff.png", difference)
        log_test("UI Comparison", np.sum(difference) == 0)

# Test Case 8: Logout Functionality
try:
    logout_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Logout']")))
    logout_button.click()
    time.sleep(1)
    redirect_check = "login.html" in driver.current_url
    local_storage_check = driver.execute_script("return localStorage.getItem('loggedIn');") is None
    log_test("Logout Functionality", redirect_check and local_storage_check)
except Exception as e:
    test_results.append(f"❌ Logout Functionality - {str(e)}")

# Display Summary of All Tests
print("\n📝 Test Summary:")
for result in test_results:
    print(result)

print("\n✅ All Tests Completed!")

# Close Browser
driver.quit()
