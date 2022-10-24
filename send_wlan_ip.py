#! /usr/bin/python

import os
import requests
import time
import logging
from rich.console import Console


logging.basicConfig(level=logging.DEBUG #设置日志输出格式
                    ,filename="/home/yammi/Documents/codes/internal_SendWlanIP.log" #log日志输出的文件位置和文件名
                    ,filemode="a" #文件的写入格式，w为重新写入文件，默认是追加
                    ,format="%(asctime)s - %(name)s - %(levelname)-9s - %(filename)-8s : %(lineno)s line - %(message)s" #日志输出的格式
                    # -8表示占位符，让输出左对齐，输出长度都为8位
                    ,datefmt="%Y-%m-%d %H:%M:%S" #时间输出的格式
                    )

def run_shell_get_wlan_ip():
	r = os.popen('ifconfig').read()
	logging.info("ifconfig result is : %s", r)
	r_list = r.split('\n')
	logging.info("list is : %s", r_list)
	mark = 0
	for each in r_list:
		if mark == 1 and 'inet' in each:
			logging.info("found inet : %s", each)
			ip_list = each.split()
			if 'inet' in ip_list:
				return ip_list[ip_list.index('inet')+1]
		if 'wlan0' in each:
			mark = 1
			logging.info("found wlan0 info : %s", each)
		else:
			pass

def ip_post(ip):
	payload={}
	headers = {
	'Authorization': 'Basic c25pcHBlcjoyS3BLIGNiQmcgYUMyNSBmNFZBIEFpMnQgV0lwTg=='
	}
	url = 'https://ssssx.vip/wp-json/jet-cct/remotecontrol/3' + '?_remote_ip=' + ip + '&_remote_name=magicdata_office&_remote_network=internal'

	try:
		response = requests.request("POST", url, headers=headers, data=payload)

		if 'success' in response.text:
			# print(f'wlan ip has been sent to ssssx.vip and response is : {response.text}')
			logging.info("wlan ip has been sent to ssssx.vip and response is : %s", response.text)
		else:
			logging.info("maybe not success : %s", response.text)
	except Exception as e:
		logging.debug('Error: %s', e)



if __name__ == '__main__':
	console = Console()
	try:
		ip = run_shell_get_wlan_ip()
		console.print(f'[cyan]检测结果[/cyan]：[blue]{ip}[/blue]')
		ip_post(ip)
		while True:
			t = int(time.time())
			if t % 3600 >= 3570 or t % 3600 <= 30:		
				ip = run_shell_get_wlan_ip()
				# print(f'Locale wlan0 ip is : {ip}')
				logging.info("Locale wlan0 ip is : %s", ip)	
				ip_post(ip)				
			else:
				pass
				
			time.sleep(60)
	except Exception as e:
		logging.debug('Error: %s', e)
	
			
		
		
