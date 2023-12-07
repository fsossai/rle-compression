import pandas
import numpy
import datetime

now = datetime.datetime.now()
date = now.strftime("%y%m%d%H%M%S")

def generate(rows, columns, ratio=100, output=None):
    N = rows
    M = columns
    L = N
    c = numpy.power(1/ratio, 1/M)
    A = numpy.random.rand(M, N)
    A *= N
    A = A.astype("int")

    for i in range(M):
        L = int(L * c)
        A[i,:] %= L

    df = pandas.DataFrame(A.T)
    print("Unique values per column:")
    print(df.nunique().sort_values(ascending=False))

    output = output or f"db_N{N}_M{M}_R{int(ratio)}_{date}.csv"
    df.to_csv(output)
    print(f"Saved to {output}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=
        "Random database generator. Unique values "
        "descrease exponentially along columns",
        argument_default=argparse.SUPPRESS)

    parser.add_argument("-N", "--rows", type=int, required=True,
        help="Number of rows")

    parser.add_argument("-M", "--columns", type=int, required=True,
        help="Number of columns")

    parser.add_argument("-R", "--ratio", type=float, default=100.0,
        help="Desired ratio between the column with the most values "
             "and the one with the least")

    parser.add_argument("-o", "--output", type=str,
        help="Output file")

    args = parser.parse_args()

    generate(**vars(args))


