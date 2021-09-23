import sys
from pypinyin import lazy_pinyin as lpy
import json
import zhconv

json_path = 'chaizi_package.json'
f = open(json_path, 'r', encoding='utf-8')
chaizi_dict = json.load(f)       #存各个能拆的汉字的结果
f.close()

class Engword:                      #存一个英语单词
    def __init__(self,word):
        self.orginal = word
        self.length = len(word)
        self.info = []
        for i in range(len(word)):
            self.info.append(word[i])

class chinesewords:                 #存一个中文词
    def __init__(self, word):
        self.length = len(word)    #词长
        self.info = []              #存词中，每个字的信息
        for char in word:#遍历存
            pinyin = lpy(char)[0]
            if char in chaizi_dict:
                self.info.append([char, pinyin, pinyin[0], chaizi_dict[char]])
            else:
                self.info.append([char, pinyin, pinyin[0]])    # 存自己的信息

class Trie_node:
    def __init__(self,value=None):
        self.value= value
        self.leaf = {}
        self.leaf['end'] = 0
        self.leaf['word'] = str()
        self.fail = None

class CTree:
    def __init__(self,pylist):
        self.flag = False
        self.root = Trie_node()
        self.Special_symbols = [' ', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')',
                                '[', ']', ';', ':', '"', ',', '<', '>', '.', '/', '?',
                                '{', '}', '`', '-', '_', '+', '=', '|', '\\', '\'',
                                '？', '、', '。', '，', '》', '《', '；', '：', '“', '‘',
                                '【', '】', '！', '￥', '…', '·', '~', '—',
                                '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        self.ans = []
        self.pinyin_list = pylist

    def insert(self, words, sensitive_word):
        for word in words:
            curr = self.root
            for i,char in enumerate(word):
                if char not in curr.leaf:
                    curr.leaf[char] = Trie_node(char)
                curr = curr.leaf[char]
                if i == len(word) - 1:
                    curr.leaf['end'] = 1
                    curr.leaf['word'] = sensitive_word

    def search_by_line(self, cnt_line, stence):     #一行一行的找
        low_stence = zhconv.convert(stence.lower(),'zh-hans')   #繁体转为简体，以及大写转小写
        totall_right = 0
        sindex = -1                                 #记录起点
        curr = self.root                            #根节点
        i = 0
        flag1 = len(low_stence) * [0]
        while i < len(low_stence):
            if low_stence[i] in curr.leaf:
                curr = curr.leaf[low_stence[i]]
                if i == len(low_stence) -1 and curr.leaf['end']:
                    for j in range(sindex,i):
                        flag1[j] = 1
                    self.ans.append(
                        'Line{}: <{}> {}\n'.format(cnt_line, curr.leaf['word'], stence[sindex:i]))
                    break
                if sindex < 0:
                    sindex = i
                i +=1
            elif low_stence[i] in self.Special_symbols:
                if sindex >= 0 and curr.leaf['end']:
                    for j in range(sindex,i):
                        flag1[j] = 1
                    self.ans.append(
                        'Line{}: <{}> {}\n'.format(cnt_line, curr.leaf['word'], stence[sindex:i]))
                    sindex = -1
                    curr = self.root
                elif sindex >= 0 and not curr.leaf['end']:
                    i += 1
                else:
                    curr = self.root
                    i += 1
            else:
                if hanzi(low_stence[i]):
                    if curr.leaf['end']:
                        for j in range(sindex, i):
                            flag1[j] = 1
                        self.ans.append(
                            'Line{}: <{}> {}\n'.format(cnt_line, curr.leaf['word'], stence[sindex:i]))
                        sindex = -1
                        curr = self.root
                    elif lpy(low_stence[i])[0] not in self.pinyin_list:
                        if curr.leaf['end']:
                            for j in range(sindex, i):
                                flag1[j] = 1
                            self.ans.append(
                                'Line{}: <{}> {}\n'.format(cnt_line, curr.leaf['word'], stence[sindex:i]))
                        sindex = -1
                        curr = self.root
                        i +=1
                    else:
                        for char in lpy(low_stence[i])[0]:
                            if char in curr.leaf:
                                totall_right += 1
                                curr = curr.leaf[char]
                            else:
                                break
                        if totall_right == len(lpy(low_stence[i])[0]):
                            totall_right = 0
                            if sindex < 0:
                                sindex = i
                            i +=1
                            if curr.leaf['end']:
                                for j in range(sindex, i):
                                    flag1[j] = 1
                                self.ans.append(
                                    'Line{}: <{}> {}\n'.format(cnt_line, curr.leaf['word'], stence[sindex:i]))
                                sindex = -1
                                curr = self.root
                            continue
                        else:
                            if curr.leaf['end']:
                                for j in range(sindex, i):
                                    flag1[j] = 1
                                self.ans.append(
                                    'Line{}: <{}> {}\n'.format(cnt_line, curr.leaf['word'], stence[sindex:i]))
                            sindex = -1
                            curr = self.root
                            if low_stence[i] in curr.leaf:
                                curr = curr.leaf[low_stence[i]]
                                sindex = i
                            i += 1
                else:
                    if curr.leaf['end']:
                        for j in range(sindex, i):
                            flag1[j] = 1
                        self.ans.append(
                            'Line{}: <{}> {}\n'.format(cnt_line, curr.leaf['word'], stence[sindex:i]))
                    sindex = -1
                    curr = self.root
                    if low_stence[i] in curr.leaf:
                        curr = curr.leaf[low_stence[i]]
                        sindex = i
                    i += 1

        sindex = -1  # 记录起点
        curr = self.root  # 根节点
        i = 0
        while i < len(low_stence):
            if flag1[i]:
                i+=1
                curr = self.root
                sindex= -1
                continue
            if low_stence[i] in curr.leaf:
                mid_curr = curr
                if lpy(low_stence[i])[0] in self.pinyin_list:
                    total = 0
                    for char in lpy(low_stence[i])[0]:
                        if char in mid_curr.leaf:
                            total += 1
                            mid_curr = mid_curr.leaf[char]
                        else:
                            break
                    if total == len(lpy(low_stence[i])[0]) and mid_curr.leaf['end']:
                        curr = mid_curr
                        self.flag = True
                if not self.flag:
                    curr = curr.leaf[low_stence[i]]
                self.flag = False
                if curr.leaf['end']:
                    for j in range(sindex,i+1):
                        flag1[j] = 1
                    self.ans.append(
                        'Line{}: <{}> {}\n'.format(cnt_line, curr.leaf['word'], stence[sindex:i+1]))
                    curr = self.root
                if sindex < 0:
                    sindex = i
                i +=1
            elif low_stence[i] in self.Special_symbols:
                if sindex >= 0 and curr.leaf['end']:
                    for j in range(sindex,i):
                        flag1[j] = 1
                    self.ans.append(
                        'Line{}: <{}> {}\n'.format(cnt_line, curr.leaf['word'], stence[sindex:i]))
                    sindex = -1
                    curr = self.root
                elif sindex >= 0 and not curr.leaf['end']:
                    i += 1
                else:
                    curr = self.root
                    i += 1
            else:
                if hanzi(low_stence[i]):
                    if curr.leaf['end']:
                        for j in range(sindex, i):
                            flag1[j] = 1
                        self.ans.append(
                            'Line{}: <{}> {}\n'.format(cnt_line, curr.leaf['word'], stence[sindex:i]))
                        sindex = -1
                        curr = self.root
                    elif lpy(low_stence[i])[0] not in self.pinyin_list:
                        if curr.leaf['end']:
                            for j in range(sindex, i):
                                flag1[j] = 1
                            self.ans.append(
                                'Line{}: <{}> {}\n'.format(cnt_line, curr.leaf['word'], stence[sindex:i]))
                        sindex = -1
                        curr = self.root
                        i +=1
                    else:
                        for char in lpy(low_stence[i])[0]:
                            if char in curr.leaf:
                                totall_right += 1
                                curr = curr.leaf[char]
                            else:
                                break
                        if totall_right == len(lpy(low_stence[i])[0]):
                            totall_right = 0
                            if sindex < 0:
                                sindex = i
                            i +=1
                            if curr.leaf['end']:
                                for j in range(sindex, i):
                                    flag1[j] = 1
                                self.ans.append(
                                    'Line{}: <{}> {}\n'.format(cnt_line, curr.leaf['word'], stence[sindex:i]))
                                sindex = -1
                                curr = self.root
                            continue
                        else:
                            if curr.leaf['end']:
                                for j in range(sindex, i):
                                    flag1[j] = 1
                                self.ans.append(
                                    'Line{}: <{}> {}\n'.format(cnt_line, curr.leaf['word'], stence[sindex:i]))
                            sindex = -1
                            curr = self.root
                            if low_stence[i] in curr.leaf:
                                curr = curr.leaf[low_stence[i]]
                                sindex = i
                            i += 1
                else:
                    if curr.leaf['end']:
                        for j in range(sindex, i):
                            flag1[j] = 1
                        self.ans.append(
                            'Line{}: <{}> {}\n'.format(cnt_line, curr.leaf['word'], stence[sindex:i]))
                    sindex = -1
                    curr = self.root
                    if low_stence[i] in curr.leaf:
                        curr = curr.leaf[low_stence[i]]
                        sindex = i
                    i += 1

def Cpinyin_list(words):
    pinyin_list = []
    for word in words:
        if hanzi(word):
            for char in word:
                if lpy(char)[0] not in pinyin_list:
                    pinyin_list.append(lpy(char)[0])
    return pinyin_list

def AC(step, word, st, result):
        # 递归，建立各类敏感词的变形形式
        if step == len(word):
            result.append(st)
            return
        else:
            for i in range(len(word[step])):
                AC(step + 1, word, st + list(word[step][i]), result)
        return result

def hanzi(word):                     #判断是否是汉字
    if 'a' <= word[0] <= 'z' or 'A' <= word[0] <= 'Z':
        return 0
    else:
        return 1

def get_ans_out(word_path,passage_path,ans_path):
    with open(word_path, 'r', encoding='utf-8') as f:
        sensitive_word = f.readlines()
    for i in range(len(sensitive_word)):
        sensitive_word[i] = sensitive_word[i].strip('\n')
    pinyin_list = Cpinyin_list(sensitive_word)
    with open(passage_path, 'r', encoding='utf-8') as f:
        txt = f.readlines()
    for i in range(len(txt)):
        txt[i] = txt[i].strip('\n')
        txt[i] = txt[i].strip(' ')
        if len(txt[i]) == 0:
            continue
    tree = CTree(pinyin_list)
    for word in sensitive_word:
        d = []
        if hanzi(word):
            c = AC(0, chinesewords(word).info,[],[])
            for i in range(len(c)):
                d.append(''.join(c[i]))
        else:
            low_word = word.lower()
            d.append(low_word)
        tree.insert(d, word)

    for i,e in enumerate(txt):
        if len(e) == 0:
            continue
        tree.search_by_line(i+1,e)
    tree.ans.insert(0,'Total:{}\n'.format(len(tree.ans)))
    with open(ans_path, "w") as f:
        for i in range(len(tree.ans)):
            f.write(tree.ans[i])

if __name__ == '__main__':
    if  len(sys.argv) == 4:
        word_path = sys.argv[1]
        passage_path = sys.argv[2]
        ans_path = sys.argv[3]
    else:
        print("输入错误！请重新输入")
        exit()
    get_ans_out(word_path,passage_path,ans_path)

