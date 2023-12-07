import matplotlib.pyplot as plt
import pathlib
import pandas
import numpy
import sys

# For scientific references see:
#
# Dolan E.D., Moŕe J.J.
# 2002
# Benchmarking Optimization Software with Performance Profiles.
# Mathematical Programming 91(2):201–213
# https://link.springer.com/article/10.1007/s101070100263

def set_defaults(kwargs):
    defaults = dict()
    defaults["problem_type"] = "min"
    defaults["xlimit"] = 10
    defaults["save"] = False
    defaults["reverse"] = False
    defaults["marker"] = "."
    defaults["marker_size"] = 10
    defaults["title"] = "Performance Profile"
    defaults["xlabel"] = "Ratio to best"
    defaults["ylabel"] = "How many"
    defaults.update(kwargs)
    kwargs.update(defaults)

def plot_dataframe(df, **kwargs):
    set_defaults(kwargs)

    fig, axs = plt.subplots(1)
    if kwargs["problem_type"] == "min":
        get_best = pandas.DataFrame.min
    else:
        get_best = pandas.DataFrame.max

    best = get_best(df, axis=1)

    N = len(df)
    y = numpy.linspace(0.0, 1.0, N+1)[1:]

    if "letters" in kwargs:
        if kwargs["letters"] != "":
            if len(kwargs["letters"]) < len(df.columns):
                print("ERROR: not enough letters specified")
                sys.exit(1)

    for i, method in enumerate(df.columns):
        vals = df[method]
        marker = kwargs["marker"]
        if "letters" in kwargs:
            if kwargs["letters"] == "":
                marker = r"${}$".format(chr(ord("A")+i))
            else:
                marker = r"${}$".format(kwargs["letters"][i])
        x = (vals / best).sort_values()
        x = 1 / x if kwargs["reverse"] else x
        plt.step(x, y, where="post", label=method,
                 marker=marker, markersize=kwargs["marker_size"])

    fig.suptitle(kwargs["title"])
    plt.xlabel(kwargs["xlabel"])
    plt.ylabel(kwargs["ylabel"])
    ticks = numpy.linspace(0, 1, 11)
    tick_names = [f"{t*100:.0f}%" for t in ticks]

    plt.yticks(ticks, tick_names)
    if not kwargs["reverse"]:
        right = min(plt.xlim()[1], kwargs["xlimit"])
        plt.xlim(left=1)
    plt.grid(True, linewidth=0.1)

    if kwargs["problem_type"] == "min":
        if kwargs["reverse"]:
            plt.legend(loc="lower left")
        else:
            plt.legend(loc="lower right")
    else:
        if kwargs["reverse"]:
            plt.legend(loc="upper right")
        else:
            plt.legend(loc="upper left")

    if "output" in kwargs:
        plt.savefig(kwargs["output"])
    elif kwargs["save"]:
        plt.savefig(str(pathlib.Path(kwargs["input"]).with_suffix(".pdf")))
    else:
        plt.show()

def extract_data(input_file):
    df = pandas.read_csv(input_file)
    r_opt = df[["input","r_opt"]].drop_duplicates(ignore_index=True)
    pp = df.pivot(columns="pipeline", index="input", values="r_out")
    pp = pandas.merge(pp, r_opt, on="input")
    pp = pp.rename(columns={"r_opt":"OPT"})
    which = []
    if "LEX+VNS" in pp.columns:
        which.append("LEX+VNS")
    else:
        which.append("LEX")
    if "NN+VNS" in pp.columns:
        which.append("NN+VNS")
    else:
        which.append("NN")
    if "ML+VNS" in pp.columns:
        which.append("ML+VNS")
    else:
        which.append("ML")
    pp = pp[which]
    return pp
     
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=
        "Plot an overall comparison of methods given a benchmark result",
        argument_default=argparse.SUPPRESS)

    parser.add_argument("input", metavar="INPUT", type=str,
        help="Benchmark results (CSV)")

    args = parser.parse_args()

    df = extract_data(args.input)
    plot_dataframe(df, xlimit=3)
