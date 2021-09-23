import json

json_path = 'chaizi_package.json'
f = open(json_path, 'r', encoding='utf-8')
chaizi_dict = json.load(f)
f.close()

#测试是否可以得到正确的拆分
def test_chai():
    print(chaizi_dict['伐'])
    print(chaizi_dict['拼'])
    print(chaizi_dict['银'])

test_chai()
