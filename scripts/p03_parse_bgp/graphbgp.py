from bokeh.models import FuncTickFormatter
from bokeh.plotting import figure, show, output_file
from ruamel.yaml import YAML
import socket



output_file("formatter.html")

bgp_db = {}
# save our data as a yaml file to be reused for graping purposes!
with open('fullbgpredundancy.yml', 'r') as fn:
    yaml=YAML()
    bgp_db = yaml.load(fn)


items = sorted(bgp_db.items(), key=lambda item: socket.inet_aton(item[0].split('/')[0]))

ip_routes = []
redundancy_counts = []
x_ticks = []


for ip_route, redundancy_count in items:
    ip_routes.append(ip_route)
    redundancy_counts.append(redundancy_count)

label_dict = {}
for i, s in enumerate(ip_routes):
    label_dict[i] = s
    x_ticks.append(i)


p = figure(plot_width=500, plot_height=500)
p.circle(x_ticks, redundancy_counts)

p.xaxis.formatter = FuncTickFormatter(code="""
    var labels = %s;
    return labels[tick];
""" % label_dict)

show(p)


