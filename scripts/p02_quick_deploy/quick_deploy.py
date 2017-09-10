from netmiko import ConnectHandler
from colorama import init
from colorama import Fore
import getpass

def quick_deploy_introduction():
    user_message = Fore.YELLOW + "# Quick Deploy Script v1.0"
    print(user_message)

def user_credentials_prompt():
    """ user credentials prompt """

    # user message
    usr_msg = "\nPlease type in your router credentials."
    print(usr_msg)

    # user credential prompt
    user = input('User: ')
    password = getpass.getpass('Password: ')
    secret = getpass.getpass('Secret: ')

    return user, password, secret

class QuickDeploy:
    """ quick deploy
    send specified commands over to specified devices """

    def __init__(self):
        # variable initialization
        self.devices = self.read_devices_text_file()
        self.commands = self.read_commands_text_file()
        self.logname = self.ask_user_for_log()
        self.print_screen = self.ask_user_if_print_to_screen()
        self.user, self.password, self.secret = user_credentials_prompt()

        # log data
        self.log = {}

    def ask_user_for_log(self):
        """ ask the user for what the log file will be stored as """

        user_message = "\nPlease enter name for the log file: "
        user_input = input(user_message)

        if user_input.endswith('.txt'):
            return user_input.strip()
        else:
            return user_input.strip() + '.txt'

    def ask_user_if_print_to_screen(self):
        """ ask user if they want to print output to the screen too """

        user_message = "\nPrint to the screen? (y/n) "
        user_input = input(user_message)

        if user_input.lower() == 'y':
            return True
        else:
            return False

    def read_devices_text_file(self):
        """ read devices text file """

        # initialize the resultant datastructure
        devices = {}

        # open the devices text file in read-only mode
        with open('devices.txt', 'r') as fn:

            # iterate through the lines in the text file
            for line in fn.read().splitlines():

                # skip empty lines
                if line is '':
                    continue

                # if comma in line, assume user specified device type
                if ',' in line:
                    # first half is device
                    device = line.split(',')[0].strip()
                    # second half is device type
                    device_type = line.split(',')[1].strip()
                    # build the dictionary as specified
                    devices[device] = device_type

                # otherwise, assume cisco ios as device type
                else:
                    # entire line is device
                    device = line
                    # device type is cisco ios
                    device_type = 'cisco_ios'
                    # build the dictionary as specified
                    devices[device] = device_type

        return devices

    def read_commands_text_file(self):
        """ read commands text file """

        # initialize the resultant datastructure
        commands = []

        # open the commands text file in read-only mode
        with open('commands.txt', 'r') as fn:

            # iterate through the lines in the text file
            for line in fn.read().splitlines():

                # skip empty lines
                if line is '':
                    continue

                commands.append(line)

        return commands

    def display_warning_to_user(self):
        """ display warning to user
        show user the commands + switches and ask if they
        would still like to proceed or not """

        user_message = Fore.CYAN + "\nYou are about to run the following commands:"
        print(user_message)

        for command in self.commands:
            print(command)

        user_message = Fore.CYAN + "\nOn the following devices:"
        print(user_message)

        for device in sorted(self.devices.keys()):
            print(device)

        user_message = Fore.RED + "\nAre you sure you wish to proceed? (y/n) " + Fore.WHITE
        user_input = input(user_message)

        if user_input.lower() == 'y':
            return True
        else:
            return False

    def run_commands(self):
        """ run commands
        main method that runs the specified commands over
        to the specified network devices """

        # iterate through the devices dictionary
        for device, device_type in sorted(self.devices.items()):
            user_message = "\nRunning requested commands on " + device.upper()
            print(Fore.CYAN + user_message + Fore.WHITE)

            # build the appropriate device parameters
            network_device_param = {
                'device_type': device_type,
                'ip': device,
                'username': self.user,
                'password': self.password,
                'secret': self.secret,
            }

            # initialize the connect handler of netmiko
            net_connect = ConnectHandler(**network_device_param)

            # enter enable mode if required
            if net_connect.find_prompt().endswith('>'):
                net_connect.enable()

            # configuration set
            config_set = []
            # flag to check if configuration lines
            config_flag = False

            # iterate through the commands list
            for line in self.commands:
                # check if we need to enter configuration mode or not
                if line.strip().startswith('conf'):
                    config_flag = True
                    continue
                # check if we reached the end of the configuration terminal
                elif line.strip().startswith('end'):
                    config_flag = False
                    # update configuration now and reset the value
                    # this is just in case there are show commands we need to run
                    # after performing the configuration updates
                    net_connect.send_config_set(config_set)
                    if self.print_screen:
                        user_message = Fore.MAGENTA + "\nRUNNING CONFIGURATION:" + Fore.WHITE
                        print(user_message)
                        for line in config_set:
                            print(line)

                    config_set = []
                    continue
                # add line to configuration set if flag is turned up
                elif config_flag:
                    config_set.append(line.strip())
                    continue

                # generate log data structure if key does not exist
                if device not in self.log:
                    self.log[device] = ''

                # otherwise assume a normal show command
                out = net_connect.send_command(line.strip())
                # add to log
                self.log[device] += '\n\n' + device + "# " + line.strip() + "\n"
                self.log[device] += out

                # print the show command output
                if self.print_screen:
                    user_message = Fore.MAGENTA + "\nRUNNING: " + Fore.WHITE + line.strip()
                    print(user_message)
                    print(out)

            # if there were configuration involved, yet not 'end'ed out...
            if config_set:
                # run the configuration now
                net_connect.send_config_set(config_set)

                if self.print_screen:
                    user_message = Fore.MAGENTA + "\nRUNNING CONFIGURATION:" + Fore.WHITE
                    print(user_message)
                    for line in config_set:
                        print(line)

            # close existing ssh session
            net_connect.disconnect()

    def write_log(self):
        """ write log """

        with open(self.logname, 'w') as fn:
            for device, logdata in sorted(self.log.items()):
                # header information
                fn.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
                fn.write(device + "\n")
                fn.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

                # write actual log data
                for line in logdata.splitlines():
                    fn.write(line + '\n')

                fn.write('\n')

def main():
    """ main function to run script """

    # colorama initialization, required for windows
    init(autoreset=True)

    # initialize script
    quick_deploy_introduction()
    qd_script = QuickDeploy()

    # only run script if user is comfortable with suggested updates
    if qd_script.display_warning_to_user():
        qd_script.run_commands()
        qd_script.write_log()

    # pauses the script at the end to state message
    input("\nComplete!")

if __name__ == '__main__':
    main()