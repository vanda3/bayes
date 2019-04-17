from parser import parser, debug, queryParser


def core(nodes, q, e, flag, debug):
    if(nodes[q].isRoot()):
        print(nodes[q].probs["[]"])


if __name__ == "__main__":
    file=""
    es={}
    print("Input BIF file name w/o extension")
    file=str(input())
    nodes, names=parser(file)
    debug(nodes)
    print("Available Variables: ",names)
    print("Pr? ",end='')
    query=str(input())
    q, e, flag = queryParser(query)
    f=0
    while True:
        if q not in names:
            print("Error, ",q, " not available.")
            f=1
        else:
            for ev in e:
                if ev not in names:
                    print("Error, ",ev, " not available.")
                    f=1
        if f==1:      
            print("Available variables: ", names)
            print("Try again. Pr? ",end='')
            query=str(input())
            q, e, flag = queryParser(query)
        else:
            break
        f=0
    core(nodes,q,e,flag,True)