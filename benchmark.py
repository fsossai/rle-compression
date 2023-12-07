import compress
import datetime
import horatio
import pandas
import time
import sys
import os

now = datetime.datetime.now()
date = now.strftime("%y%m%d-%H%M%S")
default_prefix = f"bm_{date}"

def recover(temp_file):
    results = pandas.read_json(temp_file, lines=True)
    return results

@horatio.section()
def benchmark(input_files, time_limit, prefix=None):
    temp_file = f".{default_prefix}.json"
    print(f"Temporary file: {temp_file}")
    pipelines = [
        ["none"],
        ["lex"],
        ["nn"],
        ["ml"],
        ["none", "vns"],
        ["lex", "vns"],
        ["nn", "vns"],
        ["ml", "vns"]
    ]
    args = dict()
    args["bzip"] = False
    args["time_limit"] = time_limit
    args["shuffle"] = True
    for p in pipelines:
        for file in input_files:
            args["pipeline"] = p
            res = compress.compress(file, **args)
            with open(temp_file, "a") as f:
                df = pandas.DataFrame(res, index=[0])
                json = df.to_json(None, orient="records", lines=True)
                f.write(json.strip())
                f.write("\n")

    results = recover(temp_file)
    prefix = prefix or default_prefix
    output_file = f"{prefix}.csv"
    results.to_csv(output_file, index=False, float_format="%.4f")
    os.system(f"rm {temp_file}")
    return results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=
        "Benchmarking tool for the RLE-based compressor",
        argument_default=argparse.SUPPRESS)

    parser.add_argument("input_files", metavar="INPUT_FILES", nargs="+", type=str,
        help="All databases to benchmark on. Supported formats: JSON, CSV")

    parser.add_argument("-p", "--prefix", type=str,
        help="Will be used as a prefix for the output files")

    parser.add_argument("-t", "--time-limit", type=float, default=60,
        help="Heuristic time limit [seconds]. Default is 60")

    args = parser.parse_args()

    r = benchmark(**vars(args))
    
