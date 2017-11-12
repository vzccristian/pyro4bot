


def funcion(l):
    if type(l) not in (list,tuple): l=(l,)
    for k in l:
        print k
funcion([1,2,4])
funcion("oo")
funcion(8)
funcion(("l",9,7,"paco"))
funcion(None)
