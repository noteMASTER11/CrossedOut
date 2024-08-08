import sys
import json
import requests
import re
import unidecode
import urllib.parse
import yaml
import os
import platform
import webbrowser
import browser_cookie3
from openpyxl import Workbook
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QMessageBox, QProgressBar, QCheckBox, QSpacerItem, QSizePolicy
from PyQt5.QtCore import QThread, pyqtSignal, Qt

# Путь к конфигурационным файлам
config_file_path = 'config.yml'
welcome_file_path = 'welcomescreen.yml'
last_search_file_path = 'last_search.json'


# Функция для загрузки конфурационного файла
def load_config():
    with open(config_file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


# Функция для сохранения конфигурации в файл
def save_config(config):
    with open(config_file_path, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)


# Функция для загрузки Welcome-экран данных
def load_welcome_data():
    with open(welcome_file_path, 'r') as file:
        welcome_data = yaml.safe_load(file)
    return welcome_data


# Функция для сохранения последнего поиска
def save_last_search(data):
    with open(last_search_file_path, 'w') as file:
        json.dump(data, file, indent=4)


# Функция для загрузки последнего поиска
def load_last_search():
    try:
        with open(last_search_file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return {}


# Функция для получения токена li_at
def get_li_at_token():
    cj = browser_cookie3.chrome(domain_name='www.linkedin.com')
    li_at_cookie = None
    for cookie in cj:
        if cookie.name == 'li_at':
            li_at_cookie = cookie.value
            break
    return li_at_cookie


class ParsingWorker(QThread):
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(list)

    def __init__(self, data):
        super().__init__()
        self.data = data

    def run(self):
        li_at = self.data['li_at']
        urls = [u.strip() for u in self.data['urls']]  # Разделение на несколько URL
        max_employees = self.data['max_employees']
        position_filters = [f.strip().lower() for f in self.data['position_filter'].split(',')]
        results_summary = []

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Content-type': 'application/json',
            'Csrf-Token': "ajax:5739908118104050450"
        }
        cookies = {"li_at": li_at, "JSESSIONID": "ajax:5739908118104050450"}

        def get_company_id(company):
            company_encoded = urllib.parse.quote(company)
            api1 = f"https://www.linkedin.com/voyager/api/voyagerOrganizationDashCompanies?decorationId=com.linkedin.voyager.dash.deco.organization.MiniCompany-10&q=universalName&universalName={company_encoded}"
            r = requests.get(api1, headers=headers, cookies=cookies, timeout=200)
            response1 = r.json()
            company_id = response1["elements"][0]["entityUrn"].split(":")[-1]
            return company_id

        def get_employee_data(company_id, start, count=10):
            api2 = f"https://www.linkedin.com/voyager/api/search/dash/clusters?decorationId=com.linkedin.voyager.dash.deco.search.SearchClusterCollection-165&origin=COMPANY_PAGE_CANNED_SEARCH&q=all&query=(flagshipSearchIntent:SEARCH_SRP,queryParameters:(currentCompany:List({company_id}),resultType:List(PEOPLE)),includeFiltersInResponse:false)&count={count}&start={start}"
            r = requests.get(api2, headers=headers, cookies=cookies, timeout=200)
            response2 = r.json()
            return response2

        def clean_data(data):
            emoj = re.compile("["
                              u"😀-🙏"  # emoticons
                              u"🌀-🗿"  # symbols & pictographs
                              u"🚀-🛿"  # transport & map symbols
                              u"🇠-🇿"  # flags (iOS)
                              u"─-⯯"  # chinese char
                              u"✂-➰"
                              u"✂-➰"
                              u"Ⓜ-🉑"
                              u"🤦-🤷"
                              u"𐀀-􏿿"
                              u"♀-♂"
                              u"☀-⭕"
                              u"‍"
                              u"⏏"
                              u"⏩"
                              u"⌚"
                              u"️"  # dingbats
                              u"〰"
                              "]+", re.UNICODE)

            cleaned = re.sub(emoj, '', data).strip()
            cleaned = cleaned.replace('Ü', 'Ue').replace('Ä', 'Ae').replace('Ö', 'Oe').replace('ü', 'ue').replace('ä',
                                                                                                                  'ae').replace(
                'ö', 'oe')
            cleaned = cleaned.replace(',', '')
            cleaned = unidecode.unidecode(cleaned)
            return cleaned.strip()

        def parse_employee_results(results, position_filters=None):
            employee_dict = []

            for employee in results:
                try:
                    account_name = clean_data(employee["itemUnion"]['entityResult']["title"]["text"]).split(" ")
                    badwords = ['Prof.', 'Dr.', 'M.A.', ',', 'LL.M.']
                    for word in list(account_name):
                        if word in badwords:
                            account_name.remove(word)

                    if len(account_name) == 2:
                        firstname = account_name[0]
                        lastname = account_name[1]
                    else:
                        firstname = ' '.join(map(str, account_name[0:(len(account_name) - 1)]))
                        lastname = account_name[-1]
                except:
                    continue

                try:
                    position = clean_data(employee["itemUnion"]['entityResult']["primarySubtitle"]["text"])
                except:
                    position = "N/A"

                if position_filters and not any(pf in position.lower() for pf in position_filters):
                    continue

                try:
                    location = employee["itemUnion"]['entityResult']["secondarySubtitle"]["text"]
                except:
                    location = "N/A"

                try:
                    profile_link = employee["itemUnion"]['entityResult']["navigationUrl"].split("?")[0]
                except:
                    profile_link = "N/A"

                employee_dict.append(
                    {"firstname": firstname, "lastname": lastname, "position": position, "location": location,
                     "profile_link": profile_link})

            return employee_dict

        def save_to_json(company_name, employees):
            filename = f"{company_name}.json"
            with open(filename, mode='w', encoding='utf-8') as file:
                json.dump(employees, file, indent=4, ensure_ascii=False)
            return filename

        def save_to_xlsx(company_name, employees):
            directory = os.path.join('lnkd_excel_results', company_name)
            os.makedirs(directory, exist_ok=True)
            file_path = os.path.join(directory, f'{company_name}.xlsx')

            wb = Workbook()
            ws = wb.active
            ws.title = "Employees"

            # Header
            ws.append(["FirstName", "LastName", "Position", "Location", "ProfileLink"])

            # Data
            for emp in employees:
                ws.append([emp["firstname"], emp["lastname"], emp["position"], emp["location"], emp["profile_link"]])

            wb.save(file_path)
            return file_path

        for url in urls:  # Обработка каждого URL
            if url.startswith('https://www.linkedin.com/company/'):
                try:
                    before_keyword, keyword, after_keyword = url.partition('company/')
                    company = after_keyword.split('/')[0]

                    company_id = get_company_id(company)

                    employee_dict = []
                    total_parsed = 0
                    page = 0

                    while total_parsed < max_employees:
                        api2_response = get_employee_data(company_id, page * 10)
                        page += 1

                        if not api2_response["elements"]:  # Если больше нет сотрудников для парсинга
                            print(f"[i] No more employees found. Total parsed: {total_parsed}")
                            break

                        for i in range(3):
                            try:
                                results = api2_response["elements"][i]["items"]
                                parsed_results = parse_employee_results(results, position_filters=position_filters)
                                employee_dict.extend(parsed_results)
                                total_parsed += len(parsed_results)
                                self.progress.emit(total_parsed, max_employees)
                                if total_parsed >= max_employees:
                                    break
                            except:
                                pass
                        if total_parsed >= max_employees:
                            break

                    json_filename = save_to_json(company, employee_dict)
                    xlsx_filename = save_to_xlsx(company, employee_dict)
                    results_summary.append(f"{company}: {len(employee_dict)} employees collected")

                    # Удаление JSON файла и открытие директории с .xlsx файлом
                    os.remove(json_filename)
                    # Открытие директории в зависимости от операционной системы
                    if platform.system() == "Windows":
                        os.startfile(os.path.dirname(xlsx_filename))
                    elif platform.system() == "Darwin":  # macOS
                        os.system(f"open {os.path.dirname(xlsx_filename)}")
                    else:  # Linux
                        os.system(f"xdg-open {os.path.dirname(xlsx_filename)}")

                except Exception as e:
                    print("[!] Exception. Either API has changed and this script is broken or authentication failed.")
                    print("    > Set 'li_at' variable permanently in script or use the '--cookie' CLI flag!")
                    print("[debug] " + str(e))
                    results_summary.append(f"{company}: Parsing failed or no employees found.")

            else:
                print("[!] Invalid URL provided.")
                results_summary.append(f"{url}: Invalid URL.")

        # Передача сигнала об успешном завершении с результатами
        self.finished.emit(results_summary)


class MainWindow(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.selected_employee_count = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('LinkedIn Employee Parser')
        self.setGeometry(100, 100, 1000, 800)

        layout = QVBoxLayout()

        # LinkedIn 'li_at' Token (автоопределение)
        self.config['linkedin']['li_at'] = get_li_at_token()
        save_config(self.config)

        # LinkedIn Company URL
        self.url_label = QLabel('LinkedIn Company URL(s) (comma separated):')
        self.url_input = QTextEdit(self)
        self.url_input.setFixedHeight(80)
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)

        # Number of Employees to Parse
        self.num_employees_label = QLabel('Number of Employees to Parse:')
        layout.addWidget(self.num_employees_label)

        # Кнопки для выбора количества сотрудников
        self.button_group = QHBoxLayout()
        self.buttons = []

        for count in [10, 50, 100, 500, 1000, 5000]:
            button = QPushButton(f'{count}')
            button.setCheckable(True)
            button.clicked.connect(lambda _, c=count: self.select_employee_count(c))
            self.button_group.addWidget(button)
            self.buttons.append(button)

        layout.addLayout(self.button_group)

        # Filter by Position (optional)
        self.position_label = QLabel('Filter by Position (optional):')
        self.position_input = QTextEdit(self)
        self.position_input.setFixedHeight(50)
        layout.addWidget(self.position_label)
        layout.addWidget(self.position_input)

        # Start Parsing Button
        self.start_button = QPushButton('Start Parsing', self)
        self.start_button.clicked.connect(self.on_start)
        layout.addWidget(self.start_button)

        # Loader (ProgressBar)
        self.loader = QProgressBar(self)
        self.loader.setRange(0, 100)  # Диапазон от 0 до 100
        self.loader.setVisible(False)
        layout.addWidget(self.loader)

        # Total collected
        self.total_collected_label = QLabel("Total collected 0/0")
        layout.addWidget(self.total_collected_label)

        self.setLayout(layout)

    def select_employee_count(self, count):
        self.selected_employee_count = count
        for button in self.buttons:
            button.setChecked(False)
        button = self.sender()
        button.setChecked(True)

    def update_progress(self, n, m):
        self.loader.setValue(int((n / m) * 100))
        self.total_collected_label.setText(f"Total collected {n}/{m}")

    def on_start(self):
        # Проверка выбора количества сотрудников
        if self.selected_employee_count is None:
            QMessageBox.warning(self, "Warning", "Please select the number of employees to parse.")
            return

        # Деактивация кнопки и активация лоадера
        self.start_button.setEnabled(False)
        self.loader.setVisible(True)

        # Получение данных из полей ввода
        li_at = self.config['linkedin']['li_at']
        url = self.url_input.toPlainText()
        urls = [u.strip() for u in url.split(',')]  # Разделение URL по запятой
        max_employees = self.selected_employee_count
        position_filter = self.position_input.toPlainText().lower()

        # Сохранение последнего поиска
        data = {
            'li_at': li_at,
            'urls': urls,  # Передача списка URL
            'max_employees': max_employees,
            'position_filter': position_filter
        }
        save_last_search(data)

        # Запуск парсинга в отдельном потоке
        self.thread = ParsingWorker(data)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def on_finished(self, results_summary):
        # Активация кнопки и деактивация лоадера после завершения работы
        self.start_button.setEnabled(True)
        self.loader.setVisible(False)

        # Отображение результатов
        result_text = "\n".join(results_summary)
        QMessageBox.information(self, "Parsing Completed", result_text)


class WelcomeScreen(QWidget):
    def __init__(self, config, main_window):
        super().__init__()
        self.config = config
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Welcome')
        self.setGeometry(300, 300, 400, 200)  # Размер окна уменьшен

        layout = QVBoxLayout()

        # Текст Welcome
        welcome_message = QLabel(
            "Helloworld! This application is based on the LinkedInDumper CLI script which could be seen here: https://github.com/l4rm4nd/LinkedInDumper by LRVT")
        welcome_message.setWordWrap(True)
        welcome_message.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_message)

        # Кнопка Visit original author's GitHub
        github_button = QPushButton("Visit original author's GitHub")
        github_button.clicked.connect(lambda: webbrowser.open('https://github.com/l4rm4nd/LinkedInDumper'))
        layout.addWidget(github_button)

        # Spacer item
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Нижняя часть с кнопками
        bottom_layout = QHBoxLayout()

        self.do_not_show_again = QCheckBox("Do not show again")
        bottom_layout.addWidget(self.do_not_show_again)

        continue_button = QPushButton('Continue')
        continue_button.clicked.connect(self.on_continue)
        bottom_layout.addWidget(continue_button, alignment=Qt.AlignRight)

        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    def on_continue(self):
        if self.do_not_show_again.isChecked():
            self.config['show_welcome'] = False
            save_config(self.config)
        self.close()
        self.main_window.show()


class AppController(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.config = load_config()
        self.main_window = MainWindow(self.config)

        if self.config.get('show_welcome', True):
            self.welcome_screen = WelcomeScreen(self.config, self.main_window)
            self.welcome_screen.show()
        else:
            self.main_window.show()


if __name__ == '__main__':
    app = AppController(sys.argv)
    sys.exit(app.exec_())
