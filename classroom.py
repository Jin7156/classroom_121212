import numpy as np
import random as rm

#js에서 받은 값을 dick형태로 저장해야함, js에서 object형태로 저장하고 json으로 바꾼다음 json을 python의 dick으로 저장

stdnt_num = 24
stdnt_dict = { # 그 dick가 애가 될것임
    "stdnt1": 
    "stndt2":
}
name_lst = list.(stdnt_dict.keys())

c_name_lst = random.sample(name_lst, len(name_lst))

desk_lst = [
    [1,2],
    [5,4]
]
for i in range(2):
    desk_lst[i].append(stdnt_dict[c_name_lst[i]])