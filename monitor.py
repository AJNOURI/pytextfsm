#!/usr/bin/env python
import yaml
import pexpect
import multiprocessing
import logging
from xml.dom.minidom import Document
import time
import paramiko

logger = logging.getLogger(__name__)

### Manually set logging level
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)

handler = logging.FileHandler('initconfig.log', mode='w')
# Create logging format and bind to root logging object
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
# Create file handler
handler.setFormatter(formatter)
logger.addHandler(handler)
filelog = True


class InitDev(object):
    def __init__(self, ip=" ", hostname=" ", login="admin", passwd="cisco", \
                 cmdlist=[], ci=1, flog=False, \
                 telnetport="23", sshport="22", \
                 testrun=1, iteration=1, tout=30):

        self.ip = str(ip)
        self.hostname = str(hostname)
        self.login = str(login)
        self.passwd = str(passwd)
        self.cmdlist = cmdlist
        self.ci = ci
        self.flog = flog
        self.telnetport = str(telnetport)
        self.sshport = str(sshport)
        self.testrun = testrun
        self.iteration = iteration
        self.tout = tout


    def telnet(self):
        try:
            logger.debug('telnet()- ip: ' + self.ip)
            logger.debug('telnet()- login: ' + self.login)
            logger.debug('telnet()- password: ' + self.passwd)
            logger.debug('telnet()- telnetport: ' + str(self.telnetport))
            logger.debug('telnet()- tout: ' + str(self.tout))

            self.child = pexpect.spawn('telnet', ['-l', self.login, self.ip, self.telnetport], self.tout)
            self.child.setecho(False) # Turn off tty echo
            index = self.child.expect(['.*sername.*'])
            self.child.sendline(self.login)
            index = self.child.expect(['.*assword.*'])
            # privileged level
            self.child.sendline(self.passwd)
            self.child.expect(['.*#.*'])

            # No terminal length limit
            self.child.sendline('term len 0')
            self.child.expect(['.*#.*'])
        except pexpect.ExceptionPexpect, e:
            print e.value
        logger.info('Successful Telnet authentication to host ' + self.ip)


    def ssh(self):#IP,command, login , hostname, testid, testrun, iteration, sshpass):
        # SSH paramiko send list of commands
        filelist = []
        for cmdi in self.cmdlist:
            self.sshobj = paramiko.SSHClient()
            self.sshobj.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.sshobj.connect(self.ip, username=self.login, password=self.passwd, allow_agent=False, look_for_keys=False)
            logger.info('Successful SSH authentication to host ' + self.ip)
            logger.debug('SSH sendCmds()- hostname : ' + self.hostname)
            logger.debug('SSH sendCmds()- file logging : ' + str(self.flog))

            logger.debug('SSsendCmds()- cmdi: ' + cmdi)
            stdin,stdout,stderr=self.sshobj.exec_command(cmdi)

            if self.flog:
                logger.debug('sendCmds()- file logging enabled ')
                filen = mkfile(cmdi, self.ci, self.testrun, self.iteration, self.hostname)
                file=open(filen, "w")
                for line in stdout.readlines():
                    file.write(line.strip('\r\n')+'\r\n')
                file.close()
                filelist.append(filen)


            else:
                logger.debug('sendCmds()- file logging disabled ')

            print 'paramiko ssh: ',cmdi,' DONE'
        return filelist
        self.sshobj.close()



    def TSendCmds(self):
        # Telnet pexpect send list of commands
        # old sendCmds
        logger.debug('Telnet sendCmds()- hostname : ' + self.hostname)
        logger.debug('Telnet sendCmds()- file logging : ' + str(self.flog))

        if self.flog:
            logger.debug('sendCmds()- file logging enabled ')
        else:
            logger.debug('sendCmds()- file logging disabled ')

        for cmdi in self.cmdlist:
            logger.debug('sendCmds()- cmdi: ' + cmdi)
            self.child.sendline(cmdi)
            self.child.expect(['.*#.*'])

            if self.flog:

                logger.debug('sendCmds()- Logging command result to file...')

                filename = mkfile(cmdi, self.ci, self.testrun, self.iteration, self.hostname)
                fout = file(filename, 'w')
                fout.write(self.child.after)
                self.child.logfile = fout
                return filename
            else:

                logger.debug(self.ip + ': ' + cmdi + ' done...')
        # Close the socket after executing the list of commands
        self.child.close()
        logger.debug('\n ### sendCmds()- All commands for host ' +
                     self.hostname + ': ' + self.ip + ' Successfully executed\n\n')


def readYaml(cmdfile):
    """
    Read router credentials + commands from yaml file
    :param cmdfile: YAML- format file
    :return: list of parameters
    """
    logger.debug('\n\n\n### Reading YAML command file ',  cmdfile)
    stream = open(cmdfile)
    data = yaml.load(stream)
    logger.debug('\n\n\n### Device data rdata ', data)
    return data
    # handle file exceptions

def remoteDev(rdata, flg=False, timeout=300):
    """
    Send parameter list read from yaml file to be executed in the device
    ex: remoteDev("init.yaml", flg=False)
    :param rdata: list of credentials and commands to execute
    :param flg: log command result to a file if True
    :param timeout: 5min, telnet (pexpect timeout for executing the command)
    :return: nothing or produce file in flog=True
    """

    if rdata:
        for key, value in rdata.iteritems():
            cmdlist = []
            #print key.strip('\r\n')
            hostname = key.strip('\r\n')
            #logger.debug(value)

            #logger.debug('ip: ' + value[0]['ip'])
            ip = value[0]['ip']

            #logger.debug('login: ' + value[1]['login'])
            login = value[1]['login']

            #logger.debug('password: ' + value[2]['password'])
            password = value[2]['password']

            #logger.debug('sleep: ' + str(value[3]['sleep']))
            sleep = value[3]['sleep']
            for cmd in value[4:len(value)+1]:
                #print cmd
                cmdlist.append(cmd)
            print cmdlist
            conn = InitDev(ip, hostname, login, password, cmdlist, ci=1, flog=flg, tout=timeout)
            #conn.telnet()
            #conn.TSendCmds()
            filelist = conn.ssh()
            logger.info('Sleeping : ' + str(sleep) + ' seconds... (remoteDev)')
            time.sleep(sleep)
            return filelist
    else:
        # rise exception
        logger.debug('File ' + rdata + ' empty')


def ssh_linux (ip, command, testid, testrun, iteration, username, sshpass):

    sshobj = paramiko.SSHClient()
    sshobj.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshobj.connect(ip, username, sshpass)
    stdin, stdout, stderr = sshobj.exec_command(command)

    stdin.flush()
    print stdout.readlines()
    sshobj.close()


def mkfile(command, testid, testrun, iteration, hostname):

    under_command = command.replace(':', '_')
    under_command = under_command.replace('.', '_')
    under_command = under_command.replace('/', '_')
    filename = 'C' + str(testid) + '_TR' + str(testrun) + '_IT' + str(iteration) + '_'+ hostname +'_'+ under_command
    filename = filename.replace(' ', '_')
    return filename


def para_ssh (IP,command, login , hostname, testid, testrun, iteration, sshpass):
    sshobj = paramiko.SSHClient()
    sshobj.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshobj.connect(IP,username=login,password=sshpass,allow_agent=False,look_for_keys=False)
    stdin,stdout,stderr=sshobj.exec_command(command)
    filen = mkfile(command, testid, testrun, iteration, hostname)
    file=open(filen, "w")
    for line in stdout.readlines():
        file.write(line.strip('\r\n')+'\r\n')
    file.close()
    sshobj.close()
    print 'parassh: ',command,' DONE'
    return filen, command

#OK
# single command : to include in the class InitDev
#f,c = para_ssh('192.168.0.207','sh cry ipsec sa', 'admin' ,'IOU7', '1', '1', '1', 'cisco')



# main program

# Get device data dictionary from a YAML FILE
#remoteDev(readYaml('cmds.yaml'), flg=True, timeout=300)
#print remoteDev(readYaml('cmds.yaml'), flg=True, timeout=300)


# Get device data dictionary from a script Dictionary object
dataDict = {'R1': [\
    {'ip': '192.168.0.207'}, \
    {'login': 'admin'}, \
    {'password': 'cisco'}, \
    {'sleep': 0}, \
    'sh ip eigrp neighbors'
    ]}

print remoteDev(dataDict, flg=True, timeout=300) # command result file name

# fn: apply textfsm to (filename + template)
# get a list of lists
# fn: extract needed inf from list of lists & synthesize a boolean value
