import re
# Untilities 
# You can add anything you want
class Utils:
    def __init__(self, data) -> None:
        self.data = data
    # Function used to strip strings and set desc=title if the desc is empty
    def nomalize_text(self):
        self.data["name"] =  self.data["name"].strip()
        if self.data["description"] is not None: 
            self.data["description"] =  self.data["description"].strip()
        else:
            self.data["description"] = self.data["name"].strip()

    # Used to check if the datast has a null title for further decisions 
    def has_null_title(self):
        if self.data["name"] == None:
            return True
        else:
            return False
    

# Custom printer 
def cprint(text):
    print(f":> {text}")