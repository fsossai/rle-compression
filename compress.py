import subprocess
import itertools
import horatio
import pathlib
import pandas
import fslog
import numpy
import json
import time
import sys
import os

def count_runs(column):
    gb = itertools.groupby(column.values)
    l = len(list(gb))
    return l

def count_total_runs(df):
    r = 0
    for col in df.columns:
        r += count_runs(df[col])
    return r

def rle(column):
    gb = itertools.groupby(column.values)
    rl = [(v, len(list(r))) for v, r in gb]
    return rl
    
def export_column(dbname, column):
    filename = column.name

    for p in " ()<>,.~!@#$%^&*()=:;'\"[]{}":
        filename = filename.replace(p, "_")

    filename = f"{dbname}.{filename}.rle"
    column = column.apply(json.dumps)
    with open(filename, "w") as f:
        f.write(str(column.dtype))
        f.write("\n")
        for v, c in rle(column):
            f.write(f"{v}\n{c}\n")
    return filename

def export_header(df, dbname):
    output = f"{dbname}.header"
    with open(output, "w") as f:
        c_names = df.columns.tolist()
        c_names = [json.dumps(c) for c in c_names]
        header = ",".join(c_names)
        f.write(header)
    return output

@horatio.step()
def factorize(df):
    fdf = df.copy()
    for col in df.columns:
        codes, _ = df[col].factorize()
        fdf[col] = codes

    return fdf

@horatio.step()
def parse(input_file):
    ext = pathlib.Path(input_file).suffix
    if ext == ".json":
        df = pandas.read_json(input_file, lines=True, convert_dates=False)
    elif ext == ".csv":
        df = pandas.read_csv(input_file, encoding="utf-8", engine="python")
    else:
        fslog.log(f"ERROR: '{ext}' format not supported")
        sys.exit(1)
    return df

@horatio.section()
def reorder_rand(df):
    return df.sample(frac=1, random_state=1) # shuffling

@horatio.section()
def reorder_lex(df):
    order = df.nunique(dropna=False).sort_values().index.to_list()
    rdf = df.sort_values(by=order)
    return rdf

@horatio.section()
def reorder_nn(df):
    mktemp = subprocess.run("mktemp", stdout=subprocess.PIPE, text=True)
    fact_file = mktemp.stdout.strip()
    output = f"{fact_file}.path"

    fdf = factorize(df)
    fdf.to_csv(fact_file, header=False, index=False, sep="\t")
    os.system(f"./nn.out {fact_file} {output}")
    order = numpy.loadtxt(output).astype("int32")
    rdf = df.iloc[order]
    return rdf

@horatio.section()
def reorder_vns(df, time_limit):
    mktemp = subprocess.run("mktemp", stdout=subprocess.PIPE, text=True)
    fact_file = mktemp.stdout.strip()
    output = f"{fact_file}.path"

    fdf = factorize(df)
    fdf.to_csv(fact_file, header=False, index=False, sep="\t")
    os.system(f"./vns.out {fact_file} {output} {time_limit}")
    order = numpy.loadtxt(output).astype("int32")
    rdf = df.iloc[order]
    return rdf

@horatio.section()
def build_lists(df, output_file):
    order = df.nunique(dropna=False).sort_values().index.to_list()
    rdf = df.sort_values(by=order)
    ldf = pandas.DataFrame()
    for col in df.columns:
        ldf[col] = rdf.sort_values(by=[col]).index
    ldf.T.to_csv(output_file, header=False, index=False, sep="\t")
    return ldf

@horatio.section()
def reorder_ml(df):
    mktemp = subprocess.run("mktemp", stdout=subprocess.PIPE, text=True)
    temp_file = mktemp.stdout.strip()
    fact_file = f"{temp_file}.fact"
    lists_file = f"{temp_file}.lists"
    output = f"{temp_file}.path"

    fdf = factorize(df)
    fdf.to_csv(fact_file, header=False, index=False, sep="\t")
    ldf = build_lists(df, lists_file)

    os.system(f"./ml.out {fact_file} {lists_file} {output}")
    order = numpy.loadtxt(output).astype("int32")
    rdf = df.iloc[order]
    return rdf

@horatio.section()
def export_dataframe(df, dbname):
    outputs = []
    for c in df:
        col = df[c]
        fout = export_column(dbname, col)
        outputs.append(fout)
    header = export_header(df, dbname)
    outputs.append(header)
    return outputs

@horatio.section()
def create_archive(df, output_file, **kwargs):
    default = dict()
    default["leave_columns"] = False
    default["bzip2"] = False
    default.update(kwargs)
    kwargs.update(default)

    tasks = []
    dbname = pathlib.Path(output_file).with_suffix("").name
    column_files = export_dataframe(df, dbname)
    if kwargs["bzip2"]:
        commands = [f"bzip2 -9 {fin}" for fin in column_files]
        column_files = [f + ".bz2" for f in column_files]
        parallel_command = " & ".join(commands) + "; wait"
        os.system(parallel_command)

    arguments = " ".join(column_files)
    os.system(f"tar -cf {output_file} {arguments}")
    if not kwargs["leave_columns"]:
        os.system(f"rm {arguments}")

@horatio.section()
def run_pipeline(pipeline, df, time_limit):
    for p in pipeline:
        p = p.lower()
        if p == "none":
            pass
        elif p == "rand":
            df = reorder_rand(df)
        elif p == "lex":
            df = reorder_lex(df)
        elif p == "nn":
            df = reorder_nn(df)
        elif p == "ml":
            df = reorder_ml(df)
        elif p == "vns":
            df = reorder_vns(df, time_limit)
        else:
            fslog.log(f"ERROR: heuristic '{p}' doesn't exist")
            sys.exit(1)
    return df

def get_info(input_file, output_file, dfi, dfo):
    info = dict()
    info["input"] = input_file
    info["nrows"] = len(dfi)
    info["r_in"] = count_total_runs(dfi)
    info["r_best"] = dfi.nunique(dropna=False).sum()
    info["r_ref"] = count_total_runs(reorder_lex(dfi))
    info["r_out"] = count_total_runs(dfo)
    info["input_size"] = os.stat(input_file).st_size
    info["output_size"] = os.stat(output_file).st_size
    info["c_ratio"] = info["output_size"] / info["input_size"] * 100
    return info

def print_info(info):
    r_in, r_out = info["r_in"], info["r_out"]
    r_ref, r_best = info["r_ref"], info["r_best"]
    mega = lambda x: x/(1000**2)
    mebi = lambda x: x/(1024**2)
    kilo = lambda x: x/1000

    fslog.open("Summary")
    fslog.log(f"Input file name               : {info['input']}")
    fslog.log(f"Output file name              : {info['output']}")
    fslog.log(f"Input file size               : {mebi(info['input_size']):.1f}M")
    fslog.log(f"Output file size              : {mebi(info['output_size']):.1f}M")
    fslog.log(f"Number of rows                : {kilo(info['nrows']):.0f}K")
    fslog.log(f"Pipeline                      : {info['pipeline']}")
    fslog.log(f"Input runs                    : {r_in}")
    fslog.log(f"Output runs                   : {r_out}")
    fslog.log(f"Ref runs                      : {r_ref}")
    fslog.log(f"Best runs                     : {r_best}")
    fslog.log(f"Improvement (over input)      : {r_in/r_out:.4}x")
    fslog.log(f"Improvement (over ref)        : {r_ref/r_out:.4}x")
    fslog.log(f"Improvement (upper bound)     : {r_ref/r_best:.4}x")
    fslog.log(f"Compression ratio             : {info['c_ratio']:.2f}%")
    fslog.log(f"Compression time              : {info['time']:.3f} s")
    fslog.close()

@horatio.section()
def compress(input_file, **kwargs):
    default = dict()
    default["input"] = input_file
    default["output"] = str(pathlib.Path(input_file).with_suffix(".tar").name)
    default["bzip2"] = False
    default["time_limit"] = 60
    default["leave_columns"] = False
    default["pipeline"] = ["none"]
    default["shuffle"] = False

    default.update(kwargs)
    kwargs.update(default)

    dfi = parse(kwargs["input"])

    if kwargs["shuffle"]:
        dfo = dfi.sample(frac=1, random_state=1) # shuffling
    else:
        dfo = dfi

    t = time.time()
    dfo = run_pipeline(kwargs["pipeline"], dfo, kwargs["time_limit"])
    t = time.time() - t

    create_archive(dfo, kwargs["output"], **kwargs)

    info = get_info(kwargs["input"], kwargs["output"], dfi, dfo)
    info["bzip2"] = kwargs["bzip2"]
    info["output"] = kwargs["output"]
    info["time"] = t
    info["pipeline"] = "+".join(kwargs["pipeline"]).upper()

    return info
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=
        "Compressor based on minimizing the cost of Run-Length Encoding",
        argument_default=argparse.SUPPRESS)

    parser.add_argument("input", metavar="INPUT", type=str,
        help="Input file to compress. Supported formats: JSON")

    parser.add_argument("-o", "--output", type=str,
        help="Output file")

    parser.add_argument("-y", "--leave-columns", action="store_true", default=False,
        help="Don't delete column files after compression")

    parser.add_argument("-s", "--shuffle", action="store_true", default=False,
        help="Shuffle the dataset before running the pipeline")

    parser.add_argument("-d", "--disable-logs", action="store_true", default=False,
        help="Disable logs on the terminal")

    parser.add_argument("-b", "--bzip2", action="store_true", default=False,
        help="Use bzip2 on RLE columnar files before creating the archive")

    parser.add_argument("-t", "--time-limit", type=float, default=60,
        help="Heuristic time limit [seconds]. Default is 60")

    parser.add_argument("-p", "--pipeline", nargs='+', default=["none"],
        choices=["none","lex","rand","ml","nn","vns"],
        help="Pipeline of heuristics to run sequentially. Default is 'none'")
    args = parser.parse_args()
    logs = not args.disable_logs
    info = compress(args.input, **vars(args))
    fslog.log()
    print_info(info)

