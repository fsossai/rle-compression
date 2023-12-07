import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from scipy.stats import gmean
import matplotlib
import pathlib
import pandas
import numpy

def plot(input_file):
    df = pandas.read_csv(input_file)
    r = df.pivot(columns="pipeline", index="input", values="r_out")
    get_name = lambda x: pathlib.Path(x).name.split(".")[0]
    r.index = list(map(get_name, r.index))

    methods = ["LEX+VNS", "ML+VNS", "NN+VNS"]
    lex = r.div(r["LEX"], axis=0)
    print("Run counts reduction over LEX (geomean):")
    for m in methods:
        rcr = gmean(lex[m]) - 1
        print("{:10}{:.2f} %".format(m, rcr*100))

    r.columns.name = ""
    #matplotlib.rcParams.update({'font.size': 16})
    #plt.style.use("dark_background")
    (lex[methods] - 1).plot.bar()
    plt.xticks(rotation=30)
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.ylabel("Run count reduction (over LEX)")
    plt.show()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=
        "Plot the improvements over LEX given a benchmark result",
        argument_default=argparse.SUPPRESS)

    parser.add_argument("input", metavar="INPUT", type=str,
        help="Benchmark results (CSV)")

    args = parser.parse_args()
    plot(args.input)

