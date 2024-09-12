"""
复旦大学研究生抢课程序 - 2024.8
"""
import requests
import threading
import time
import datetime
import re
import json
import os

cnt = 0


def request(ck, classification, course_ids, csrf_token):
    global cnt
    for course_id in course_ids:

        # url = "http://yjsxk.fudan.sh.cn/yjsxkapp/sys/xsxkappfudan/xsxkCourse/choiceCourse.do?_="
        url = "http://" + target + "/yjsxkapp/sys/xsxkappfudan/xsxkCourse/choiceCourse.do?_=" + str(
            int(time.time() * 1000))

        headers = {
            "Cookie": ck.replace("\n", "").strip(),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # response_token = requests.get(url_token, headers=headers)
        # match = re.search(r'id="csrfToken" value=\'([a-f0-9]{32})\'', response_token.text)
        #
        # # 获取匹配到的csrfToken值
        # csrf_token = match.group(1) if match else None

        data = {
            "bjdm": course_id,
            "lx": str(course_classification_dict[classification]),
            "bqmc": classification,
            "csrfToken": csrf_token
        }

        response = requests.post(url, headers=headers, data=data)

        try:
            data = json.loads(response.text)
            if data["code"] == 0:
                cnt += 1
                # print("选课id：{}，状态：{}".format(course_id, data["msg"]))
                if cnt % 20 == 0:
                    print(".", end="")
                if cnt % 1000 == 0:
                    print("")
            else:
                print("\n选课id：{}，提交选课成功，请查看课表，提交时间：{}".format(course_id,
                                                              datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                print("继续抢课", end="")
                return data["code"], course_id
        except Exception as e:
            print("无法提交，请检查ck信息: {}".format(e.__str__()))
            return 0, course_id
    return 0, None


def convert_seconds(s):
    h = int(s // 3600)  # 获取小时数
    m = int((s % 3600) // 60)  # 获取剩余的分钟数
    s = int(s % 60)  # 获取剩余的秒数
    return h, m, s


def wait_until(target_time):
    now = datetime.datetime.now()
    if now > target_time:
        target_time += datetime.timedelta(days=1)

    wait_seconds = (target_time - now).total_seconds()
    hours, minutes, seconds = convert_seconds(wait_seconds)
    print("当前时间：{}, ".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), end="")
    print(f"将在 {hours}小时 {minutes}分 {seconds}秒 后开始抢课")
    time.sleep(wait_seconds)


def main():
    wait_until(start_time)
    print("开始抢课，当前时间：{}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    while True:
        csrf_token = get_csrf_token()

        if csrf_token is None:
            raise RuntimeError("cookies过期")

        for classification_and_course_id in classification_and_course_ids:
            if len(classification_and_course_id) == 1:
                continue
            classification = classification_and_course_id[0]
            course_ids = classification_and_course_id[1:]
            code, course_id = request(ck, classification, course_ids, csrf_token)
            if code == 1:
                # 提交成功
                classification_and_course_id.remove(course_id)
            if len(classification_and_course_id) == 1:
                break
        if all(len(sublist) == 1 for sublist in classification_and_course_ids):
            print("\n抢课结束，当前时间：{}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            break


def get_csrf_token():
    # url_token = "http://yjsxk.fudan.sh.cn/yjsxkapp/sys/xsxkappfudan/xsxkHome/gotoChooseCourse.do"
    url_token = "http://" + target + "/yjsxkapp/sys/xsxkappfudan/xsxkHome/gotoChooseCourse.do"
    headers = {
        "Cookie": ck.replace("\n", "").strip(),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response_token = requests.get(url_token, headers=headers)
    match = re.search(r'id="csrfToken" value=\'([a-f0-9]{32})\'', response_token.text)
    # 获取匹配到的csrfToken值
    csrf_token = match.group(1) if match else None

    if csrf_token is None or csrf_token == "":
        raise RuntimeError("cookies过期")
    return csrf_token


def check_ck():
    while True:
        get_csrf_token()
        time.sleep(60)


def killer(deadline):
    now = datetime.datetime.now()
    if now > deadline:
        deadline += datetime.timedelta(days=1)
    while datetime.datetime.now() < deadline:
        try:
            get_csrf_token()
        except Exception as e:
            print("{}, {}".format(e.__str__(), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            # print(e)
            os._exit(0)
        time.sleep(5)
    print("\n抢课结束，当前时间：{}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    os._exit(0)


if __name__ == "__main__":
    # 提取的Cookies，有效期约3小时
    ck = """
    
_WEU=tGIm0thN5Gwpm89Y2dCzqVJ*hhIq62s2mzYJa09bPkiL_JQJToZR3ISTV4ytif4O; route=2dfce4235a22b1b5497d0314d3a4e42b; JSESSIONID=_37Z_LuzXh2_bK8ivEFvcjk1DOZVW0SgKjnbmXc-Ozee3mJEgChp!165080853; XK_TOKEN=76405885-0a27-4a8e-b02e-f5d3cb1e9a9f

"""
    # 以下课程信息需要手动填入, 第一个课程类别可在以下course_classification_dict变量中找到，后面为课程代码
    classification_and_course_ids = [
        ["第一外国语", "2024202501ENGL731004.12", "2024202501ENGL731004.14"
            , "2024202501ENGL731004.13", "2024202501ENGL731004.04"
            , "2024202501ENGL731004.05", "2024202501ENGL731004.07", "2024202501ENGL731004.08"
            , "2024202501ENGL731004.02", "2024202501ENGL731004.06"
            , "2024202501ENGL731004.27", "2024202501ENGL731004.29", "2024202501ENGL731004.30"
            , "2024202501ENGL731004.23", "2024202501ENGL731004.22", "2024202501ENGL731004.24"
            , "2024202501ENGL731004.25", "2024202501ENGL731004.20", "2024202501ENGL731004.21"
         ],
        ["公共选修课", "20241-003-QEDU733015-1714463254204"]
    ]

    # 定义你希望执行任务的开始时间和结束，例如12:57，最好在抢课时间点的前几分钟，但别提前太早，防止学校服务器压力过大
    start_time = datetime.datetime.now().replace(hour=12, minute=57, second=30, microsecond=0)
    end_time = datetime.datetime.now().replace(hour=13, minute=10, second=30, microsecond=0)

    # 请求的域名会变动，如果发现启动脚本时报cookie过期，那么可以尝试换域名（改这个参数的前提是cookie确实是新获取的，并未真正过期）
    target = "yjsxk.fudan.edu.cn"
    # target = "yjsxk.fudan.sh.cn"

    # 以下信息无需改动，改动上面的信息即可
    course_classification_dict = {"学位基础课": 8, "专业选修课": 8, "学位专业课": 8, "公共选修课": 9, "第一外国语": 7,
                                  "政治理论课": 7, "专业外语": 7}

    threading.Thread(target=killer, args=(end_time,)).start()
    main()
    os._exit(0)
