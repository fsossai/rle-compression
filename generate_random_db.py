import pandas
import numpy
import datetime

now = datetime.datetime.now()
date = now.strftime("%y%m%d-%H%M%S")

def generate(rows, columns, ratio=100, output=None):
    L = rows
    c = numpy.power(1/ratio, 1/columns)
    A = numpy.random.rand(columns, rows)
    A *= rows
    A = A.astype("int")

    for i in range(columns):
        L = int(L * c)
        A[i,:] %= L

    df = pandas.DataFrame(A.T)
    print("Unique values per column:")
    print(df.nunique().sort_values(ascending=False))

    output = output or f"db_{rows}x{columns}_{date}.csv"
    df.to_csv(output)
    print(f"Saved to {output}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=
        "Random database generator. Unique values "
        "descrease exponentially along columns",
        argument_default=argparse.SUPPRESS)

    parser.add_argument("-n", "--rows", type=int, required=True,
        help="Number of rows")

    parser.add_argument("-m", "--columns", type=int, required=True,
        help="Number of columns")

    parser.add_argument("-r", "--ratio", type=float, default=100.0,
        help="Desired ratio between the column with the most values "
             "and the one with the least")

    parser.add_argument("-o", "--output", type=str,
        help="Output file")

    args = parser.parse_args()

    #generate(args.rows, args.columns, args.ratio)
    generate(**vars(args))


