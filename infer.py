from parser import parser, debug, queryParser


def inference(nodes, q, e, debug):
    ancestor=[]
    e=[]


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
    q, e = queryParser(query)
    flag=2
    while flag!=0:
        if q not in names:
            print("Error, ",q, " not available.")
            flag=1
        for ev in e:
            if ev not in names:
                print("Error, ",ev, " not available.")
                flag=1
        if flag==1:      
            print("Available variables: ", names)
            print("Try again.")
            query=str(input)
            q, e = queryParser(query)
        else:
            flag=0
        flag=2
    #inference(nodes,q,e,True)