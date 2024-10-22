# Openwrt-Campus-Network脚本
在OpenWrt小主机上跑的一个python程序，主要用来摆脱校园网个人账号的流量使用限制  
**宿舍小主机配置**：J1800 + 4G RAM + 64G ROM  
**实验室小主机配置**：J1900 + 8G RAM +64G ROM  
## py程序主要功能
1.**实时监测每个校园网账号的流量使用情况**：未用到15GB之前，每10分钟检测一次当前账号已用流量；15GB~20GB之间，每5分钟检测一次已用流量  
2.**自动切换校园网账号**：从第一个校园网账号开始使用，每个账号用到20GB流量之后会自动切换到下一个账号,以便能够继续使用高速校园网流量  
+ 本科生每月不限速流量:20GB
+ 研究生每月不限速流量:30GB  
3.**批量检测校园网账号流量使用情况**：导入已有的校园网账号名单，自动检测每个账号当月的流量使用情况，用**TXT文件**保存名单，每个账号信息占一行  
**名单示例如下：**  
姓名	 学号	       密码  
张三  1000300801	123456  
李四  1100300811	789456  
......  
**返回结果示例如下:**  
姓名	  学号	     密码   已用流量  
张三  1000300801	123456  10867M  
李四  1100300811	789456  123456M  
## 使用脚本程序前提条件  
1.拥有一批可以自由支配的校园网账号  
2.有相应的软路由硬件，并在openwrt小主机上安装好需要的python第三方库   
bs4                0.0.2  
pip                24.0  
requests           2.31.0  
3.通过邮件通知用户流量使用情况和异常情况，最好是用两个不同的邮箱(我使用了QQ邮箱163邮箱)，然后在邮箱设置处开启POP3/SMTP服务并获取密钥Token  
4.在小主机上提前创建好相应的校园网账号`TXT文件`，我选择把账号信息文件放在`/root`目录下，手动创建1~4，除了`student_information.txt`要包含校园网账号名单，另外三个都是空文件  
![image](https://github.com/2819685584/Openwrt-Campus-Network/assets/87923345/95ba5f97-c79b-4737-bd77-0da047863790)  
5.在openwrt小主机上写入开机自启动脚本命令  
![image](https://github.com/2819685584/Openwrt-Campus-Network/assets/87923345/f8b3598a-1727-4d6e-b482-bfc5df05fe8c)  
6.在小主机上新建脚本文件`/root/autolog.sh`，写入如下内容：  
```
#!/bin/sh
nohup python3 /root/login.py &
```
7.新建`TrafficQuery.py`和`login.py`文件，然后把相应代码复制进去
## 执行脚本
手动执行：直接输入如下命令：  
`bash autolog.sh`  
自动执行：每次小主机启动时都会自动执行`bash autolog.sh`，但是有可能失灵，可以多重启两次试试  





