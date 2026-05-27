'''학생의 이름과 키를 dict으로 저장, 튜플리스트로 바꿔서 키순대로 정렬, 
키와 시력순으로 나누어둔 리스트에 각각 이름을 저장, 
for i in range(len(학생 리스트)):
    i +=
    나누어진 리스트.append(학생 튜플리스트[i][0])

아무튼 그 구간마다 학생 이름 리스트에 저장한다음
그거를 랜덤으로 섞고, 그거를 key로 삼아서 자리배치에 계산할 리스트에 넣는다. 그리고 조건에 부합하느넥 나오면 그거를 html쪽에 저장을 한ㄷ. '''
import config as cn
numlen_short0 = len(cn.desk_lst_shortbad) -1
numlen_short1 = len(cn.desk_lst_shortgood)-1
numlen_high1 = len(cn.desk_lst_higgood) -1
numlen_high0 = len(cn.desk_lst_highbad) - 1

def setting(lst):
    for i in range(len(lst)-1):
        if cn.stdnteye_dict.get(lst[n][0], None) == 0: