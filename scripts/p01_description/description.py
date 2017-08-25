"""
description modifier script
related article: The Cautionary Tale Of Paramiko
author: syedur rahman (risedfo)
"""

# import our custom paramiko library
from sshfw import *

# import over the time library to keep track of execution time
import time

def parse_show_ip_int_brief(conn, router):
    """ parse show ip int brief
    this will contain the logic that we need to go through the
    'show ip int brief' output and figure out which ports are admin up
    yet link-down. using this information we will have a list of ports
    that we can later iterate through to find any existing descriptions and
    eventually shutdown """

    # useful CLI message to send so that we can keep
    # track of what's going on currently in the script
    print("ROUTER " + router + ": RUNNING 'SHOW IP INT BRIEF'")

    # collect the show ip int brief output
    command = 'show ip int brief'
    show_ip_int_brief_output = conn.send_command(command)

    # initialize the down port list
    down_port_list = []

    # iterate through each line one at a time
    for line in show_ip_int_brief_output.splitlines():
        # find any lines that contains "up" as in admin-up
        if 'up' in line.lower():
            # within those lines, find if they also contain "down" as in link-down
            if 'down' in line.lower():
                # these are our admin "up" yet link-down ports
                # we will take the first word of this line as our port
                # and append it to our existing down port list
                down_port_list.append(line.split()[0])

    return down_port_list

def parse_show_interface(conn, router, down_port_list):
    """ parse show interface
    this will contain the logic that we need in order to find the descriptions
    for every down port we added to our list. we need to first iterate
    through the down port list and launch 'show interface x/x' to collect
    the right information. this will generate a useful dictionary for us

    input -> down_port_list = [downport1, downport2, ...]
    output -> description_dictionary = {downport1 : description1, downport2...}
    """

    # initialize our new dictionary
    description_dictionary = {}

    # now iterate through the newly generated down port list
    for down_port in down_port_list:
        # further initialize our dictionary using down port as key
        description_dictionary[down_port] = ''

        # initialize the exact command string to send to switch
        command = 'show interface ' + down_port

        # useful CLI message to send so that we can keep
        # track of what's going on currently in the script
        print("ROUTER " + router + ": RUNNING '" + command.upper() + "'")

        # run show interface x/x to collect the exact description we need
        show_interface_output = conn.send_command(command)

        # check if description in the output at all
        if 'Description:' in show_interface_output:
            # iterate through output to find the exact description location
            # and then replace the empty description in our dictionary
            for line in show_interface_output.splitlines():
                # once the exact line with the description has been located...
                if 'Description:' in line:
                    # proceed to replace the existing empty description
                    # within our dictionary, note how this is being split
                    # is based off our expected command output
                    # "Description: host" <- expected line
                    description = line.split(':')[1]
                    description_dictionary[down_port] = description

    return description_dictionary

def configure_interfaces(conn, router, description_dictionary):
    """ configure interfaces
    enter into 'config t' mode and actually start the configuration of our
    interfaces based off the newly created description dictionary. our goal
    is to make sure to append existing descriptions with our message and also
    shutting down each description as well per our requirements """

    # our message that we need to append to our descriptions
    append = '(audit item - admin down 2017)'

    # enter into configuration terminal
    conn.send_command('config t')

    # iterate through our existing description dictionary
    for down_port, description in sorted(description_dictionary.items()):
        # useful CLI message to send so that we can keep
        # track of what's going on currently in the script
        print("ROUTER " + router + ": CONFIGURING " + down_port.upper())

        # checks if there is an existing description or not
        if description:
            # if there is, then it appends our message to the end of it
            description = description + ' ' + append
        # otherwise we can use the append as the whole description
        else:
            # otherwise we can replace the entire description with our message
            description = append

        # these are our conf t commands to configure the interface
        conn.send_command('interface ' + down_port)
        conn.send_command('desc ' + description)
        conn.send_command('shutdown')

    # end out of configuration terminal after updates have been made
    conn.send_command('end')

def description_script(routers):
    """ simple test function to see execution time """

    # pick and choose which conceptual idea to run by uncommenting
    conn = SSHTimerMethod()
    #conn = SSHTrailingMethod()

    # start timer to measure elapsed time
    start_timer = time.time()

    # log into each router by iterating list
    for router in routers:
        # log into specified router
        conn.login(router)

        # enter into enable mode
        conn.enable_mode()

        # run term len 0 to prevent paging
        conn.no_paging()

        # launch our parser function for show ip int brief output and
        # generate our down port list as a direct result
        down_port_list = parse_show_ip_int_brief(conn, router)

        # launch our parser function for show interface output and
        # generate our description dictionary as a direct result
        description_dictionary = parse_show_interface(conn, router, down_port_list)

        # launch our configuration function
        configure_interfaces(conn, router, description_dictionary)

        # close the entire session to that switch
        conn.close_ssh_session()

    # end timer
    end_timer = time.time()

    print("\nExecution Time: " + str(end_timer-start_timer))

def main():
    # set up a list for all routers we need to log into
    routers = ['10.0.0.1', '10.2.0.1', '10.3.0.1']

    # run the main logic of our script
    description_script(routers)

if __name__ == "__main__":
    main()