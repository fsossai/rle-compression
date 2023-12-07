import matplotlib.pyplot as plt
import matplotlib
import pathlib
import pandas

def plot(input_file):
    df = pandas.read_csv(input_file)
    r = df.pivot(columns="pipeline", index="input", values="time")
    get_name = lambda x: pathlib.Path(x).name.split(".")[0]
    r.index = list(map(get_name, r.index))
    r.columns.name = ""

    methods = ["LEX","NN","ML"]

    matplotlib.rcParams.update({'font.size': 16})
    #plt.style.use("dark_background")
    r[methods].plot.bar()
    plt.xticks(rotation=30)
    plt.ylabel("Execution time [s]")
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
