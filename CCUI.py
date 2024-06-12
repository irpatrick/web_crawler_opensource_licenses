from http.client import HTTPException
import json
import os
import subprocess
from time import sleep
from xml.etree.ElementInclude import include
# from scrapy.crawler import CrawlerProcess
# from scrapy import cmdline
from apis.api import API
from spiders.dynamic import DynamicSpider

from spiders.fetchopensouce import FetchOpenSource
from spiders.licenses import LicenceAnalyser
from spiders.static import StaticSpider
# from dotenv import load_dotenv
from storage.sql_db import Database
from utils.classifier import Classify
from utils.util import cprint


"""
To add a script / command

1. Create a class which inherit from the class Command
2. Create a constructor ex:
def __init__(self) -> None:
        # Assigning a command name
        self.COMMAND_NAME = ["opensource"]
    
3. You can create any methode you wnat but the most important is exec which ovarrides the parent methode with your executions
4. Add a documentation variable to the class created ex: DOCUMENTATION = {"key":"command", "value":"description"}
*** Under the CrawlerUCLI class ***
5. Add the command in the self.commands_level_one variable ex: self.commands_level_one = ['show', 'publish', ...]
6. Create the command ex: publish = PablishCommand() and append it to the  self.commands_list list ex:  self.commands_list = [show, crawl, publish, ...]
7. Finaly go to ShowManuel class and add the command documentation for users to be able to see it in the terminal. 
ex: soted_list = sorted([
                {"key": "clear", "value": "To clean the terminal"},
                {"key": "close", "value": "Close the program"},
                {"key": "exit", "value": "Exit from a loop or another function"},
                self.DOCUMENTATION,
                Show.DOCUMENTATION, ])
Good luck!!

"""


CONFIG_FILE_URI="./configs/config.json"
GIT_REPOS_URI="./configs/git_repos.json"

class Information():
    title = ""
    body = []
    step=0
    def __init__(self, title, body) -> None:
        self.title = title
        self.body = body
        if len(self.body) < 10:
            self.step=0
        else:
            self.step = int(len(self.body)/7)


class Command():
    COMMAND_NAME = []
    DOCUMENTATION = {}

    def exec(self, *args, **kwargs):
        cprint(f"Executing command {self.COMMAND_NAME}")

class Show(Command):
    DOCUMENTATION = {"key":"show", "value":"Dispaly lists of 'show' commands"}
    def __init__(self, info,  close, name) -> None:
        self.COMMAND_NAME = name
        self.information = info
        self.close = close

    def escaper(self, text, tabs):
        if len(text)<tabs:
            return " " * (tabs-len(text))
        return""

    def exec(self, *args, **kwargs):
        cprint("")
        cprint(f"{self.information.title}")
        cprint("")       
        c = 0
        steps = self.information.step
        # Fin the number of ecaptes
        tabs = max([len(el.get('key')) for el in self.information.body])
        number_of_elements = len(self.information.body)
        for element in self.information.body:
            c+=1
            if steps == 0:
                pass
            else:
                if (c%7 == 0):
                    cprint("Press 'ENTER' to go to the next page ('exit' to go back, close to 'close' the app)")
                    command = input(":> ")
                    if command is None:
                        pass
                    elif command == 'close':
                        self.close()
                    elif command == 'exit':
                        break

            cprint(f"{c}. {self.escaper(f'{c}', len(f'{number_of_elements}'))} {element.get('key')} {self.escaper(element.get('key'), tabs)} {element.get('value')}")

class ShowWebsites(Show):
    DOCUMENTATION = {"key":"show websites", "value":"To show a list of configured websites"}
    def __init__(self, close) -> None:
        CONFIG_FILE = open(CONFIG_FILE_URI)
        CONFIGS = json.load(CONFIG_FILE)
        body = []
        for conf in CONFIGS:
            body.append({"key":f"NO: {conf.get('id')}", "value":conf.get("description")})
        info = Information(
                title="List of available websites",
                body=body
            )
        super().__init__(info, close, ["show", "websites"])


class ShowCountries(Show):
    DOCUMENTATION =  {"key":"show countries", "value":"To show a list of countries"}
    def __init__(self, close) -> None:
        countries_file = open('african_countries.json')
        countries_list = json.load(countries_file)
        body = []
        for c in countries_list:
            body.append({"key":c, "value":""})

        info = Information(
                title="List of available countries",
                body=body
            )
        
        super().__init__(info=info, close=close, name=["show", "countries"])


class OpenSourceFetch(Command):
    DOCUMENTATION = {"key":"opensource", "value":"To fetch repos based on a given topic"}
    
    def __init__(self) -> None:
        self.COMMAND_NAME = ["opensource"]
        
    def exec (self, *args, **kwargs):
        choice = input(":> Enter a topic: ")
        fetcher = FetchOpenSource(topic=choice)
        fetcher.crawl()
    

class OpenLicensesCollecter(Command):
    DOCUMENTATION =  {"key":"license", "value":"Crawl a list of github repot's lices file"}
    TEST = False
    SELECTED_CONF = {}
    FILE_DIR = "./data/licenses.json"
    def __init__(self) -> None:
        self.COMMAND_NAME = ["license"]
        self.CONFIG_FILE = open(GIT_REPOS_URI)
        self.CONFIGS = json.load(self.CONFIG_FILE)

    def exec (self, *args, **kwargs):

        # process = DynamicSpider(self.SELECTED_CONF, DB=d, TEST=self.TEST)
        process = LicenceAnalyser(self.CONFIGS, self.FILE_DIR)
        process.crawl()
       
                


class Crawler(Command):
    DOCUMENTATION =  {"key":"crawl", "value":"Crawl a website. Follow the guidelines"}
    TEST = False
    SELECTED_CONF = {}
    DIRECTORY = "./data/"
    def __init__(self, show_websites:ShowWebsites, show_countries:ShowCountries) -> None:
        # load_dotenv()
        # self.TEST =  True if int(str(os.getenv("TEST"))) == 1 else False
        self.COMMAND_NAME = ["crawl"]
        self.READY = False
        self.DEFAULT = False
        self.CONFIG_FILE = open(CONFIG_FILE_URI)
        self.COUNTRIES_FILE = open('african_countries.json')
        self.CONFIGS = json.load(self.CONFIG_FILE)
        self.COUNTRIES_LIST = json.load(self.COUNTRIES_FILE)
        self.show_websites = show_websites
        self.show_countries = show_countries

    def execution_ (self,):
        d = Database()
        # Create a class for the script execution and configure the class such that the directory is created once 
        if not os.path.exists(self.DIRECTORY):
            os.makedirs(self.DIRECTORY, exist_ok=True)
        if os.path.exists(f'{self.SELECTED_CONF["file_name"]}.json') and (d.check_if_db_isempty()!=0):
                self.SELECTED_CONF["file_name"] = self.SELECTED_CONF["file_name"]+"new"
        with open(f'{self.SELECTED_CONF["file_name"]}.json', 'w') as f:
                f.write('\n[')

        #  Check if the wesite is a JS Rendered website
        if self.SELECTED_CONF["is_dynamic"]:
            process = DynamicSpider(self.SELECTED_CONF, DB=d, TEST=self.TEST)
            process.crawl()
        else:
            process = CrawlerProcess()
            # Add your spider to the process
            process.crawl(StaticSpider, CONFIGS=self.SELECTED_CONF, DB=d, TEST=self.TEST)
            # cmdline.execute("scrapy runspider scrapywebcro.py -O".split())
            # Start the crawling process
            process.start()
            
        with open(f'{self.SELECTED_CONF["file_name"]}.json', 'a') as f:
            f.write('\n]')
        d.close_connection()

    

    def exec(self, *args, **kwargs):
        # Load configurations again
        self.CONFIG_FILE = open(CONFIG_FILE_URI)
        self.CONFIGS = json.load(self.CONFIG_FILE)
        # 
        self.show_websites.exec()
        choice = input(":> Which site doyou want to crawl: ")
        
        for element in self.CONFIGS:
            if  str(element.get('id')) == str(choice):
                self.SELECTED_CONF = element
                break

        if self.SELECTED_CONF:
        #   If the selected configs requires some filtering
        #   The user can choose a country to filter by
            self.READY = True
           
            #  5 is a magic choice
            if self.SELECTED_CONF.get("choose_country"):
                country = input(":>Choose a country: ")
            
                # Country names to lower case
                countries = [c.lower() for c in self.COUNTRIES_LIST]
                if country.lower() in countries:
                    start_url = self.SELECTED_CONF['start_url'].replace("african_country", country)
                    self.SELECTED_CONF["start_url"] = start_url
                    file_name = self.SELECTED_CONF['file_name'] + country
                    self.SELECTED_CONF['file_name'] = file_name
                elif  country == '5':
                    self.DEFAULT = True
                else:
                    cprint("The selected country does not exist!!")
                    self.show_countries.exec()
                    self.READY = False
        # 
        if self.READY and len(self.SELECTED_CONF)!=0:
            cprint("=======================================")
            cprint("")
            cprint("=======================================")
            cprint("")
            cprint("Very good!!")
            cprint("")
            cprint("The domain: "+ self.SELECTED_CONF["domain"])
            cprint("Start URL: "+ self.SELECTED_CONF["start_url"])
            # If the file has rules
            if self.SELECTED_CONF.get('is_dynamic') is False:
                cprint("Dataset traversal rule: "+ self.SELECTED_CONF['rules'][0]['allow'])
                cprint("Restriction rule: "+ self.SELECTED_CONF["rules"][0]["deny"])
                cprint("Single dataset visit rule: "+ self.SELECTED_CONF["rules"][1]["allow"])
                cprint("Restriction rule: "+ self.SELECTED_CONF["rules"][1]["deny"])
            cprint("=======================================")
            cprint("")
            is_ok = input(":>If all is ok press 1")
            if is_ok == '1':
                if self.DEFAULT is False:
                    self.execution_()
                else:
                    start_url = self.SELECTED_CONF['start_url'].replace("african_country", self.COUNTRIES_LIST[0])
                    self.SELECTED_CONF["start_url"] = start_url
                    file_name = self.SELECTED_CONF['file_name'] + self.COUNTRIES_LIST[0]
                    self.SELECTED_CONF['file_name'] = file_name
                    # Create a CrawlerProcess
                    self.execution_()            
        else:
            pass

# The main interface
class CrawlerTest(Crawler):
    DOCUMENTATION =  {"key":"crawl test", "value":"Crawl a website for testing. (SQL database is OFF)"}
    def __init__(self, show_websites: ShowWebsites, show_countries: ShowCountries) -> None:
        super().__init__(show_websites, show_countries)
        self.COMMAND_NAME = ["crawl", "test"]
        self.TEST = True


class ClassifyCommand(Command):
    DOCUMENTATION = {"key": "classify", "value": "To class data based on the 17 SDGS"}
    def __init__(self, ) -> None:
        # self.api = API()
        self.db = Database()
        self.classify = Classify()
        self.COMMAND_NAME = ["classify"]
        super().__init__()
    
    def exec(self, *args, **kwargs):
        try:
            print("Hello") 
            self.classify.class_by_sdgs(self.db)
           
        except HTTPException as e:
            cprint(e)


class Publish(Command):
    DOCUMENTATION = {"key": "publish", "value": "To send data to OPEN DATA API "}
    def __init__(self, ) -> None:
        self.api = API(TEST=False)
        self.COMMAND_NAME = ["publish"]
        super().__init__()


    def exec(self, *args, **kwargs):
        try:
            loggedIn = self.api.authenticate()
            if loggedIn:
                self.api.publish_link()
            else:
                print("SYS Closed!")
        except HTTPException as e:
            cprint(f"Network request error: {e}")


class PublishTest(Command):
    DOCUMENTATION = {"key": "publish test", "value": "To send data to OPEN DATA API TEST API"}
    def __init__(self, ) -> None:
        self.api = API(TEST=True)
        self.COMMAND_NAME = ["publish", "test"]
        super().__init__()


    def exec(self, *args, **kwargs):
        try:
            loggedIn = self.api.authenticate()
            if loggedIn:
                self.api.publish_link()
            else:
                print("SYS Closed!")
        except HTTPException as e:
            cprint(f"Network request error: {e}")


class ShowManuel(Show):
    DOCUMENTATION = {"key": "show man", "value": "To show all available commands"}
    def __init__(self, close) -> None:
        # List of all commands documentations
        soted_list = sorted([
                {"key": "clear", "value": "To clean the terminal"},
                {"key": "close", "value": "Close the program"},
                {"key": "exit", "value": "Exit from a loop or another function"},
                self.DOCUMENTATION,
                Show.DOCUMENTATION,
                ShowCountries.DOCUMENTATION,
                ShowWebsites.DOCUMENTATION,
                Crawler.DOCUMENTATION,
                CrawlerTest.DOCUMENTATION,
                Publish.DOCUMENTATION,
                ClassifyCommand.DOCUMENTATION,
                PublishTest.DOCUMENTATION,
                OpenLicensesCollecter.DOCUMENTATION,
                OpenSourceFetch.DOCUMENTATION
            ], key=lambda el: el['key'])
        
        info = Information(
            title="List of available commands",
            body= soted_list
        )
        super().__init__(info, close, ["show", "man"])




class CrawlerUCLI():
    command1 = None
    command2 = None
    command3 = None
    on = True
    commands = []
    c_len = 0

    INVALID_COMMAND_MESSAGE = "Note a valid command use show man to learn about the tool"

    def __init__(self) -> None:
        self.print_program_title()
        self.commands_level_one = ['show', 'crawl', 'publish', 'delete', 'exit', 'close', 'clear', 'jconfig', 'classify', 'license', 'opensource']
        self.commands_level_two = ['website', 'country', 'man', 'test', 'verify', 'db', 'file']
        info = Information(
            title="Available 'show' commands",
            body=[
                ShowCountries.DOCUMENTATION,
                ShowWebsites.DOCUMENTATION,
                ShowManuel.DOCUMENTATION
            ]
        )
        show = Show(info=info, close=self.close, name=["show"])
        show_manuel = ShowManuel(close=self.close)
        show_countries = ShowCountries(close=self.close) 
        show_websites = ShowWebsites(close=self.close)
        publish = Publish()
        publish_test = PublishTest()
        crawler = Crawler(show_countries=show_countries, show_websites=show_websites)
        crawler_test  = CrawlerTest(show_countries=show_countries, show_websites=show_websites)
        classify = ClassifyCommand()
        license = OpenLicensesCollecter()
        opensource = OpenSourceFetch()
        self.commands_list = [
            show_websites,
            show_countries,
            crawler,
            crawler_test,
            show,
            show_manuel,
            publish,
            classify,
            publish_test,
            license,
            opensource
        ]

    def __str__(self) -> str:
        return f"{self.command1} {self.command2} {self.command3} {self.commands} {self.c_len}"
    
    def validate_command(self, args):
        self.commands  = args.split(" ")    
        self.c_len = len(self.commands)

        if(self.c_len>3 or self.c_len==0):
            return {"code":1, "message": self.INVALID_COMMAND_MESSAGE}
        
        # check if the command submited is one of the recognized commands
        if self.commands[0] in self.commands_level_one: 
             self.command1 = self.commands[0]
        else:
            return {"code":1, "message": self.INVALID_COMMAND_MESSAGE}
        
        # check if the command submited is one of the recognized commands
        if self.c_len > 1:
            if (self.c_len == 2) or (self.c_len == 3 and self.commands[1] in self.commands_level_two):
                self.command2 = self.commands[1]
            else:
                return {"code":1, "message": self.INVALID_COMMAND_MESSAGE}
        
        # check if the command submited is one of the recognized commands
        if self.c_len == 3 :
            self.command3 = self.commands[2]  
         
        return {"code":0}
    
    def parse_args(self):
        while self.on:
            args = input(":> ")
            resp = self.validate_command(args)
            if(resp.get('code') == 0):
                self.execute_comand()
            
    
    def print_program_title(self):
        cprint("==================== OPEN DATA PORTAL CRAWL BOT ====================")
        cprint("Use 'show man' to learn the basic commands. 'close' to close the program")
        cprint("")


    def dosexec(self, args):
        subprocess.call(args,  shell=True)

    def clear(self):
        self.dosexec("cls")
        self.print_program_title()

    def close(self):
        self.on = False
     

    def execute_comand(self):
        
        if self.command1 == 'close':
            self.close()

        if self.command1 == 'clear':
            self.clear()

        for cm in self.commands_list:
            # cprint(cm.COMMAND_NAME)
            if cm.COMMAND_NAME == self.commands :
                cm.exec(self.commands)


if __name__ == '__main__':
    CrawlerUCLI().parse_args()
