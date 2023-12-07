import matplotlib.pyplot as plt
import matplotlib
import pathlib
import pandas
import numpy

def plot(input_file):
    df = pandas.read_csv(input_file)
    r = df.pivot(columns="pipeline", index="input", values="r_out")
    r_opt = df[["input","r_opt"]].drop_duplicates(ignore_index=True)
    r = pandas.merge(r, r_opt, on="input")
    r["input"] = r["input"].apply(lambda x: pathlib.Path(x).name.split(".")[0])
    r = r.set_index("input")

    x = (r["r_opt"]/r["NONE"]).sort_values().index

    def make_bar(y, name):
        plt.bar(x, y[x], label=name.upper())

    matplotlib.rcParams.update({'font.size': 16})
    #plt.style.use("dark_background")
    plt.figure(figsize=(10, 7))
    plt.xticks(rotation=30)

    ticks = numpy.linspace(0, 1, 11)
    tick_names = [f"{t*100:.0f}%" for t in ticks]
    plt.yticks(ticks, tick_names)

    plt.ylim(bottom=0, top=1)
    make_bar(r["ML"]/r["NONE"], "ML")
    make_bar(r["LEX"]/r["NONE"], "LEX")
    make_bar(r["NN"]/r["NONE"], "NN")
    make_bar(r["r_opt"]/r["NONE"], "OPT")
    plt.ylabel("Compression ratio")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=
        "Plot the final reduction ",
        argument_default=argparse.SUPPRESS)

    parser.add_argument("input", metavar="INPUT", type=str,
        help="Benchmark results (CSV)")

    args = parser.parse_args()
    plot(args.input)
