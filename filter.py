import argparse
def all_valid(fname, foname):
    f = open(fname, "r")
    fo = open(foname, "a")
    line=f.readline();
    while(line and len(line) > 1):
        tk = line.rstrip().split(',')
        b = True
        if(tk[4] == '1' or tk[4] == '5' or tk[4] == '6' or tk[4] == 'None'):
            tk[4] = '1'
        if(tk[4] == '2' or tk[4] == '3' or tk[4] == '4' or tk[4] == '7'):
            tk[4] = '2'
        for i in range(0, len(tk)):
            if(tk[i] == '-1' or tk[i] == '0'):
                b = False
        if (tk[-1][0] >= '0' and tk[-1][0] <= '9') and int(tk[-1]) > 400:
            b = False
        if b:
            fo.write(','.join(tk)+'\n')
        line=f.readline()


def parse_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('in_path', nargs=1)
    parser.add_argument('out_path', nargs=1)
    return parser.parse_args()

def main():
    args = parse_args()
    all_valid(args.in_path[0], args.out_path[0])
    #all_valid("users.csv", "users2.csv")
if __name__ == "__main__":
    main()
