""" ssh framework
basic paramiko framework to enable access to routers
demonstrates the two techniques as described in the conceptual article """

import paramiko
import getpass
import time


def user_credentials_prompt():
    """ user credentials prompt """

    # user message
    usr_msg = "Please type in your router credentials."
    print(usr_msg)

    # user credential prompt
    user = input('User: ')
    user_pw = getpass.getpass('User Password: ')
    enable_pw = getpass.getpass('Enable Password: ')

    # console formatting
    print('')

    return user, user_pw, enable_pw

class SSHTimerMethod:

    def __init__(self):
        self.user, self.user_pw, self.enable_pw = user_credentials_prompt()

    def login(self, switch):
        """ login
        logs into specified switch """

        # set up ssh client
        ssh_setup = paramiko.SSHClient()

        # add missing host key policy (set as auto)
        ssh_setup.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # connect to switch
        ssh_setup.connect(
            switch, 
            username=self.user, 
            password=self.user_pw, 
            look_for_keys=False, 
            allow_agent=False,
            )
        # set up transport channel for session
        transport = ssh_setup.get_transport()

        # invoke session
        self.ssh_session = transport.open_session()

        # set up for interactive mode, multiple commands - pty
        self.ssh_session.get_pty()

        # invoke session's shell
        self.ssh_session.invoke_shell()

        # keep session active with parameters while class is initialized
        self.ssh_session.keep_this = ssh_setup

    def enable_mode(self):
        """ enable mode timer method
        user the timer method to get into enable mode """

        self.send_command('enable', DELAY=1)
        self.send_command(self.enable_pw, DELAY=1)

    def no_paging(self):
        """ no paging timer method
        user the timer method to remove any paging """

        self.send_command('terminal len 0', DELAY=1)

    def send_command(self, command, DELAY=5):
        """ send command timer method
        this sends our commands to the switches, but through the timer
        method, the default delay set as 5 seconds! """

        # send command over to switch
        self.ssh_session.send(command + '\n')

        # delay by specified delay
        time.sleep(DELAY)

        # initialize the data received from switch
        data = self.ssh_session.recv(1).decode('utf-8')

        # read from socket while there is data
        while self.ssh_session.recv_ready():
            # keep reading 512 bytes of data from socket
            data += self.ssh_session.recv(512).decode('utf-8')

            # minor delay to allow cpu some breathing room
            time.sleep(.0001)


        return data

    def close_ssh_session(self):
        """ close ssh session
        closes the current session so that there are no hanging ssh threads """

        self.ssh_session.close()

class SSHTrailingMethod:

    def __init__(self):
        self.user, self.user_pw, self.enable_pw = user_credentials_prompt()

    def login(self, switch):
        """ login
        logs into specified switch """

        # set up ssh client
        ssh_setup = paramiko.SSHClient()

        # add missing host key policy (set as auto)
        ssh_setup.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # connect to switch
        ssh_setup.connect(
            switch, 
            username=self.user, 
            password=self.user_pw, 
            look_for_keys=False, 
            allow_agent=False,
            )
        # set up transport channel for session
        transport = ssh_setup.get_transport()

        # invoke session
        self.ssh_session = transport.open_session()

        # set up for interactive mode, multiple commands - pty
        self.ssh_session.get_pty()

        # invoke session's shell
        self.ssh_session.invoke_shell()

        # keep session active with parameters while class is initialized
        self.ssh_session.keep_this = ssh_setup

    def enable_mode(self):
        """ enable mode expect trailing method
        user the expect trailing method to get into enable mode """

        self.send_command('enable')
        self.send_command(self.enable_pw)

    def no_paging(self):
        """ no paging expect trailing method
        user the expect trailing method to remove any paging """

        self.send_command('terminal len 0')

    def send_command(self, command):
        """ send command expect trailing method
        this sends our command to the switches, but through the expect
        trailing method! """

        # send command over to the switch
        self.ssh_session.send(command + '\n')

        # initialize the data received from switch
        data = self.ssh_session.recv(1).decode('utf-8')

        while True:
            # read from socket, if there is data to be read
            if self.ssh_session.recv_ready():
                # keep reading 512 bytes of data from socket
                data += self.ssh_session.recv(512).decode('utf-8')

            # grab current last line from collected socket, subject to
            # keep changing as more data flows in
            current_last_line = data.splitlines()[-1].strip()

            # check if there are spaces in the line, skip if so
            if ' ' in current_last_line:
                continue
            # enable mode
            elif current_last_line.endswith('#'):
                break
            # password prompt
            elif current_last_line.endswith(':'):
                break

            # minor delay to allow cpu some breathing room
            time.sleep(.0001)

        return data

    def close_ssh_session(self):
        """ close ssh session
        closes the current session so that there are no hanging ssh threads """

        self.ssh_session.close()

