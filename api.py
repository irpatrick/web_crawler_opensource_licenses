# This fil 
from cgitb import text
import hashlib
import json
# from urllib import response
from h11 import Response
import requests
import time
from util import cprint
# from CCUI import print
from sql_db import Database
from dotenv import load_dotenv
import os



class API:
    
    token = ""

    def __init__(self, sleep_time=3, slot=10) -> None:
         # Load the environment variables from the .env file
        load_dotenv()
        self.email = os.getenv("EMAIL")
        self.password = os.getenv("PASSWORD")
        self.base_url = os.getenv("BASE_URL_LOCAL")
        self.slot = slot
        self.sleep_time = sleep_time

    def authorize(self, password):
        hash_object = hashlib.sha256()

        hash_object.update(bytes(f'{password}', 'utf-8'))
        in_password = hash_object.hexdigest()
        # print(in_password)
        store_password = os.getenv("HASH_PASSWORD")
        if in_password == store_password:
            return True
        return False

    def authenticate(self):
        url = f"{self.base_url}/login"
        
        headers = {
            "Content-Type": "application/json"
        }

        # Access the environment variables
        

        payload = {
            "email": self.email,
            "password": self.password,
        }

        response = requests.post(url, headers=headers, json=payload)

        if 200 <= response.status_code < 290:
            data = json.loads(response.text)
            self.token = data.get('token')
            cprint("===> Logged in ...")
            return True
        # Failed to login
        cprint(f"===> {response.text}")
        return False


    def send_http_post_request(self, link, d):
       
        if len(self.token) == 0:
            cprint("===> Authentication required") 
            raise Exception("Authentication required ...")
        # sleep_time = 3
        # Before each request spleep for $val t sec

        cprint(f"===> Sleeping for {self.sleep_time} sec ...")
        time.sleep(self.sleep_time)
        cprint("===> Sending the request ...")
        # Define the API endpoint URL
        url = f"{self.base_url}/link"

        # Define the token value

        # Define the request headers with the token
        headers = {
            "Authorization": f"{self.token}",
            "Content-Type": "application/json"
        }

        # Define the request payload 
        payload = {
            "link": link.data,
            "name": link.name,
            "description": link.description,
            "organization": link.organization,
            "isPrivate": link.isPrivate,
            "type": link.type,
            "category": link.category,
            "tags": link.tags
        }

        # Send the POST request
        response = requests.post(url, headers=headers, json=payload)
        # response = Response(headers=[], status_code=500)
        # Check the response
        cprint(f"===> Response satatus: {response.status_code}")
        if 200 <=  response.status_code < 290:
            cprint("===> Request successful")
            cprint("===> Updating the database unpublished => published")
            d.mark_as_visited(link.hash_value)
        else:
            cprint("===> Request failed")

        # Print the response content
        return response.text
       


    def publish_link(self,):
        cprint(" Enter the pass code first: ")
        pass_code = input(":>_ ")
        if self.authorize(password=pass_code):

            d = Database()
            results = d.get_all_links_by_publishment_status(count=self.slot)

            for r in results:
                response = self.send_http_post_request(r, d)
                cprint("===> Response from the server/gatway...")
                cprint(response)

            d.close_connection()
        else:
            cprint(" Invalid passcode")
# Tests are done here

# def main():
#     api = API()
#     api.publish_link()
#     # print(api.authorize("321"))
#     # # authenticate first 
#     # loggedIn = api.authenticate()
#     # if loggedIn:
#     #     api.publish_link()
#     # else:
#     #     print("===> SYS Closed!")

# main()