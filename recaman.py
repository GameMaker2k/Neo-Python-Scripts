import sys

""" Recamán sequence with limit :P """
def seqtest(limit: int) -> list[int]:
    """ Generate the sequence up to a non-negative integer limit. """
    limit = int(abs(limit))
    x = 0
    xt = 1
    seqlist = [0]
    while True:
        if((x - xt)>0 and (x - xt) not in seqlist):
            x -= xt
        else:
            x += xt
        if x > limit:
            break
        xt += 1
        seqlist.append(x)
    return seqlist

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            print("Please provide an integer limit, e.g.: python recaman.py 10000")
            sys.exit(1)
        print(seqtest(limit))
    else:
        print("Usage: python recaman.py <limit>")
