from launchpadlib.launchpad import Launchpad, STAGING_SERVICE_ROOT
from launchpadlib.credentials import Credentials
import os

class LP_Server(object):
    cachedir = ".launchpad/cache/"
    credential_file = ".launchpad/lp_credential.txt"    
    application = 'openobject'
    def get_lp(self):
        if not os.path.isdir(self.cachedir):            
            os.makedirs(self.cachedir)
            
        if not os.path.isfile(self.credential_file):        
            launchpad = Launchpad.get_token_and_login(self.application, STAGING_SERVICE_ROOT, self.cachedir)        
            launchpad.credentials.save(file(self.credential_file, "w"))
        else:        
            credentials = Credentials()
            credentials.load(open(self.credential_file))
            launchpad = Launchpad(credentials, STAGING_SERVICE_ROOT, self.cachedir)
        return launchpad

    def get_lp_people_info(self, launchpad, users):    
        res = {}
        if not isinstance(users,list):
            users = [users]
        for user in users:
            result = {}            
            for person in launchpad.people.find(text=user):
                result['karma'] = person.karma                       
                result['name'] = person.name
            res[user] = result    
        return res

if __name__ == '__main__':
    lp_server = LP_Server()
    lp = lp_server.get_lp()
    print lp_server.get_lp_people_info(lp, 'hmo-tinyerp')
    

        

