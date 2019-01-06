import itchat
from itchat.content import *
import shelve
import re
import threading

templates = ['.*说到.*(我就想起了.*)*','惊闻.*深感.*','\.\.两开花','.*说到.*(我就想到了.*)*','.*不是.*不是.*','.*小朋友.*问我.*几.*','.*心中只有一个.*',
    '.*是可悲的.*是可耻的','.*是要给.*谢罪的','.*不分.*颠倒','我.*28.*82.*我太了解.*了','.*从28.*到82.*','我从.*到.*我太了解.*了','弘扬.*希望多多.*','苦练.*笑对.*','.*都没有.*没有.*这就.*啊',
    '我将继续扮演.*','.*叔叔.*到底有几.*啊','.*显神通.*样样有','体验不一样的.*文化','.*要向全国人民谢罪','师父我们走','师父，我们走']
words = ['六小龄童','妖精','金猴皮鞋','皮鞋','营养钙面','六小灵童','孙悟空','美猴王','开花','六学','西游',
    '西天取经','白骨精','大闹天宫','身份证','签售','签书','敢问路在何方','中美合拍','中外合拍','章金莱']
viwords = ['零糖麦片','章口就莱','灵堂卖片','遛小龄童','遛小灵童','战术后仰','野生锁链','章承恩']
crDict = {}
sentences = []
lock = threading.Lock()
noRepeat = None #我真的不知道这个库为什么会不由自主的复读

check = lambda s:tCheck(s) or wCheck(s) or sCheck(s)

def record(flag,name,nickName):
    db['chatrooms'][name]['total'] += 1
    if not nickName in db['chatrooms'][name]['personal']:
        db['chatrooms'][name]['personal'][nickName] = {}
        db['chatrooms'][name]['personal'][nickName]['total'] = db['chatrooms'][name]['personal'][nickName]['666'] = 0
    db['chatrooms'][name]['personal'][nickName]['total'] += 1
    if flag:
        db['chatrooms'][name]['666'] += 1
        db['chatrooms'][name]['personal'][nickName]['666'] += 1

@itchat.msg_register(TEXT, isGroupChat = True)
def text_reply(msg):
    global noRepeat
    if msg == noRepeat:
        return
    noRepeat = msg
    with lock:
        if msg['FromUserName'] in crDict:
            if crDict[msg['FromUserName']] in db['names']:
                name = crDict[msg['FromUserName']]
                s = msg.text
                nickName = msg.actualNickName
                if msg['Content'] == '$666$':
                    if not name in db['chatrooms'] or not db['chatrooms'][name]['total']:
                        msg.user.send('无本群数据。你记录群六学数据，你说你记录的比我好，来，你上来试试。')
                    else:
                        msg.user.send('我看着贵群六度从28上升到82，我太了解贵群了。\n群六度:%.2f%%' % (db['chatrooms'][name]['666'] / db['chatrooms'][name]['total'] * 100))
                elif msg['Content'] == '$help$':
                    msg.user.send('我记录群六学也只是代表我本人的一种风格，我怎么会去说我是正宗、唯一？不可能。\n$[言论]$ 判定是否为六学言论 例：$戏说不是胡说，改编不是乱编$\n$666$ 返回群六学度\n$help$ 使用帮助')
                elif msg['Content'] == '$6star$':
                    if not name in db['chatrooms'] or not db['chatrooms'][name]['total']:
                        msg.user.send('无本群数据。你记录群六学数据，你说你记录的比我好，来，你上来试试。')
                    star = sorted(list(db['chatrooms'][name]['personal'].items()),key = lambda x:x[1]['666'],reverse = True)[0]
                    msg.user.send('大家好，群六学之星是[%s]，是大闹天宫首席文化大使。\n六学言论数：%d\t六度：%.2f%%' % 
                        (star[0],star[1]['666'],star[1]['666'] / star[1]['total'] * 100))
                elif msg.text[0] == '$' and msg.text[len(msg.text) - 1] == '$':
                    s = msg.text[1:len(msg.text) - 1]
                    if tCheck(s) or wCheck(s) or sCheck(s):
                        msg.user.send('那现在我们的个别微信群六学遍地，你们好笑我是笑不出来，我说我这个眼泪在肚子里我笑不出来。')
                        record(True,name,nickName)
                    else:
                        msg.user.send('我从来没有诋毁过其他版本的西游记，沙雕群友也没有玩六学梗。')
                        record(False,name,nickName)
                else:
                    if not name in db['chatrooms']:
                        db['chatrooms'][name] = {}
                        db['chatrooms'][name]['666'] = db['chatrooms'][name]['total'] = 0
                        db['chatrooms'][name]['personal'] = {}
                    if tCheck(s) or wCheck(s) or sCheck(s):
                        record(True,name,nickName)
                    else:
                        record(False,name,nickName)

def nameCmd(cmd):
    s = cmd.split(' ')
    if len(s) == 1:
            print('缺少参数，我安检的时候，都听说你这个指令是假的。')
            return None
    else:
        name = s[1]
        for i in range(2,len(s)):
            name += ' ' + s[i]
        return name

def tCheck(s):
    cnt = 0
    for t in templates:
        cnt += len(re.findall(t,s))
    return cnt > 0

def wCheck(s):
    for w in viwords:
        if s.find(w) != -1:
            return 1
    cnt = 0
    threshold = 0.08
    for w in words:
        cnt += s.count(w)
    return cnt / len(s) >= threshold

def lcsSim(s1,s2):
    l1,l2 = len(s1),len(s2)
    f = [[0] * (l2 + 1)] * (l1 + 1)
    for i in range(1,l1 + 1): 
        for j in range(1,l2 + 1): 
            if s1[i - 1] == s2[j - 1]: 
                f[i][j] = 1 + f[i - 1][j - 1]
            else:
                f[i][j] = max(f[i - 1][j],f[i][j - 1]) 
    return f[l1][l2] / min(l1,l2)

def ignorePunc(s):
    p = """！？｡＂＃＄％＆＇（）＊＋－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰–—‘'‛“”„‟…‧﹏!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~"""
    s2 = []
    for c in s:
        if not c in p:
            s2.append(c)
    return "".join(s2)

def sCheck(s):
    threshold = 0.8
    for st in sentences:
        if lcsSim(ignorePunc(st),ignorePunc(s)) >= threshold:
            return 1
    return 0

itchat.auto_login(True)

db = shelve.open('666',writeback = True)
with open('sentences.dat','r',encoding = 'utf-8') as f:
    for line in f.readlines():
        sentences.append(line)
if not 'names' in db:
    db['names'] = set()
if not 'chatrooms' in db:
    db['chatrooms'] = {}
chatrooms = itchat.get_chatrooms(True)
for cr in chatrooms:
    crDict[cr['UserName']] = cr['NickName']

itchat.run(debug = False,blockThread = False)

print('“六六六”微信六学机器人，指令章口就莱，管理得心应手。输入h获取帮助信息。')
print('>荣耀归于六学家')
while 1:
    cmd = input('>')
    if cmd[0] == 'h':
        print("""指令列表，我从28条记到82条，我太了解他了:
        a(add) [name]:增加新的群聊
        r(remove) [name]:移除现有的群聊。若不加参数则是清空所有群聊。
        l(list):获取当前群聊列表
        q(quit):退出机器人""")
    elif cmd[0] == 'q':
        break
    elif cmd[0] == 'a':
        name = nameCmd(cmd)
        if name != None:
            with lock:
                db['names'].add(name)
            print('俺赚钱了，赚钱了！群[%s]已经添加到列表中。' % (name))            
    elif cmd[0] == 'l':
        print('我加这么多群聊，前后是十七年：')
        with lock:
            for name in db['names']:
                print('\t' + name)
    elif cmd[0] == 'r':
        name = nameCmd(cmd)
        if name != None:
            with lock:
                if not name in db['names']:
                    print('群名，不能戏说恶搞，不能随便翻拍，列表中没这名字。')
                else:
                    db['names'].remove(name)
                    print('假的身份证[%s]已经从列表中移除。' % (name))
        else:
            cmd2 = input('你说你要清空列表，你清空的比我好，你上来试试？输入y清空所有列表，输入其他取消操作：')
            if cmd2 == 'y':
                with lock:
                    db['names'] = set()       
    elif cmd == '荣耀归于六学家':
        print('全国人民心目中只有一个美猴王，你复读我的台词也没用。')
    else:
        print('戏说不是胡说，改编不是乱编，你这样使用未定义的指令，我的眼泪都在肚子里。')

db.close()