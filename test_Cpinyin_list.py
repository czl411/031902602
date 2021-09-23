import main

#是否可以得到敏感词拼音表，且去重
def test_Cpinyin_list():
    test1 = ['傻逼逼','侧面积','厉害牛的','牛里脊肉']
    print(main.Cpinyin_list(test1))

test_Cpinyin_list()