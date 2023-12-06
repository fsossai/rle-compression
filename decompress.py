import subprocess
import itertools
import pathlib
import horatio
import pandas
import fslog
import numpy
import json
import time
import sys
import os

@horatio.section()
def extract_columns(input_file):
    command = f"tar -tf {input_file}"
    output = subprocess.check_output(command, shell=True, text=True)
    os.system(f"tar -xf {input_file}")
    extracted = output.strip().split("\n")
    compressed = [x for x in extracted if x.endswith(".bz2")]
    if len(compressed) > 0:
        with horatio.step("decompressing with bzip2"):
            arguments = " ".join(compressed)
            os.system(f"bzip2 --decompress --force {arguments}")

    rle_files = []
    header = None
    for x in extracted:
        if x.endswith(".header"):
            header = x
        elif x.endswith(".header.bz2"):
            header = str(pathlib.Path(x).with_suffix(""))
        elif x.endswith(".bz2"):
            rle_files.append(str(pathlib.Path(x).with_suffix("")))
        elif x.endswith(".rle"):
            rle_files.append(x)

    column_names = pandas.read_csv(header)
    return rle_files, header

def read_file(filename):
    with open(filename, "r") as f:
       lines = f.readlines() 
    return lines

@horatio.section()
def build_dataframe(rle_files, header):
    column_names = pandas.read_csv(header).columns.tolist()
    df = dict()
    for rle_file, name in zip(rle_files, column_names):
        #with horatio.section(f"Run-length decoding {name:20}"):
        data = undo_rle(read_file(rle_file))
        df[name] = data
    
    arguments = " ".join(rle_files + [header])
    os.system(f"rm {arguments}")
    return pandas.DataFrame(df)

@horatio.section()
def save_dataframe(df, output_file):
    df.to_json(output_file, orient="records", lines=True)

def undo_rle(x):
    ty = x[0].strip()
    x = x[1:]
    it1 = iter(x)
    it2 = iter(x)
    next(it2)
    y = []
    for v, c in zip(it1, it2):
        v = v.strip()
        v = json.loads(v)
        y += [v] * int(c)
        next(it1, None)
        next(it2, None)
    y = pandas.Series(y).astype(ty)
    return y

def get_info(input_file, output_file):
    info = dict()
    info["input"] = input_file
    info["output"] = output_file
    info["input_size"] = os.stat(input_file).st_size
    info["output_size"] = os.stat(output_file).st_size
    info["expansion"] = info["output_size"] / info["input_size"]
    return info

def print_info(info):
    input_size = os.stat(info["input"]).st_size
    output_size = os.stat(info["output"]).st_size
    mebi = lambda x: x/(1024**2)
    fslog.log(f"Input file size   : {mebi(input_size):.1f}M")
    fslog.log(f"Output file size  : {mebi(output_size):.1f}M")
    fslog.log(f"Expansion factor  : {info['expansion']:.2f}x")
    fslog.log(f"Elapsed time      : {info['time']:.3f} s")

@horatio.section()
def decompress(input_file, **kwargs):
    default = dict()
    default["input"] = input_file
    default["output"] = str(pathlib.Path(input_file).with_suffix(".json").name)

    default.update(kwargs)
    kwargs.update(default)

    t = time.time()
    rle_files, header = extract_columns(kwargs["input"])
    df = build_dataframe(rle_files, header)
    save_dataframe(df, kwargs["output"])
    t = time.time() - t

    info = get_info(kwargs["input"], kwargs["output"])
    info["time"] = t

    return info
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=
        "Compressor based on minimizing the cost of Run-Length Encoding",
        argument_default=argparse.SUPPRESS)

    parser.add_argument("input", metavar="INPUT", type=str,
        help="Input TAR file to decompress")

    parser.add_argument("-d", "--disable-logs", action="store_true", default=False,
        help="Disable logs on the terminal")

    parser.add_argument("-o", "--output", type=str,
        help="Output file")

    args = parser.parse_args()
    fslog.param["enabled"] = not args.disable_logs
    info = decompress(args.input, **vars(args))
    fslog.log()
    print_info(info)
