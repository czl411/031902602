import main

#测试是否可以正确判断是否为汉字
def test_hanzi():
    test1 = ['fuawd','哇饿啊上的','qwesw','订购']
    for word in test1:
        if main.hanzi(word):
            print(word,'yes')

test_hanzi()