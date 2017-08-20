from sshfw import *
import time

def description_script(routers):
    """ simple test function to see execution time """

    # pick and choose which conceptual idea to run by uncommenting
    conn = SSHTimerMethod()
    #conn = SSHTrailingMethod()

    # start timer to measure elapsed time
    start = time.time()

    append = '(audit item - admin down 2017)' # the description we need to append

    # log into each router by iterating list
    for router in routers:
        # initialize the two datastructures that we will need
        down_port_list = [] # list of all down ports
        description_dictionary = {} # key will be port, value being description

        # log into specified router
        conn.login(router)

        # enter into enable mode
        conn.enable_mode()

        # run term len 0 to prevent paging
        conn.no_paging()

        # collect the show ip int brief output
        command = 'show ip int brief'
        show_ip_int_brief_output = conn.send_command(command)
        print("ROUTER " + router + ": RUNNING 'SHOW IP INT BRIEF'")

        # iterate through each line one at a time
        for line in show_ip_int_brief_output.splitlines():
            # find any lines that contains "up"
            if 'up' in line.lower():
                # within those lines, find if they also contain "down"
                if 'down' in line.lower():
                    # these are our admin "up" yet link-down ports
                    # append the first word in this line as that contains
                    # the down interface information that we will need
                    down_port_list.append(line.split()[0])

        # now iterate through the newly generated down port list
        for down_port in down_port_list:
            # further initialize our dictionary using down port as key
            description_dictionary[down_port] = ''

            # run show interface x/x to collect the exact description we need
            command = 'show interface ' + down_port
            show_interface_output = conn.send_command(command)
            print("ROUTER " + router + ": RUNNING '" + command.upper() + "'")

            # check if description in the output at all
            if 'Description:' in show_interface_output:
                # iterate through output to find the exact description
                # and then replace the empty description in our dictionary
                # with the real one
                for line in show_interface_output.splitlines():
                    if 'Description:' in line:
                        # collect the exact description by
                        # splitting on ':'
                        description = line.split(':')[1]
                        description_dictionary[down_port] = description

        # enter into configuration terminal
        conn.send_command('config t')

        for down_port, description in sorted(description_dictionary.items()):
            print("ROUTER " + router + ": CONFIGURING " + down_port)
            # if the down port had an existing description, append to it
            if description:
                description = description + ' ' + append
            # otherwise we can use the append as the whole description
            else:
                description = append

            conn.send_command('interface ' + down_port)
            conn.send_command('desc ' + description)
            conn.send_command('shutdown')

        # end out of configuration terminal after updates have been made
        conn.send_command('end')

        # close the entire session to that switch
        conn.close_ssh_session()

    # end timer
    end = time.time()

    print("\nExecution Time: " + str(end-start))

def main():
    # set up a list for all routers we need to log into
    routers = ['10.0.0.1', '10.2.0.1', '10.3.0.1']

    # run the main logic of our script
    description_script(routers)

if __name__ == "__main__":
    main()