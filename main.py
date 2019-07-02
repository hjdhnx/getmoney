#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
# File  : main.py
# Author: DaShenHan&道长-----先苦后甜，任凭晚风拂柳颜------
# Date  : 2019/6/30

from comtypes import client
from time import sleep
# from random import randint
lw = client.CreateObject("lw.lwsoft3")
print(lw.ver())  # 打印乐玩版本号
hwnd = 0
bag_pos = (0, 0)
pos_list = []
pic_area = (0, 0, 2000, 2000)
mode = (3, 2, 2, 0, 0)


def getmoney(pos=(-1, -1), thing_name="金子"):
    if pos == (-1, -1):
        print("请传入坐标元组")
    else:
        print(f"{thing_name}的坐标：{pos}")
        abslen = (abs(pos[0] + 10 - 400)**2 + abs(pos[1] + 5 - 268)**2)**0.5
        print(f"{thing_name}中心距人物距离:{round(abslen)}")
        ret = lw.MoveTo(pos[0] + 5, pos[1] + 5)  # 移动到钱中心
        print(f"移动到{thing_name}的位置?{ret==1}")
        if abslen <= 140:
            lw.LeftDown()  # 按住鼠标左键不放
            # lw.EnableRealMouse(1, 20, 30)  # 开启轨迹移动
            global bag_pos
            # lw.MoveR(randint(-10,10),randint(-10,10))#相对随机移动
            lw.MoveTo(bag_pos[0] + 2, bag_pos[1] + 2)  # 移动到背包位置
            sleep(0.2)  # 这个延时必须
            lw.LeftUp()  # 弹起鼠标左键
            lw.KeyPress(13)  # 按下回车键
            sleep(0.2)  # 这个延时必须
            lw.LeftClick()
            sleep(0.3)  # 这个延时必须
        else:
            pos_list.remove(pos)
            print(pos_list)
            walk_len = abslen - 140
            print(f"这个距离的{thing_name}太远了共{abslen}，人物需要走{walk_len}")
            lw.RightDown()
            sleep(0.1 + 0.01 * round(walk_len))
            lw.RightUp()


def findmoney(findthingPath=r"imgs\金子.bmp"):
    ret = lw.FindPicEx(pic_area[0],pic_area[1],pic_area[2],pic_area[3],r"{}".format(findthingPath),"000000",0.8,0)
    if ret is not None:
        thing_name = findthingPath.split("\\")[1].split(".")[0]
        print(f"找到{thing_name}了?", ret is not None)
        ret = ret.split('|')
        global pos_list
        pos_list = []
        for i in ret:
            if (int(i.split(',')[1]) < 1060) and (int(i.split(',')[2]) < 711):
                pos_list.append((int(i.split(',')[1]), int(i.split(',')[2])))
        print(f"发现地上有{thing_name}，坐标列表:{pos_list}")
        for pos in pos_list:
            getmoney(pos, thing_name)


def binwindow(gamename="cool", bagIcoPath=r"imgs\背包.bmp"):
    global hwnd
    hwnd = lw.FindWindow(f"{gamename}","Ultima Online")  # 找指定的游戏窗口句柄
    print('游戏窗口句柄为:', hwnd)  # 打印窗口句柄
    ret = lw.BindWindow(hwnd,mode[0],mode[1],mode[2],mode[3],mode[4])  # 绑定游戏窗口，支持隐藏到边上，不支持最小化
    print(f"{gamename}窗口绑定成功？", ret == 1)
    if ret == 1:  # 如果绑定成功
        ret = lw.findpic(pic_area[0],pic_area[1],pic_area[2],pic_area[3],r"{}".format(bagIcoPath),sim=1)  # 找下背包是否打开状态
        print("找到背包了?", ret == 1)
        if ret != 1:  # 如果背包没打开就开始点击打开背包再循环判断背包是否打开
            while True:
                print("没找到我的背包，接下来双击两下人物再找。")
                lw.MoveTo(400, 268)  # 移动到游戏客户端中心，人物位置
                lw.LeftDoubleClick()
                # lw.LeftDoubleClick()
                # 执行两次连续双击人物，因为一次好像点不出来背包
                ret = lw.findpic(pic_area[0],pic_area[1],pic_area[2],pic_area[3],r"{}".format(bagIcoPath),sim=1)
                if ret == 1:
                    print("找到了我的背包")
                    break  # 找到背包跳出循环
        x = int(lw.x())
        y = int(lw.y())
        print(f"背包坐标：{x},{y}")  # 打印背包坐标
        global bag_pos
        if "背包.bmp" in bagIcoPath:
            bag_pos = (x + 15, y + 15)  # 坐标偏移后加入元组，后面非人为操作不会影响背包的位置
        else:
            bag_pos = (x + 5, y + 5)  # 坐标偏移后加入元组，后面非人为操作不会影响背包的位置


def unbinwindow():
    lw.UnBindWindow()


def count_time(lens):
    step = lens // 45  # 总共需要走多少步
    rego = step * 45  # 实际走的路程
    sy = lens % 45  # 余数，走了后还有多远
    time = 0.2
    if step > 1 and sy <= 22.5:
        time = step * 0.5 - 0.8  # 按下后需要延迟的时间
        print(f"离走的距离{lens}还差{sy}，少走半步")
    elif step >= 1 and sy >= 22.5:
        time = step * 0.5 - 0.3  # 按下后需要延迟的时间
        print(f"离走的距离{lens}还差{sy}，多走半步")
        step += 1
        rego += 45
        sy -= 45
    elif sy >= 22.5:
        sy -= 45
        step += 1
        rego += 45
        time = step * 0.5 - 0.1  # 按下后需要延迟的时间
        print(f"离走的距离{lens}还差{sy}，多走半步")
    return (time, step, rego, sy)


def go(way, lens):
    pas = 30
    way_ditc = {"s": (0, pas), "n": (0, -pas), "se": (pas, 2 * pas), "ne": (pas, 0),"nw": (-pas, -pas), "w": (-pas, pas), "sw": (-pas, 2 * pas), "e": (pas, pas)}
    way_pos = way_ditc[way]
    lw.MoveTo(400 + way_pos[0], 268 + way_pos[1])
    # 一步走45码
    lw.RightDown()
    ret = count_time(lens)
    sleep(ret[0])  # 每0.5秒走一步。千万别跑
    lw.RightUp()
    return (ret[1], ret[2], ret[3])


def goes(rx, ry):
    retx = (0, 0, 0)
    rety = (0, 0, 0)
    if rx > 0:
        retx = go("e", abs(rx))
        # print(f"向右走{abs(rx)}")
    if rx < 0:
        retx = go('w', abs(rx))
        # print(f"向左走{abs(rx)}")
    if ry > 0:
        rety = go('s', abs(ry))
        # print(f"向上走{abs(rx)}")
    if ry < 0:
        rety = go("n", abs(ry))
        # print(f"向下走{abs(rx)}")
    return (retx, rety)


def goto(pos):
    now = (400, 268)
    rx = pos[0] - now[0]
    ry = pos[1] - now[1]
    ret = goes(rx, ry)
    return ret


def getthings():
    binwindow(gamename="xhe.cool", bagIcoPath=r"imgs\金箱子.bmp")
    while True:
        findmoney(r"imgs\金子.bmp")
        # findmoney(r"imgs\木材1.bmp")
        sleep(2)


def getthings_shiti():
    while True:
        ret = lw.findpic(pic_area[0],pic_area[1],pic_area[2],pic_area[3],r"imgs\尸体背包.bmp",sim=1)
        if ret == 1:
            findmoney(r"imgs\金子.bmp")
            # findmoney(r"imgs\木材1.bmp")
            sleep(2)

def walk(dire, steps=1):
    way = {"上": 38, "下": 40, "左": 37, "右": 39}
    for i in range(steps):
        lw.KeyPress(way[dire])


def findtree():
    treelist = [r"imgs\伞树.bmp",r"imgs\伞树2.bmp",r"imgs\针树.bmp",r"imgs\针树2.bmp",r"imgs\鸟树.bmp",r"imgs\高脚树.bmp"]
    todo = []
    for i in treelist:
        ret = lw.FindPicEx(pic_area[0],pic_area[1],pic_area[2],pic_area[3],i, "000000",0.8,0)
        if ret is not None:
            print(f"{i}:  {ret}")
            ret = ret.split('|')
            for i in ret:
                ok = i.split(',')
                todo.append((int(ok[1]), int(ok[2])))
    print(todo)
    now = (400, 268)
    for i in todo:
        rx = i[0] - now[0]
        ry = i[1] - now[1]
        if rx < 0:
            a = (abs(rx) %45 // 22.5) * (abs(rx) %45) + abs(rx) // 45 * 45  # 计算得到实际负偏移
            b = 0
            if ry < 0:
                b = (abs(ry) %45 // 22.5) * (abs(ry) %45) + abs(ry) // 45 * 45  # 计算得到实际负偏移
                now = [now[0] - a, now[1] - b]
            elif ry > 0:
                b = (ry % 45 // 22.5) * (ry % 45) + ry // 45 * 45  # 计算得到实际正偏移
                now = [now[0] - a, now[1] + b]
        elif rx > 0:
            a = (abs(rx) %45 // 22.5) * (abs(rx) %45) + abs(rx) // 45 * 45  # 计算得到实际正偏移
            if ry < 0:
                b = (abs(ry) %45 // 22.5) * (abs(ry) %45) + abs(ry) // 45 * 45  # 计算得到实际负偏移
                now = [now[0] + a, now[1] - b]
            elif ry > 0:
                b = (ry % 45 // 22.5) * (ry % 45) + ry // 45 * 45  # 计算得到实际正偏移
                now = [now[0] + a, now[1] + b]
        print(f"走路后坐标:{now}")
        ret = goes(rx, ry)
        print(ret)
        sleep(1)


if __name__ == '__main__':
    binwindow(gamename="xhe.cool", bagIcoPath=r"imgs\金箱子.bmp")
    # getthings_shiti()  调用捡尸体东西函数
    # walk("左", 4)
    getthings()
