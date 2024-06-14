import requests
import re
import time
import random
import os


# 进度可视化(进度条)
def print_progress_bar(completed, total, length=50):
    progress = int(length * completed / total)
    bar = '[' + '=' * progress + '-' * (length - progress) + ']'

    if completed/total < 0.35:
        color = '31'  # 红色
    elif completed/total < 0.7:
        color = '33'  # 黄色
    else:
        color = '32'  # 绿色

    bar = f"\033[{color}m{bar}\033[0m"  # \033[0m 重置颜色

    # 打印进度条
    print(f'\r{bar} {completed+1}/{total}', end='')


# 短睡眠
def sleep_short():
    time.sleep(random.uniform(0.3, 1.5))


# 长睡眠(默认短睡眠，如需长睡眠请手动更改)
def sleep_long():
    time.sleep(random.uniform(1.5, 5))


sleep = sleep_short


def crawler(title, cookie):

    # 主页面
    url_main = "https://tyutr.alphacoding.cn/task"

    # 请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome"
                      "/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
        "Cookie": cookie
        }

    # 请求题库所在主页面
    resp_main = requests.get(url_main, headers=headers)

    url_ID = ("https://tyutr.alphacoding.cn/api/learning/v4/tasks/my?"
              "types=exercise,lesson,project&status=undone&limit=10&skip=0")

    # 获得子url所需的ID和lessonPath
    resp_problem = requests.get(url_ID, headers=headers)

    problem_content = resp_problem.text

    # 题库页面分为已完成与未完成，默认请求未完成的库，若已完成则会自动切换
    if title not in resp_problem.text:
        url_ID = ("https://tyutr.alphacoding.cn/api/learning/v4/tasks/my?"
                  "types=exercise,lesson,project&status=done&limit=10&skip=0")
        resp_problem = requests.get(url_ID, headers=headers)
        problem_content = resp_problem.text

    # 获取Path中的courseID、taskID与titleID所在字块
    if title == "编程题练习库":
        ID_content = re.search(r'"courseId":(?P<courseID>.\d+),"taskId":(?P<taskID>\d+),"title":"编程题练习库"',
                               problem_content)
        Path_content = re.findall(r'"title":"编程题练习库",.*?({.*?]),', problem_content)
    elif title == "程序设计题练习库":
        ID_content = re.search(r'"courseId":(?P<courseID>.\d+),"taskId":(?P<taskID>\d+),"title":"程序设计题练习库"',
                               problem_content)
        Path_content = re.findall(r'"title":"程序设计题练习库",.*?({.*?]),', problem_content)
    elif title == "填空题练习库":
        ID_content = re.search(r'"courseId":(?P<courseID>.\d+),"taskId":(?P<taskID>\d+),"title":"填空题练习库"',
                               problem_content)
        Path_content = re.findall(r'"title":"填空题练习库",.*?({.*?]),', problem_content)

    elif title == "程序填空题练习库":
        ID_content = re.search(r'"courseId":(?P<courseID>.\d+),"taskId":(?P<taskID>\d+),"title":"程序填空题练习库"',
                               problem_content)
        Path_content = re.findall(r'"title":"程序填空题练习库",.*?({.*?]),', problem_content)
    elif title == "判断题练习题":
        ID_content = re.search(r'"courseId":(?P<courseID>.\d+),"taskId":(?P<taskID>\d+),"title":"判断题练习题"',
                               problem_content)
        Path_content = re.findall(r'"title":"判断题练习题",.*?({.*?]),', problem_content)
    elif title == "单选题练习库":
        ID_content = re.search(r'"courseId":(?P<courseID>.\d+),"taskId":(?P<taskID>\d+),"title":"单选题练习库"',
                               problem_content)
        Path_content = re.findall(r'"title":"单选题练习库",.*?({.*?]),', problem_content)
    else:
        print("Error!")

    # 获取Path中的courseID和taskID
    courseID = ID_content.group("courseID")
    taskID = ID_content.group("taskID")

    # 获取titleID
    Path_list = re.findall(r'"title":.*?"lessonPath":"(?P<ID>.*?)"', Path_content[0], re.S)

    # 总进度
    total_steps = len(list(Path_list))

    # 请求题目页面
    for titleID in list(Path_list):
        # url = "https://tyutr.alphacoding.cn/api/learning/v4/exercises/[courseID]/[titleID]/info?taskId=[taskID]"
        url = "https://tyutr.alphacoding.cn/api/learning/v4/exercises/"+courseID+"/"+titleID+"/info?taskId="+taskID

        # 休眠防止被ban
        sleep()
        resp = requests.get(url, headers=headers)

        if title == "编程题练习库":
            # 获取题目内容
            content = re.search(r'"title":"(?P<title>.*?)".*?"question":"(?P<question>.*?)".*?"codeSolution":"(?P<solution>.*?)","checkUserContext"',
                                resp.text, re.S)

            # 将原始str还原成非原始str
            question = (content.group("question")
                        .encode('latin1', 'backslashreplace')
                        .decode('unicode_escape', errors="ignore"))
            solution = (content.group("solution")
                        .encode('latin1', 'backslashreplace')
                        .decode('unicode_escape', errors="ignore"))

            # 写入题目
            os.makedirs('CodeQuestion', exist_ok=True)
            with open(f'./CodeQuestion/{content.group("title")}.md', 'w') as file:
                print(question, file=file)
                print("\n**答案**：\n", file=file)
                print("```python", file=file)
                print(solution, file=file)
                print("```", file=file)

                file.flush()

        elif title == "程序设计题练习库":
            # 获取题目内容
            content = re.search(r'"title":"(?P<title>.*?)".*?"question":"(?P<question>.*?)".*?"codeSolution":"(?P<solution>.*?)","checkUserContext"',
                                resp.text, re.S)

            # 将原始str还原成非原始str
            question = (content.group("question")
                        .encode('latin1', 'backslashreplace')
                        .decode('unicode_escape', errors="ignore"))
            solution = (content.group("solution")
                        .encode('latin1', 'backslashreplace')
                        .decode('unicode_escape', errors="ignore"))

            # 写入题目
            os.makedirs('ProgressDesign', exist_ok=True)
            with open(f'./ProgressDesign/{content.group("title")}.md', 'w') as file:
                print(question, file=file)
                print("\n**答案**：\n", file=file)
                print("```python", file=file)
                print(solution, file=file)
                print("```", file=file)

                file.flush()

        elif title == "程序填空题练习库":
            content = re.search(
                r'"title":"(?P<title>.*?)".*?"question":"(?P<question>.*?)".*?"fillContent":"(?P<fill>.*?)",.*?"fillSourceCode":"(?P<answer>.*?)",',
                resp.text, re.S)

            # 将原始str还原成非原始str
            question = (content.group("question")
                        .encode('latin1', 'backslashreplace')
                        .decode('unicode_escape', errors="ignore"))
            fill = (content.group("fill")
                        .encode('latin1', 'backslashreplace')
                        .decode('unicode_escape', errors="ignore"))
            answer = (content.group("answer")
                        .encode('latin1', 'backslashreplace')
                        .decode('unicode_escape', errors="ignore"))


            # 写入题目
            os.makedirs('CodeCompletion', exist_ok=True)
            with open(f'./CodeCompletion/{content.group("title")}.md', 'w') as file:
                print(question, file=file)
                print("\n**填空处**：\n", file=file)
                print("```python", file=file)
                print(fill, file=file)
                print("```", file=file)
                print("\n**答案**：\n", file=file)
                print("```python\n", file=file)
                print(answer, file=file)
                print("\n```", file=file)

                file.flush()

        elif title == "填空题练习库":

            content = re.search(
                r'"title":"(?P<title>.*?)".*?"question":"(?P<question>.*?)".*?"fillContent":"(?P<fill>.*?)",.*?"matchRule":"(?P<answer>.*?)"',
                resp.text, re.S)

            # 将原始str还原成非原始str
            question = (content.group("question")
                        .encode('latin1', 'backslashreplace')
                        .decode('unicode_escape', errors="ignore"))
            fill = (content.group("fill")
                        .encode('latin1', 'backslashreplace')
                        .decode('unicode_escape', errors="ignore"))

            answer = (content.group("answer")
                        .encode('latin1', 'backslashreplace')
                        .decode('unicode_escape', errors="ignore"))

            # 写入题目
            os.makedirs('Completion', exist_ok=True)
            with open(f'./Completion/{content.group("title")}.md', 'w') as file:
                print(question, file=file)
                print("\n**填空处(代码请无视)**：\n", file=file)
                print("```python", file=file)
                print(fill, file=file)
                print("```", file=file)
                print("\n**答案**：\n", file=file)
                print(answer, file=file)

                file.flush()

        elif title == "单选题练习库":
            content = re.search(
                r'"title":"(?P<title>.*?)".*?"question":"(?P<question>.*?)".*?"options":.*?"option":'
                r'"(?P<option1>.*?)"(?P<answer1>.*?)"option":"(?P<option2>.*?)"(?P<answer2>.*?)"option":'
                r'"(?P<option3>.*?)"(?P<answer3>.*?)"option":"(?P<option4>.*?)"(?P<answer4>.*?)}',
                resp.text, re.S)

            # 将原始str还原成非原始str
            question = (content.group("question")
                        .encode('latin1', 'backslashreplace')
                        .decode('unicode_escape', errors="ignore"))
            option1 = (content.group("option1")
                        .encode('latin1', 'backslashreplace')
                        .decode('unicode_escape', errors="ignore"))
            option2 = (content.group("option2")
                        .encode('latin1', 'backslashreplace')
                        .decode('unicode_escape', errors="ignore"))
            option3 = (content.group("option3")
                        .encode('latin1', 'backslashreplace')
                        .decode('unicode_escape', errors="ignore"))
            option4 = (content.group("option4")
                        .encode('latin1', 'backslashreplace')
                        .decode('unicode_escape', errors="ignore"))

            if '"isCorrect":true' in content.group("answer1"):
                answer = 'A'
            elif '"isCorrect":true' in content.group("answer2"):
                answer = 'B'
            elif '"isCorrect":true' in content.group("answer3"):
                answer = 'C'
            elif '"isCorrect":true' in content.group("answer4"):
                answer = 'D'
            else:
                answer = 'Error!'

            # 写入题目
            os.makedirs('MultipleChoice', exist_ok=True)
            with open(f'./MultipleChoice/{content.group("title")}.md', 'w') as file:
                print(question, file=file)
                print("\n**选项**：\n", file=file)
                print("A:", option1, '\n', sep=' ', file=file)
                print("B:", option2, '\n', sep=' ', file=file)
                print("C:", option3, '\n', sep=' ', file=file)
                print("D:", option4, '\n', sep=' ', file=file)
                print("\n**答案**：\n", file=file)
                print(answer, file=file)

                file.flush()

        elif title == "判断题练习题":
            content = re.search(
                r'"title":"(?P<title>.*?)".*?"question":"(?P<question>.*?)".*?"options":'
                r'.*?"option":"(?P<option>.*?)".*?"isCorrect":(?P<answer>false|true)',
                resp.text, re.S)

            # 判断答案
            question = (content.group("question")
                        .encode('latin1', 'backslashreplace')
                        .decode('unicode_escape', errors="ignore"))
            if content.group("answer") is True or content.group("answer") == 'true':
                answer = content.group("option")
            else:
                if content.group("option") == "正确":
                    answer = "错误"
                else:
                    answer = "正确"

            # 写入题目
            os.makedirs('TrueFalse', exist_ok=True)
            with open(f'./TrueFalse/{content.group("title")}.md', 'w') as file:
                print(question, file=file)
                print("\n**答案**：\n", file=file)
                print(answer, file=file)

                file.flush()

        # 进度可视化
        print_progress_bar(list(Path_list).index(titleID), total_steps)
        # 关闭响应卡
        resp.close()

    # 关闭主页面响应卡
    resp_problem.close()


def main():
    # 选择库
    choice_dict = {
        "1": "编程题练习库",
        "2": "程序填空题练习库",
        "3": "填空题练习库",
        "4": "程序设计题练习库",
        "5": "单选题练习库",
        "6": "判断题练习题",
    }

    flag = True
    cflag = True
    while flag:
        # 初始化界面
        print("-"*50)
        print("欢迎使用tyutAlpha平台题目爬取！")
        print("1. 编程题练习库        2. 程序填空题练习库")
        print("3. 填空题练习库        4. 程序设计题练习库")
        print("5. 单选题练习库        6. 判断题练习题")
        print("0: 退出")
        choice = input("请输入你的选择(数字)：")
        while choice[0] not in "1234560":
            print("请输入一个合理的值!")
            choice = input("请输入你的选择(数字)：")

        if choice[0] == '0':
            break

        # 重复使用时免除多次cookie提示
        if cflag:
            cookie = input("请输入你的Cookie(错误输入将导致无法正常运行):")
            cflag = False

        print("-"*50)

        # 爬取题目
        crawler(title=choice_dict[choice[0]], cookie=cookie)
        print("\n爬取完成！")

        inp = input("是否继续爬取?(y/n):")
        if inp[0] == 'y' or inp[0] == 'Y':
            flag = True
        else:
            flag = False

    print("欢迎下次使用！")


if __name__ == '__main__':
    main()
