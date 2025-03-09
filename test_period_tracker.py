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


def test_example():
    assert 1 == 1

# Setup WebDriver
service = Service(ChromeDriverManager().install())
options = Options()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 5)

# Open Login Page
file_path = os.path.abspath("login.html")
driver.get("file://" + file_path)

# Store test results
test_results = []

def log_test(test_name, condition):
    if condition:
        test_results.append(f"✅ {test_name} - Passed")
    else:
        test_results.append(f"❌ {test_name} - Failed")

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
log_test("Empty Prediction Fields", "Please enter both Last Period Date and Cycle Length." in prediction)

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

# Test Case 7: Symptom Tracker Log
wait.until(EC.presence_of_element_located((By.XPATH, "//a[text()='Symptom Tracker']"))).click()
time.sleep(1)
driver.find_element(By.ID, "mood").send_keys("Happy")
driver.find_element(By.ID, "cramps").click()
driver.find_element(By.XPATH, "//button[text()='Save Log']").click()
time.sleep(1)
symptom_logs = driver.find_element(By.ID, "symptomHistory").text
log_test("Symptom Tracker Log", "Happy" in symptom_logs and "cramps" in symptom_logs)

# Test Case 8: Clear Symptom History
driver.find_element(By.XPATH, "//button[text()='Clear Symptom History']").click()
time.sleep(1)
symptom_logs = driver.find_element(By.ID, "symptomHistory").text
log_test("Clear Symptom History", symptom_logs == "")

# Test Case 9: Logout Functionality
logout_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Logout']")))
logout_button.click()
time.sleep(1)
redirect_check = "login.html" in driver.current_url
local_storage_check = driver.execute_script("return localStorage.getItem('loggedIn');") is None
log_test("Logout Functionality", redirect_check and local_storage_check)

# Display Summary of All Tests
print("\n📝 Test Summary:")
for result in test_results:
    print(result)

print("\n✅ All Tests Completed!")

# Close Browser
driver.quit()
