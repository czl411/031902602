import sys
import time
import pypinyin
from pychai import Schema
from zhconv import convert

def get_ans_and_out(ans, org_txt, path):          #一行一行的找出敏感词
    file = open(org_txt, encoding="utf-8")      #以‘utf-8’的形式，打开文本文件（文章）
    lines = 0
    while 1:
        line = file.readline()                  #读取一整行文件，赋给line
        if not line:
            break                               #最后一行，跳出
        lines += 1
        ans_in_lines = []                       #以列表的方式，存出问题的地方（元组：第几行、什么敏感词、原词）
        ans_in_lines.extend(get_list(ans, line, lines))   #加入第lines行的扫描结果
        for i in ans_in_lines:                  #一个i代表一个出问题的地方
            ans.answer.append("Line" + str(lines) + ": <" + i[2] + "> " + line[i[0]:i[0] + i[1]] + "\n")    #全扫描之后加入到结果（列表）中
    with open(path, 'a', encoding='utf-8') as f:  # 以‘utf-8’格式，打开输出目标文件
        f.write("Total: " + str(ans.sum) + '\n')
        for info in ans.answer:
            f.write(info)

def dfs(nums, t, result):
        tmp_copy = t.copy()  # 拷贝一份
        if len(t) >= nums:
            result.append(tmp_copy)
            return

        for i in range(3):
            t.append(i)
            dfs(nums, t, result)
            t.pop()
        return

def allpossible(nums):  # 返回排列组合后的所有可能
        result = []
        tmp = []
        dfs(nums, tmp, result)
        return result

def get_list(ans, txt, lines):  # 传入（测试文本，没用，没用）返回起始位置、长度、敏感词 三元组
    now_tree = ans.mgtree
    start_index = -1
    original_length = -1
    scan_mode = -1                      # 1检测中文
    ans_location = []                   #存本行扫描结果
    index_text = 0                      #总共有多少错误
    temp_now_tree = {}
    ingore_index = -1
    while index_text < len(txt):
        key = txt[index_text]
        if key.isalpha():
            key = key.lower()  # 一律改小写
        if '\u4e00' <= key <= '\u9fff':
            key = convert(key, 'zh-hans')  # 一律转简体

        if not key.isalpha() and not ('\u4e00' <= key <= '\u9fff'):  # 去除掉 符号 空格等
            original_length += 1
            index_text += 1
            continue
        flag_find = key in now_tree
        if flag_find:
            now_tree = now_tree.get(key)
            if now_tree.get("isEnd") == 1:  # 结束识别
                if not temp_now_tree and now_tree.get("canBeMore"):

                    if index_text == len(txt) - 2:
                        if str(lines) + str(start_index) not in ans.already_exist.keys():
                            ans_location.append((start_index, original_length, ans.transfomer_hanzi[now_tree.get("word")]))
                        ans.already_exist[str(lines) + str(start_index)] = 1
                        now_tree = ans.mgtree
                        original_length = -1
                        start_index = -1
                        scan_mode = -1
                        ans.sum += 1
                        index_text += 1
                        temp_now_tree = {}
                        continue
                    temp_now_tree = now_tree  # 保存当前状态
                    ingore_index += 1
                    index_text += 1
                    original_length += 1
                    continue
                else:
                    if str(lines) + str(start_index) not in ans.already_exist.keys():
                        ans_location.append((start_index, original_length, ans.transfomer_hanzi[now_tree.get("word")]))
                    ans.already_exist[str(lines) + str(start_index)] = 1
                    now_tree = ans.mgtree  # 恢复now_map
                    original_length = -1
                    start_index = -1
                    scan_mode = -1
                    ans.sum += 1
                    index_text += 1
                    temp_now_tree = {}
                    continue
            if (now_tree.get("isStart") == 1) & (start_index == -1):  # 找到敏感词头
                if scan_mode == -1 and ('\u4e00' <= key <= '\u9fff'):
                    scan_mode = 1
                original_length = 1
                start_index = index_text
            original_length += 1
            index_text += 1
        else:
            if temp_now_tree:
                if str(lines) + str(start_index) not in ans.already_exist.keys():
                    ans_location.append((start_index, original_length - 1, ans.transfomer_hanzi[temp_now_tree.get("word")]))
                ans.already_exist[str(lines) + str(start_index)] = 1
                now_tree = ans.mgtree
                original_length = -1
                start_index = -1
                scan_mode = -1
                ans.sum += 1
                index_text -= ingore_index
                temp_now_tree = {}
                continue
            if scan_mode == 1:
                if key.isalpha() or key.isdecimal():  # 这里屏蔽不了中文 不知道为啥
                    if not ('\u4e00' <= key <= '\u9fff'):
                        original_length += 1
                        index_text += 1
                        continue
            if '\u4e00' <= key <= '\u9fff':  # 对于中文 寻找同音的替换
                pinyin = pypinyin.lazy_pinyin(key)[0]
                noYet = True
                now_index = index_text
                for i in pinyin:
                    flag_find_pinyin = i in now_tree
                    if flag_find_pinyin:
                        if (now_tree.get("isStart") == 1) & (start_index == -1):  # 找到敏感词头
                            if scan_mode == -1 and ('\u4e00' <= key <= '\u9fff'):
                                scan_mode = 1
                            original_length = 1
                            start_index = now_index
                        now_tree = now_tree.get(i)
                    else:
                        noYet = False
                        break
                if noYet:
                    original_length += 1
                    if now_tree.get("isEnd") == 1:  # 结束识别
                        original_length -= 1
                        if str(lines) + str(start_index) not in ans.already_exist.keys():
                            ans_location.append((start_index, original_length, ans.transfomer_hanzi[now_tree.get("word")]))
                        ans.already_exist[str(lines) + str(start_index)] = 1
                        now_tree = ans.mgtree
                        original_length = -1
                        start_index = -1
                        scan_mode = -1
                        ans.sum += 1
                        index_text += 1
                        temp_now_tree = {}
                        continue
                    index_text += 1
                    continue
            now_tree = ans.mgtree
            start_index = -1
            original_length = -1
            index_text += 1
    return ans_location

def init_mgtree(ans, sensitive_word_list):  # 造树过程
    sensitive_word_tree = {}                 #存放结果

    for word in sensitive_word_list:        #一个词一个词来建立
        now_tree = sensitive_word_tree

        for i in range(len(word)):          #一个字一个字来
            keychar = word[i]                    #第一个字
            word_tree = now_tree.get(keychar)      #返回key对应的键值

            if word_tree:                    #key键值不空
                now_tree = word_tree
            else:
                next_tree = {"isEnd": 0}
                now_tree[keychar] = next_tree
                now_tree = next_tree
                if keychar in ans.souzm:
                    now_tree["canBeMore"] = 1
            # 到最后一个字

            if i == len(word) - 1:
                now_tree["isEnd"] = 1
                now_tree["word"] = word
            if i == 0:
                now_tree["isStart"] = 1

    return sensitive_word_tree

def kuozhan(self):
    for string in self.original_word:
            self.wordschai.append(string.lower())    #敏感词统一格式，都转换成小写
            tw = ""
            if '\u4e00' <= string[0] <= '\u9fff':           #是否是汉字
                for char in string:
                    if char in wubi98.tree:
                        tree = wubi98.tree[char]
                        first = tree.first
                        second = tree.second
                        while first.structure == 'h':
                            if first.first is None:
                                break
                            first = first.first
                        while second.structure == 'h':
                            if second.second is None:
                                break
                            second = second.second
                        tw += first.name[0]
                        tw += second.name
                        self.chai_dic[first.name[0]] = 1  # 对于偏旁来说 拼音的组合不被需要
                        self.chai_dic[second.name] = 1
                        self.need_another_part[first.name[0]] = second.name  # 对于偏旁来说 汉字的组合需要增加另一半
                    else:
                        tw += char
                self.wordschai.append(tw)
            self.transfomer_hanzi[string.lower()] = string
            self.transfomer_hanzi[tw] = string
    pinyin_sentitive_word = list(set(self.wordschai))  # 去重

    # 开始做拼音+本体的中文
    # ans_dataset中 0为需要用拼音的地方 1为用中文的地方 2为拆字  开始组词
    for tw in self.wordschai.copy():  # 注意用copy 不然越打越多

        if '\u4e00' <= tw[0] <= '\u9fff':  # 识别为汉字

            pinyin = pypinyin.lazy_pinyin(tw)  # 拼音数组
            temp_word_respective = []  # 汉字数组 临时每一个单词
            for i in range(len(tw)):
                temp_word_respective.append(tw[i])
            ans_dataset = allpossible(len(tw))  # ans_dataset是组合列表
            chai_dic = False
            for i in ans_dataset:

                index = 0  # 子列表中第几个数
                result_word = ""  # 最终组合结果
                for j in range(len(i)):
                    if i[j] == 1:
                        result_word += temp_word_respective[index]
                        if temp_word_respective[index] in self.need_another_part:
                            result_word += self.need_another_part[temp_word_respective[index]]
                    if i[j] == 0:
                        if temp_word_respective[index] in self.chai_dic:
                            chai_dic = True
                        result_word += pinyin[index]
                    if i[j] == 2:
                        if temp_word_respective[index] in self.chai_dic:
                            chai_dic = True
                        result_word += pinyin[index][0]
                        self.souzm[pinyin[index][0]] = 1
                    index += 1

                if not chai_dic:  # 不需要跳过
                    pinyin_sentitive_word.append(result_word)
                if result_word not in self.transfomer_hanzi:
                    self.transfomer_hanzi[result_word] = tw
        else:
            self.transfomer_hanzi[tw] = tw

    pinyin_sentitive_word = list(set(pinyin_sentitive_word))  # 去重
    self.mgtree = init_mgtree(self, pinyin_sentitive_word)  # 构造trie树

class MGci:
    def __init__(self, word_path):
        self.mgtree = []                    #敏感词树
        self.sum = 0                        #存最终有多少个
        self.answer = []                    #存结果
        self.transfomer_hanzi = {}          #存敏感词的各种形式
        self.original_word = []             #存敏感词
        self.wordschai = []                 #存敏感词左右拆分
        self.souzm = {}                     #存敏感词以及拆分词的首字母
        self.chai_dic = {}                  #存拆分后的敏感词的字和偏旁，以字典的形式，若可以查到，返回1
        self.need_another_part = {}         #组成敏感字的对应偏旁和部首，用字典的形式。比如‘ 氵’：‘去’
        self.already_exist = {}

        # --读入敏感词汇 获得pinyin
        with open(word_path, "r", encoding='utf-8') as file:
            self.original_word = file.readlines()  # 读入文本
        self.original_word = sorted([i.split('\n')[0] for i in self.original_word])  # 按照换行符区分不同敏感词
        kuozhan(self)

if __name__ == '__main__':
    wubi98 = Schema('wubi98')
    wubi98.run()
    if len(sys.argv) > 1:
        words_txt = sys.argv[1]
        org_txt = sys.argv[2]
        ans_txt = sys.argv[3]
    elif len(sys.argv) == 1:
        wordsname = "words.txt"
        orgname = "org.txt"
        ansname = "ans.txt"
    else:
        print("输入错误!")
        exit(0)
    t1 = time.time()
    ans = MGci(words_txt)
    get_ans_and_out(ans,org_txt,ans_txt)  # 得到答案数组并输出到文件
    t2 = time.time()
    sum_t = t2 - t1
    #print(t2)
    exit()