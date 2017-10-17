from bokeh.models import FuncTickFormatter
from bokeh.plotting import figure, show, output_file
from ruamel.yaml import YAML
import socket


def graph_bgp(label_dict, redundancy_counts, x_ticks):
    """ graph bgp
    the main graphing function used to graph the given dataset
    we will be graphing this two ways - full and downsampled
    for computers that cannot handle the full graph, please use the downsampled
    data set in order to see the graph without hassle """

    # define output html file
    output_file("bgpgraph.html")

    # define the figure initial parameters
    p = figure(
        title="INTERNET'S REDUNDANCY", # title
        toolbar_location="above",  # toolbar location
        sizing_mode='stretch_both',  # sizing parameters of the graph
        output_backend="webgl", # allows us to utilize webgl to reduce load
        )

    # draw circles with size 1, color navy, and semi transparent for each datapoint
    p.circle(x_ticks, redundancy_counts, size=1, color="navy", alpha=0.5)

    # x axis label
    p.xaxis.axis_label = 'IPv4 Routes'

    # y axis label
    p.yaxis.axis_label = 'AVAILABLE REDUNDANT PATHS'

    # this allows us to replace our x_ticks with real labels - ip routes
    p.xaxis.formatter = FuncTickFormatter(code="""
        var labels = %s;
        return labels[tick];
        """ % label_dict)

    # displays graph on default browser
    show(p)

def load_bgp_database(filename):
    """ load bgp database
    we load our existing bgp information from the yaml file generated from
    our first script here in order to graph that information """

    # initialize our bgp db
    bgp_db = {}

    # load our existing bgp databses
    with open(filename, 'r') as fn:
        yaml=YAML()
        bgp_db = yaml.load(fn)

    return bgp_db

def return_full_bgp_db(bgp_db):
    """ return full bgp db
    parses through the bgp db and returns the three parameters required
    to graph the dataset, unfiltered and unsampled. using this function
    is not recommended and will cause the script to take forever to finish
    running """

    # we need to be able to sort our ip routes properly
    # there is an issue with sorting normally, for example 10.0.0.9 is treated
    # to be greater than 10.0.0.255
    # thankfully, python does allow us to perform custom sorts and the socket
    # library has a wonderful built in sorter for ip addresses. it does not work
    # with subnets (/20, etc) so we need to remove that before sorting

    sorted_bgp_db = sorted(
        bgp_db.items(),
        key=lambda item: socket.inet_aton(item[0].split('/')[0]),
        )

    # initialize our datastructures
    ip_routes = []
    redundancy_counts = []
    x_ticks = []
    label_dict = {}

    # iterate through the sorted bgp db, and store our routes and redundancy
    # counts as a list
    for ip_route, redundancy_count in sorted_bgp_db:
        ip_routes.append(ip_route)
        redundancy_counts.append(redundancy_count)

    # iterate through the ip routes list, and store it as a dictionary with a
    # specific numerical value for graphing and labeling purposes
    for i, s in enumerate(ip_routes):
        # required to label the x axis with the routes
        label_dict[i] = s

        # used to map the x axis with numerical increments 1, 2, 3...
        # this is then replaced with the label information as stored above
        # required as we cannot do custom labels of the x-axis by default
        x_ticks.append(i)

    return label_dict, redundancy_counts, x_ticks

def return_sampled_bgp_db(bgp_db):
    """ return sampled bgp db
    parses through the bgp db and returns the three parameters required
    to graph the dataset, filtered and sampled. """

    # we need to be able to sort our ip routes properly
    # there is an issue with sorting normally, for example 10.0.0.9 is treated
    # to be greater than 10.0.0.255
    # thankfully, python does allow us to perform custom sorts and the socket
    # library has a wonderful built in sorter for ip addresses. it does not work
    # with subnets (/20, etc) so we need to remove that before sorting

    sorted_bgp_db = sorted(
        bgp_db.items(),
        key=lambda item: socket.inet_aton(item[0].split('/')[0]),
        )

    # initialize our datastructures
    ip_routes = []
    redundancy_counts = []
    x_ticks = []
    label_dict = {}

    # sample counter
    sample_count = 0

    # iterate through the sorted bgp db, and store our routes and redundancy
    # counts as a list
    for ip_route, redundancy_count in sorted_bgp_db:
        # every 10th entry will be stored, making the dataset 10x smaller
        if sample_count % 10 == 0:
            ip_routes.append(ip_route)
            redundancy_counts.append(redundancy_count)

        # increment sample counter
        sample_count += 1

    # iterate through the ip routes list, and store it as a dictionary with a
    # specific numerical value for graphing and labeling purposes
    for i, s in enumerate(ip_routes):
        # required to label the x axis with the routes
        label_dict[i] = s

        # used to map the x axis with numerical increments 1, 2, 3...
        # this is then replaced with the label information as stored above
        # required as we cannot do custom labels of the x-axis by default
        x_ticks.append(i)

    return label_dict, redundancy_counts, x_ticks


def main():
    # load bgp database
    bgp_db = load_bgp_database('fullbgpredundancy.yml')

    # run full and unfiltered sampling, not recommended!
    #label_dict, redundancy_counts, x_ticks = return_full_bgp_db(bgp_db)

    # run sampled bgp database
    label_dict, redundancy_counts, x_ticks = return_sampled_bgp_db(bgp_db)

    # graph the information generated
    graph_bgp(label_dict, redundancy_counts, x_ticks)

if __name__ == '__main__':
    main()


