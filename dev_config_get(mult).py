from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoAuthenticationException
from datetime import datetime
import pandas
import os
import time
import re
from concurrent.futures import ThreadPoolExecutor,as_completed

def get_dev(row,commands):
    ip = row['ip']
    username = row['username']
    passwd = row['passwd']
    device = {
        'device_type': 'cisco_ios',  # 根据你的设备类型和版本选择合适的类型
        'ip': '{}'.format(ip),  # 设备 IP 地址
        'username': '{}'.format(username),  # 用户名
        'password': '{}'.format(passwd),  # 密码
        'secret': passwd}
    print(f'开始连接{ip}')

    try:
        with ConnectHandler(**device) as connection:
            connection.enable()
            print('{}登录成功，准备收集'.format(ip))
            SN=connection.send_command("show inv")
            SN=SN[SN.find('SN: ')+3:SN.find('DEVID:')].strip('\n')
            #####################开始执行作业cli_part#
            with open(f'{SN}.txt', 'w+', encoding='utf-8') as f:
                print(f'开始记录{ip}/{SN}的信息')
                output=''
                for command in commands:
                    print(f'在{SN}执行命令{command}')
                    prompt = connection.find_prompt()
                    output += '{}{}\n'.format(prompt, command)
                    output += connection.send_command(command, read_timeout=60)
                    output += '\n'
                f.write(output)
    except NetmikoAuthenticationException:
        print('{}登录失败，请检查用户名和密码×'.format(ip))



if __name__ == '__main__':
    #ssh参数########################################
    get_commands = [
        "ping 192.168.1.254",
        "ter len 0",
        "sh ver",
        "show inv",
        "show run",
        "show logg",
        "show ip int b",
        "sh tech-su"
        ]
    max_workers=24
    dev_pd=pandas.read_csv('dev_info.csv')
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        fetures=[executor.submit(get_dev,row,get_commands) for index, row in dev_pd.iterrows()]
        for future in as_completed(fetures):
            result=future.result()
    print('执行完毕')



