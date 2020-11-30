from git import Repo
from git import Git
from git import exc
from zipfile import ZipFile
from base64 import standard_b64encode
import web
import os
import os.path
import string

urls = ('/build/(.*)/(.*)', 'build')

def validate(project):
    for char in project:
        if char == '-' or char in string.ascii_letters:
            continue
        else:
            return False

    return True

class build():

    def GET(self, user, project):

        print(user, project)

        if not validate(user):
            return 'haha'

        if not validate(project):
            return 'haha'

        try:
            # clone the repo from the verio github
            repo = Repo.clone_from('git@github.com:' + user + '/' + project + '.git', os.path.join('./builds/', project))
        except exc.GitCommandError as e:
            # we assume that the error is cause the repository has already been cloned
            # so we just pull the latest commits
            print(e)
            print('pullin')
            Git(os.path.join('./builds/', project)).pull()
      
        # build the downloaded project using maven (assuming it uses java, of course)
        os.system('mvn clean package -f ' + ('./builds/' + project + '/pom.xml'))  

        # create a zip file on ./builds/(project).zip
        zip = ZipFile(os.path.join('./builds/', project + '.zip'), 'w')
       
        # loop through all jar files in the target directory
        for file in os.listdir('./builds/' + project + '/target/'):
            if file.endswith('.jar'): 
                # add the current file to the zip
                zip.write('./builds/' + project + '/target/' + file)

        # close the zip file
        zip.close()

        web.header('Content-type', 'application/octet-stream')
        web.header('Content-transfer-encoding', 'base64') 
        web.header('Content-Disposition', 'filename="' + project + '.zip"') 

        # return standard_b64encode(open('./builds/' + project + '.zip', 'rb').read())
        return open('./builds/' + project + '.zip', 'rb').read()

if __name__ == '__main__':
    app = web.application(urls, globals())
    app.run()

