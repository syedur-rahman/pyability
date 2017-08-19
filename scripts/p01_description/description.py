from sshfw import *
import time

def execution_test(conn):
    """ simple test function to see execution time """

    # start timer
    start = time.time()

    # general method flow
    conn.login('10.0.0.1')
    conn.enable_mode()
    conn.no_paging()
    show_ip_int_brief_out = conn.send_command('show ip int brief')
    print("COLLECTING ALL CONNECTED PORTS FROM SHOW IP INT BRIEF:")
    for line in show_ip_int_brief_out.splitlines():
        if 'up' in line.lower():
            if 'down' not in line.lower():
                print(line)
    conn.close_ssh_session()

    # end timer
    end = time.time()

    print("\nExecution Time: " + str(end-start))

def main():
    print("TEST - ELAPSED TIME")
    print("\nSSH TIMER METHOD!")
    conn = SSHTimerMethod()
    execution_test(conn)

    print("\nSSH TRAILING METHOD!")
    conn = SSHTrailingMethod()
    execution_test(conn)

if __name__ == "__main__":
    main()