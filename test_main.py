import main

#测试给一组数据，能否得出正确结果
def test_main():
    test_sensitive_word = ['你好','再见','good']
    txt = ['我让你好拉拉，哇基地啊加我i，哇哈毒害子啊见在建房子，你很棒，good！GOOD！',
           '好你好，你---女子，不太想在建！',
            '',
           'zaij吧！你好菜！g==o--od！']
    pinyin_list = main.Cpinyin_list(test_sensitive_word)
    test_tree = main.CTree(pinyin_list)
    for word in test_sensitive_word:
        d = []
        if main.hanzi(word):
            c = main.AC(0, main.chinesewords(word).info, [], [])
            for i in range(len(c)):
                d.append(''.join(c[i]))
        else:
            low_word = word.lower()
            d.append(low_word)
        test_tree.insert(d, word)
    for i,e in enumerate(txt):
        if len(e) == 0:
            continue
        test_tree.search_by_line(i+1,e)
    for ans in test_tree.ans:
        print(ans)

test_main()