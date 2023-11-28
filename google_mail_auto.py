from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager as CDM

# login_info.txt 파일에 ID/Password 부분 수정 필요
def get_login_info():
    with open("login_info.txt", "r") as file:
        login_info = file.readlines()
    return {
        "id": login_info[0].strip(),
        "password": login_info[1]
    }

class EmailAutomation:
    def __init__(self, login_info):
        self.login_info = login_info
        service = Service(executable_path=CDM().install())
        options = Options()
        options.add_experimental_option("detach", True)
        options.add_argument('--start-maximized')
        options.add_argument("--disable-blink-features=AutomationControlled")

        self.driver = webdriver.Chrome(service=service, options=options)

        self.driver.get("https://google.com")

        login_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "gb_za")))
        login_btn.click()
        
        def init_login():
            active_element = self.driver.switch_to.active_element
            active_element.send_keys(login_info["id"])
            id_next_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="identifierNext"]/div/button')))
            id_next_btn.click()
            password_enter = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input')))
            password_enter.send_keys(login_info["password"])
            password_next_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="passwordNext"]/div/button')))
            password_next_btn.click()
        # 구글 로그인 2단계 인증 필요할 경우 자체 해결 
        
        def init_home_to_gmail():
            google_app_Menu = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.CLASS_NAME, "gb_g")))
            google_app_Menu.click()
            self.driver.switch_to.frame('app')
            gmail_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/c-wiz/div/div/div[2]/div[2]/div[1]/ul/li[7]/a')))
            gmail_btn.click()
            
        init_login()
        init_home_to_gmail()
        
    def send_mail(self, recipients, subject, description):
        self.driver.switch_to.default_content()
        compose_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[7]/div[3]/div/div[2]/div[1]/div[1]/div/div')))
        compose_btn.click()
        self.driver.switch_to.default_content()
        recipients_box = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'agP')))
        recipients_box.send_keys(recipients)
        subject_box = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.NAME, 'subjectbox')))
        subject_box.send_keys(subject)
        description_box = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'Am')))
        description_box.send_keys(description)
        send_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'dC')))
        send_btn.click()
        
    def delete_last_mail(self):
        test_mail_check = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'y2')))
        test_mail_check.click()
        self.driver.switch_to.default_content()
        delete_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id=":4"]/div[2]/div[1]/div/div[2]/div[3]/div')))
        delete_btn.click()
    
    def get_last_email_info(self, description):
        self.driver.switch_to.default_content()
        return {
            "email": WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'zF'))).get_attribute('email'),
            "title": WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'bqe'))).get_attribute('innerText'),
            "description": WebDriverWait(self.driver, 10).until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'y2'), description))
        }
        
    def __del__(self):
        self.driver.quit()

def validation(login_info, email:EmailAutomation):
    try:
        last_email_info = email.get_last_email_info("test description")
    except TimeoutException:
        print("시간 초과")
        return True
    if last_email_info["email"] != login_info["id"]:
        print(login_info["id"])
        print(last_email_info["email"])
        print("메일 수신자 불일치")
        return True
    if last_email_info["title"] != 'test title':
        print(last_email_info["title"])
        print("메일 제목 불일치")
        return True
    if not last_email_info["description"]:
        print(last_email_info["description"])
        print("메일 내용 불일치")
    email.delete_last_mail()
    print("테스트 정상")
    return False
        
def main():
    login_info = get_login_info()
    email = EmailAutomation(login_info)
    email.send_mail(login_info["id"], "test title", "test description")
    if validation(login_info, email):
        return

main()