import json
import time
from TrafficQuery import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPAuthenticationError, SMTPException
import ssl
import traceback



# 通过result的状态判断是否登录成功，1表示成功，0表示失败
def judgeLogin(response_text: str):
    # 提取 JSON 部分
    json_startIndex = response_text.find("{")
    json_endIndex = response_text.rfind("}")
    json_data = response_text[json_startIndex:json_endIndex + 1]
    # 解析json
    data = json.loads(json_data)
    # 判断结果
    if data.get("result") == 1:
        # 登陆成功
        return True
    elif data.get("result") == 0:
        # 登陆失败
        print("登录失败,密码错误")
        return False
    else:
        # 异常情况
        print(f"登陆失败,异常情况")
        print(f"result={data.get('result')}")
        return False


# 登录校园网
def login(account: str, password: str):
    loginurl = "http://10.0.1.5/drcom/login"
    # 产生一个3000~8000的随机数作为参数
    num = random.randint(3000, 9000)
    # GET http://10.0.1.5/drcom/login?callback=dr1003&DDDDD=23032300001&upass=12345678&0MKKey=123456&R1=0&R2=&R3=0&R6=0&para=00&v6ip=&terminal_type=1&lang=zh-cn&jsVersion=4.2&v=2013&lang=zh
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Referer": "http://10.0.1.5/chkuser?url=www.163.com/",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    params = {"callback": "dr1003",
              "DDDDD": account,
              "upass": password,
              "0MKKey": "123456",
              "R1": "0",
              "R2": "",
              "R3": "0",
              "R6": "0",
              "para": "00",
              "v6ip": "",
              "terminal_type": "1",
              "lang": "zh-cn",
              "jsVersion": "4.2",
              "v": str(num)
              }
    try:
        response = requests.get(url=loginurl, params=params, headers=headers)
        response_text = response.text
        if judgeLogin(response_text):
            # print(f"登陆成功\n")
            return True
        else:
            print(f"response_text.status_code = {response_text.status_code}")
            return False
    except requests.RequestException as e:
        print(e)
        return False


# 将查询到的剩余流量从M转化为G
def convert(input: str):
    input = int(input.replace("M", ""))
    # 把M换算成G
    convert = input / 1024
    convert_round = round(convert, 2)
    # print(convert_round)
    return convert_round

def execute():
    # 记录查询次数
    count = 1
    # 从第一个账号开始判断
    login("18003*****", "******")
    login_time = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
    pri = f"{login_time} 已登录初始用户'**'"
    with open("/root/currentUser.txt", "a") as log_file:
        log_file.write(pri + "\n")
    try:
        # 所有人的流量信息
        traffic_summary = return_check_result("/root/student_information.txt")
    except Exception as e:
        find_all_exception = f"查询所有用户流量时出现异常:{e}"
        with open("/root/currentUser.txt", "a") as log_file:
            log_file.write(find_all_exception + "\n")
    # 从第一个账号开始使用流量
    current_using = 0
    # 日志文件路径
    # log_file_path = "C:\\Users\\LHF\\Desktop\\currentUser.txt"
    log_file_path = "/root/currentUser.txt"
    # for item in traffic_summary:
    #     print(item)

    while True:
        try:
            # 未超出可用名单且流量还没达到15G，就十分钟后重新检查
            if current_using <= len(traffic_summary) - 1 and convert(traffic_summary[current_using][3]) < 15.0:
                current_time = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                tf = TrafficQuery(account=traffic_summary[current_using][1], password=traffic_summary[current_using][2])
                used = tf.run()
                traffic_summary[current_using][3] = used
                update_msg = f"{current_time} 用户{traffic_summary[current_using][0]}已用流量更新为{traffic_summary[current_using][3]}"
                with open("/root/updateTraffic.txt", "a") as log_file:
                    log_file.write(update_msg + "\n")
                used = convert(used)
                message = f"{current_time} 第{count}次查询,当前用户为 {traffic_summary[current_using][0]}, 校园网账号为 {traffic_summary[current_using][1]}, 已用流量 {used}G"
                # print(message)
                with open(log_file_path, "a") as log_file:
                    log_file.write(message + "\n")
                time.sleep(600)
                count += 1
            # 大于15G小于20G时则五分钟更新一次
            elif current_using <= len(traffic_summary) - 1 and convert(traffic_summary[current_using][3]) > 15.0 and convert(traffic_summary[current_using][3]) < 20.0:
                current_time = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                tf = TrafficQuery(account=traffic_summary[current_using][1], password=traffic_summary[current_using][2])
                used = tf.run()
                traffic_summary[current_using][3] = used
                update_msg = f"{current_time} 用户{traffic_summary[current_using][0]}已用流量更新为{traffic_summary[current_using][3]}"
                with open("/root/updateTraffic.txt", "a") as log_file:
                    log_file.write(update_msg + "\n")
                used = convert(used)
                message = f"{current_time} 第{count}次查询;当前用户为:{traffic_summary[current_using][0]};账号:{traffic_summary[current_using][1]};已用流量 {used}G"
                # print(message)
                with open(log_file_path, "a") as log_file:
                    log_file.write(message + "\n")
                time.sleep(300)
                count += 1
            # 当前用户已用完20G流量，切换到下一用户
            elif (current_using < len(traffic_summary) - 1) and convert(traffic_summary[current_using][3]) > 20.0:
                current_using += 1
                login(account=traffic_summary[current_using][1], password=traffic_summary[current_using][2])
                used = convert(traffic_summary[current_using][3])
                message = (f"{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())} {traffic_summary[current_using - 1][0]}流量已用尽,共使用{convert(traffic_summary[current_using - 1][3])}G\n "
                           f"切换到用户:{traffic_summary[current_using][0]},已用流量 {used}G")
                # print(message)
                with open(log_file_path, "a") as log_file:
                    log_file.write(message + "\n")
            # 出现特殊情况，直接跳到下一个
            else:
                current_using += 1
                login(account=traffic_summary[current_using][1], password=traffic_summary[current_using][2])
                used = convert(traffic_summary[current_using][3])
                message = f"{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())} 出现意料之外的情况，直接切换到下一用户 {traffic_summary[current_using][0]}, 已用流量 {used}G"
                print(message)
                with open(log_file_path, "a") as log_file:
                    log_file.write(message + "\n")
        # 异常处理
        except Exception as e:
            error_msg = f"程序出现异常: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())  # 导入 traceback 模块
            with open("/root/currentUser.txt", "a") as log_file:
                log_file.write(error_msg + "\n")
            send_mail(exception_msg=error_msg)
            # 异常后过5分钟重新启动函数
            time.sleep(300)
            continue

# 出现异常发送通知邮件
def send_mail(exception_msg):
    # 配置SMTP服务器的信息
    smtp_server = "smtp.163.com"
    smtp_port = 465
    # 换成自己的发送邮箱地址，用来发邮件
    sender_email = "*******@163.com"
    # 换成自己的发送邮箱地址，用来接受邮件
    receiver_email = "********@qq.com"
    # 可以到邮箱设置里面找
    password = "******"

    # 构建邮件内容
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "实验室OpenWrt程序异常通知"
    body = f"程序执行时出现异常：\n\n{exception_msg}"
    message.attach(MIMEText(body, "plain"))

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())  # 发送邮件
        print("邮件发送成功！")
    except SMTPAuthenticationError:
        print("登录失败，用户名或密码错误。")
    except SMTPException as e:
        print("邮件发送失败:", e)


if __name__ == "__main__":
    execute()
