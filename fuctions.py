import numpy as np
import random as rm
import config as cn

#js에서 받은 값을 dick형태로 저장해야함, js에서 object형태로 저장하고 json으로 바꾼다음 json을 python의 dick으로 저장


def ramdomset(dict):
    names = list(dict.keys())
    rm_namelst = rm.sample(names, len(names))
    for i in range(len(names)):
        cn.desk_lst[i].append(dict[rm_namelst[i]])
    return rm_namelst #가장 효율적인 자리배치를 찾았을 경우의 리스트를 순차적으로 변수에 저장해야함, 애는 그런거 못함

def numpylylst(classroom, desk, plate):
    mathdesk = np.array(desk)
    mathclass = np.arrary(clasroom)
    mathplate = np.array(plate)
    return mathclass, mathdesk, mathplate

def deskset():
    