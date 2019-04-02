from parser import parser, debug


def inference(nodes, q, es, debug):
    ancestor=[]
    e=[]
    ancestor.append(q)
    evl=[] # list of ancestors
    for k,v in es.items():
        ancestor.append(k)
        e.append(k)
    i=0
    # find all ancestors
    while len(ancestor)!=0:
        curr=ancestor.pop(0)
        if debug:
            print("CURR: ",curr)
        if curr not in evl:
            if debug:
                print("Iter ",i,": ",ancestor)
            evl.append(curr)
            parents=nodes[curr].parent
            if len(parents)!=0:
                for p in parents:
                    if p not in evl: 
                        ancestor.append(p)
            if debug:
                print("ANC: ", ancestor)
                print("EVL: ", evl)
                i+=1


if __name__ == "__main__":
    file=""
    es={}
    print("Input BIF file name w/o extension")
    file=str(input())
    nodes=parser(file)
    debug(nodes)
    print("Input query variable")
    q=str(input())
    print("Input evidence (e.g. X=false), type # when finished")
    e=str(input())
    print("evidence: ",e)
    while e.count('#')==0:
        a=e.split('=')
        if(a[1] in nodes[a[0]].classes):
            es[a[0].strip()]=a[1].strip()
            print("0:",a[0].strip(), ", 1:",a[1].strip())
        else:
            print("Error, available values:", nodes[a[0]].classes)
        e=str(input())
    inference(nodes,q,es,True)