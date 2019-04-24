from parser import parser, debug, queryParser, dict_to_tuple, tuple_to_dict
from copy import deepcopy
from ast import literal_eval
import time

space=0
deb=True

# Core Algorithm
def core(nodes, names, q, e):
    global space
    space=0
    start = time.time()
    result = init_factors(nodes, q, e, 1)
    end= time.time()
    print("\nTop-Down strategy:\n",result)
    print("Time elapsed=",end-start," Space used=",space)
    print("--------------------------------------------------")
    space=0
    start2 = time.time()
    result2 = init_factors(nodes, q, e, 2)
    end2= time.time()
    print("\nBottom-Up strategy:\n",result2)
    print("Time elapsed =",end2-start2," Space used=",space)
    print("--------------------------------------------------")
    space=0
    start3 = time.time()
    result3 = init_factors(nodes, q, e, 3)
    end3= time.time()
    print("\nMost Cardinal strategy:\n",result3)
    print("Time elapsed =",end3-start3," Space used=",space)
    print("--------------------------------------------------")


def gen_perms(vars,nodes):
    """
    Generates all possible permutations of the given variables
    :param vars:        The variables to permutate
    :return:            A list of tuples ([vars], [values_of_vars])
    """
    # For all possible values of all vars, create a permutation and add it to the list
    perms = []

    for var in vars:
        if len(perms) == 0:
            for value in nodes[var].classes:
                perms.append({var: value})
        else:
            classes = nodes[var].classes
            old_perms = perms
            for i in range(1, len(classes)):
                perms = perms + deepcopy(old_perms)

            for i in range(0, int(len(perms) / len(classes))):
                for j in range(0, len(classes)):
                    perms[i + j * int(len(perms) / len(classes))][var] = classes[j]

    perm_tuples = []
    for dictionary in perms:
        tup = dict_to_tuple(dictionary)
        perm_tuples.append(tup)

    return perm_tuples


def process_query(nodes, var, perm):
    """
    Gets the probability for the permutation
    :param nodes:   The network
    :param var:     The variable we query
    :param perm:    The permutation in question in form ([vars],[vars_values])
    :return:        The probability of the permutation
    """

    # The variable has no parents. Just return the probability it has set for that evidence value.
    if nodes[var].isRoot():
        return nodes[var].probs['{}'][0]
    # The variable has parents. Query its probability
    else:
        return nodes[var].getProbability(perm)      # Get the probability

# Generates valid permutations of values for factors
def make_factor(nodes, var, factor_vars, e):
    global space
    space+=1
    factor_vars.sort()

    all_vars = deepcopy(nodes[var].parent)
    all_vars.append(var)

    perms = gen_perms(all_vars,nodes)

    # Filter out permutations not in accord with the evidence
    perms = filter_perms(perms, e)

    # Calculate probabilities for each permutation
    probabilities = {}
    for perm in perms:
        prob = process_query(nodes, var, perm)
        probabilities[perm] = prob
        
    return factor_vars, probabilities

# Removes unecessary values from table
def filter_perms(perms, e):
    old_perms = deepcopy(perms)
    for perm in old_perms:
        for key, value in e.items():
            lst_vars = literal_eval(perm[0])
            lst_values = literal_eval(perm[1])
            for i, _ in enumerate(lst_vars):
                if perm in perms and (lst_vars[i] == key) & (lst_values[i] != value):
                    # Remove the permutations that don't match the evidence
                    perms.remove(perm)

    return perms


def product(nodes, factorA, factorB, e):
    global space
    space+=1
    vars = []
    vars.extend(factorA[0])
    vars.extend(factorB[0])
    for key in e.keys():
        vars.append(key)

    # Eliminate repeated variables
    vars = list(set(vars))
    perms = gen_perms(vars,nodes)

    # Remove the perms that don't match the evidence
    perms = filter_perms(perms, e)

    probabilities = {}
    for perm in perms:
        perm_dict = tuple_to_dict(perm)
        prob1 = 0
        prob2 = 0

        # Get the probability of the permutation on factorA
        used_varsA = factorA[0]
        used_perm_dictA = deepcopy(perm_dict)
        if len(used_varsA) != len(perm_dict):
            for v in perm_dict.keys():
                if v not in used_varsA:
                    used_perm_dictA.pop(v)
        for tup, prob in factorA[1].items():
            dit = tuple_to_dict(tup)

            if all(key in dit and dit[key] == val for key, val in used_perm_dictA.items()):
                prob1 = prob

        used_varsB = factorB[0]
        used_perm_dictB = deepcopy(perm_dict)
        if len(used_varsB) != len(perm_dict):
            for v in perm_dict.keys():
                if v not in used_varsB:
                    used_perm_dictB.pop(v)
        # Get the probability of the permutation on factorB
        for tup, prob in factorB[1].items():
            dit = tuple_to_dict(tup)
            if all(key in dit and dit[key] == val for key, val in used_perm_dictB.items()):
                prob2 = prob

        probabilities[perm] = prob1 * prob2

    return vars, probabilities


def sum_out(nodes, var, factors, e):
    """
    Sum out factors, based on var
    :param var:         The var to remove
    :param factors:     List of factors in form of [([factor_vars]), {(perm, prob)})]
    :return:
    """
    factors_with_var = []
    indices = []
    for i, factor in enumerate(factors):
        if var in factor[0]:
            factors_with_var.append(factor)
            indices.append(i)

    if len(factors_with_var) > 1:
        for i in reversed(indices):
            del factors[i]
        result = factors_with_var[0]
        for factor in factors_with_var[1:]:
            result = product(nodes, result, factor, e)
        factors.append(result)

    # SUM-OUT OPERATION
    # For each factor:
    # Calculate the table of the new factor

    # If the only value that changed in a permutation is the value of
    # the variable we are eliminating, sum the probabilities of those permutations
    # i.e:
    #   C   X   Prob            Eliminating X:      C   Prob
    #   T   p   0.9                                 T   1.0 (0.9 + 0.1)
    #   T   n   0.1                                 F   1.0 (0.2 + 0.8)
    #   F   p   0.2
    #   F   n   0.8                              (Only 2 permutations, not 4)

    #   C   D   Prob            Eliminating D:      C   Prob
    #   T   T   0.65                                T   1.0 (0.65 + 0.35)
    #   T   F   0.35                                F   1.0 (0.3 + 0.7)
    #   F   T   0.3
    #   F   F   0.7                              (Only 2 permutations, not 4)

    for i, factor in enumerate(factors):
        for j, v in enumerate(factor[0]):
            if v == var:
                # variables of the new factor (remove var from the current factor)
                new_vars = factor[0][:j] + factor[0][j+1:]
                var_probs = {}
                for tup, prob in factor[1].items():
                    perm = tuple_to_dict(tup)

                    # The "remaining perm" is the perm without the var we are summing out
                    remaining_perm = deepcopy(perm)
                    remaining_perm.pop(var)

                    # Search for the "remaining perm" in the tuples of the list
                    # Sum the values of the probabilities on the cases
                    # where the "remaining perm" matches
                    for tup2, prob2 in factor[1].items():
                        check_perm = tuple_to_dict(tup2)
                        if all(check_perm[key_perm] == val_perm for key_perm, val_perm in remaining_perm.items()):
                            if dict_to_tuple(remaining_perm) in var_probs.keys():
                                var_probs[dict_to_tuple(remaining_perm)] += prob2
                            else:
                                var_probs[dict_to_tuple(remaining_perm)] = prob2

                # replace the old factor
                factors[i] = (new_vars, var_probs)
                if len(new_vars) == 0:
                    del factors[i]
    return factors

def init_factors(nodes, q, e, flag):
    global deb
    elimd = set()
    factors = []

    i = 0
    while i < len(nodes):
        vars = filter(lambda var: var not in elimd, list(nodes.keys()))
        if flag==1:
            vars = filter(lambda var: all(parent in elimd for parent in nodes[var].parent), vars)
        elif flag==2:
            vars = filter(lambda var: all(child in elimd for child in nodes[var].child), vars)
        else:
            tmp={}
            for v in vars:
                tmp[v]=nodes[v].cardinal
            tmp=sorted(tmp.items(), key=lambda x: x[1],reverse=True)
            vars=[]
            for a in tmp:
                vars.append(a[0])
        factor_vars = {}

        for var in vars:
            factor_vars[var] = [par for par in nodes[var].parent if par not in e]
            if var not in e:
                factor_vars[var].append(var)

        var_to_elim = list(factor_vars.keys())[0]

        if len(factor_vars[var_to_elim]) > 0:
            factors.append(make_factor(nodes, var_to_elim, factor_vars[var_to_elim], e))

        if var_to_elim != q and var_to_elim not in e:
            if deb:
                print("Eliminating " + var_to_elim)
            factors = sum_out(nodes, var_to_elim, factors, e)

        elimd.add(var_to_elim)
        i += 1  # Not a part of the code

    if len(factors) >= 2:
        result = factors[0]
        for factor in factors[1:]:
            result = product(nodes, result, factor, e)
    else:
        result = factors[0]

    result = normalize_factor(nodes, result, q)

    return result


def normalize_factor(nodes, factor, q):
    sum_probs = sum(factor[1].values())
    probs = []
    probs_dict={}
    for tup, prob in factor[1].items():
        dit = tuple_to_dict(tup)
        for clas in nodes[q].classes:
            if dit[q] == clas:
                if clas in probs_dict:
                    probs_dict[clas]+=prob
                else:
                    probs_dict[clas]=prob
    for clas, prob in probs_dict.items():
        if len(probs)==0:
            probs=[(clas,round(prob/sum_probs,5))]
        else:
            probs.append((clas,round(prob/sum_probs,5)))
    return probs


if __name__ == "__main__":
    es = {}
    print("Input BIF file name w/o extension")
    file = str(input())
    nodes, names = parser(file)
    if deb:
        debug(nodes)
    print("Available Variables: ", names)
    print("Pr? ", end='')
    query = str(input())
    q, e, f = queryParser(query,nodes)
    while True:
        if q not in names:
            print("Error. ", q, " not available.")
            print("Available variables: ", names)
            f = -1
        else:
            for ev in e.keys():
                if ev not in names:
                    print("Error. ", ev, " not available.")
                    print("Available variables: ", names)
                    f = -1
                elif e[ev] not in nodes[ev].classes:
                    print("Error. '", e[ev], "' isn't valid.")
                    print("Available values for variable ",ev,": ",nodes[ev].classes,".")
                    f= -1
                else:
                    pass
        if f == -1:
            print("Try again. Pr? ", end='')
            query = str(input())
            q, e, f = queryParser(query, nodes)
        else:
            break
    print("--------------------------------------------------")
    print("Tamanho da rede: ",len(nodes))
    core(nodes, names, q, e)