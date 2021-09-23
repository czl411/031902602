import main

#测试是否可以得到所有重组形式
def test_AC():
    test1 = main.AC(0,[['拼', '拼', 'p', '扌并'], ['银', 'yin', 'y', '钅艮']],[],[])
    for i in test1:
        print(i)

test_AC()