import main

#测试是否可以得到一个汉语敏感词的各个词的敏感形式
def test_chinesewords():
    test1 = main.chinesewords('你好菜啊')
    print(test1.info)

test_chinesewords()