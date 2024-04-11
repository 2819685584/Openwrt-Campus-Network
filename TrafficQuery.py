import requests
import sys
import hashlib
import random
from bs4 import BeautifulSoup
import datetime


class TrafficQuery:
    # 第一次发送GET请求的header
    headers_1 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document'
    }

    # 发送POST请求的header
    headers_2 = {
        'Host': 'nicdrcom.guet.edu.cn',
        'Connection': 'keep-alive',
        'Content-Length': '91',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Microsoft Edge";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Upgrade-Insecure-Requests': '1',
        'Origin': 'https://nicdrcom.guet.edu.cn',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://nicdrcom.guet.edu.cn/Self/login/?302=LI',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
    }

    # 请求dashboard的header
    headers_3 = {
        'Host': 'nicdrcom.guet.edu.cn',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'sec-ch-ua': '"Microsoft Edge";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
    }

    # 用户自助服务系统Web-URL
    url_1 = "https://nicdrcom.guet.edu.cn/Self/login/?302=LI"
    # 伪造16位小数randomCode的URL 需加上伪造的t使用  没有这一步会登陆不了
    url_2 = "https://nicdrcom.guet.edu.cn/Self/login/randomCode?t="
    # 发送POST请求的URL 需加上sessionid使用
    url_3 = "https://nicdrcom.guet.edu.cn/Self/login/verify;jsessionid="
    # dashboard的URL
    url_4 = "https://nicdrcom.guet.edu.cn/Self/dashboard"

    def __init__(self, account: str, password: str):
        self.account = account
        self.password = password
        self.session = requests.session()

    # 第一次GET请求的结果
    def getFirstResponse(self):
        response = self.session.get(url=self.url_1, headers=self.headers_1)
        return response

    # 第二次请求，解决验证码
    def getSecondRequest(self, random_T):
        url_2 = self.url_2 + random_T
        # print(url_2)
        self.session.get(url=url_2)

    # 第三次POST请求,发送登录信息
    def getThirdRequest(self, Cookie, md5_password, checkcode):
        url_3 = self.url_3 + Cookie
        # print(url_3)
        # 定义请求体
        data = {
            "foo": "",
            "bar": "",
            "checkcode": checkcode,
            "account": self.account,
            "password": md5_password,
            "code": ""
        }
        self.session.post(url=url_3, headers=self.headers_2, data=data)

    # 第四次请求，获取仪表盘信息并返回HTML
    def getForthRequest(self):
        result_html = self.session.get(url=self.url_4, headers=self.headers_3, allow_redirects=True)
        return result_html.text

    # 获取Cookie，cookie原来的样式是{JSESSIONID=AA492264B02C08023B0B23800F11E667}
    # 这里只需要获取"AA492264B02C08023B0B23800F11E667"部分把他拼接到url_2后面构成完整请求
    def getCookie(self, response):
        if response.headers.get("Set-Cookie"):
            Cookie = response.headers.get("Set-Cookie").replace("JSESSIONID=", "").replace("; Path=/Self; HttpOnly", "")
            # print(Cookie)
        else:
            print("Cookie未找到，终止程序")
            sys.exit()
        return Cookie

    # 获取隐藏在HTML中的checkcode
    # openwrt不支持etree解析xpath，只能用bs4 or 正则表达式
    def getCheckcode(self, response):
        response_text = response.text
        soup = BeautifulSoup(response_text, features='html.parser')
        # 找到所有name为 checkcode 的 input 元素
        checkcode_inputs = soup.select('input[name=checkcode]')
        # 打印每个找到的元素的值
        for input_element in checkcode_inputs:
            checkcode = input_element['value']
            # print("checkcode = " + input_element['value'])
            break
        return checkcode

    # 随机生成randomCode，像这样子的{t=0.6189532606303612}
    # 好像是跟验证码有关的，没有这个请求会被重定向到登陆页面
    def getrRandom_t(self):
        # 生成小数点后的第一位和最后一位数字，保证它们不为0
        first_digit = random.randint(1, 9)
        last_digit = random.randint(1, 9)
        # 生成中间的随机数字字符串
        middle_digits = ''.join([str(random.randint(0, 9)) for _ in range(14)])
        # 组合所有部分
        random_T = f"0.{first_digit}{middle_digits}{last_digit}"
        return random_T

    # 把密码加密成32位小写md5值
    def md5_password(self):
        # 创建 MD5 对象
        md5 = hashlib.md5()
        # 将字符串转换为字节对象并更新 MD5 对象
        md5.update(self.password.encode())
        # 获取 MD5 值（32位小写散列值）
        md5_password = md5.hexdigest()
        # 返回结果
        return md5_password

    # 解析HTML获取每一个人对应页面的已用流量
    def parseResult(self, result_html):
        # 创建Beautiful Soup解析器对象
        soup = BeautifulSoup(result_html, 'html.parser')
        # 找到第一个 <dt> 标签的内容并打印
        first_dt_tag = soup.find('dt')
        dt_text = 0
        if first_dt_tag:
            # 解析HTML得到已用流量
            dt_text = first_dt_tag.get_text(strip=True)
            # print(dt_text)
            return dt_text

    def run(self):
        response = self.getFirstResponse()
        cookie = self.getCookie(response)
        checkcode = self.getCheckcode(response)
        random_T = self.getrRandom_t()
        md5_password = self.md5_password()
        self.getSecondRequest(random_T=random_T)
        self.getThirdRequest(Cookie=cookie, md5_password=md5_password, checkcode=checkcode)
        result_html = self.getForthRequest()
        used = self.parseResult(result_html=result_html)
        return used


# Windows下学生名单路径："C:\\Users\\LHF\\Desktop\\账号信息.txt"
def return_check_result(student_list_path):
    # 打开文本文件并读取内容
    with open(student_list_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    # 提取每行信息并存储在列表中
    account_info = []
    # 从第二行开始提取
    for line in lines[1:]:
        # 使用制表符分割每行内容
        parts = line.strip().split("\t")
        # 确保分割之后每行有三个字段
        if len(parts) == 3:
            account_info.append(parts)

    # 打印存储的账号信息列表
    # print("账号信息：")
    # for info in account_info:
    #     print(info)

    # 在循环中检查账号和密码，并将结果添加到每行信息的末尾
    for info in account_info:
        account = info[1]  # 学号作为账号
        password = info[2]  # 密码
        tf = TrafficQuery(account, password)
        used = tf.run()
        # 将结果添加到每行信息的末尾
        info.append(used)
    return account_info


# 保存查询结果到文件中作为日志
# Windows下为:"C:\\Users\\LHF\\Desktop\\查询结果.txt"
# Linux下为:"/root/log.txt
def save_check_result(save_path,account_info):
    # 获取当前的年月日时分秒
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 将新获取的 account_info 追加到文件末尾
    with open(save_path, "a", encoding="utf-8") as file:
        # 写入当前时间
        file.write(current_datetime + "\n")
        # 写入分隔线
        file.write("--------------------\n")
        # 写入更新后的信息
        for info in account_info:
            file.write("\t".join(info) + "\n")


if __name__ == '__main__':
    # account_info = return_check_result(student_list_path="C:\\Users\LHF\Desktop\\账号信息.txt")
    # save_check_result(save_path="C:\\Users\\LHF\Desktop\\查询结果.txt",account_info=account_info)
    result = return_check_result(student_list_path="/root/student_information.txt")
    save_check_result(save_path="/root/checkresult.txt", account_info=result)
