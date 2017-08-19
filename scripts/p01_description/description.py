from sshfw import SSHFramework
import time

def main():
    print("Running show ip int brief, time elapse test")
    conn = SSHFramework()
    conn.login('10.0.0.1')

    # start timer
    start = time.time()

    # timer method
    conn.enable_mode_tm()
    conn.no_paging_tm()
    show_ip_int_brief_out = conn.send_command_tm('show ip int brief')
    conn.close_ssh_session()

    # end timer
    end = time.time()

    print("Execution Time For TM: " + str(end-start))

    conn.login('10.0.0.1')

    # start timer
    start = time.time()

    # expect trailing method
    conn.enable_mode_etm()
    conn.no_paging_etm()
    show_ip_int_brief_out = conn.send_command_etm('show ip int brief')
    conn.close_ssh_session()

    # end timer
    end = time.time()

    print("Execution Time For ETM: " + str(end-start))


if __name__ == "__main__":
    main()