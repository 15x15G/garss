import feedparser
import time
import os
import re
import pytz
from datetime import datetime
import requests
import markdown
import json
import shutil
from urllib.parse import urlparse


def get_rss_info(feed_url):
    result = {"result": []}
    # 如何请求出错,则重新请求,最多3次
    for i in range(3):
        try:
            headers = {
                # 设置用户代理头(为狼披上羊皮)
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
                "Content-Encoding": "gzip"
            }
            # 设置10秒钟超时
            feed_url_content = requests.get(feed_url,  timeout= 10 ,headers = headers).content
            feed = feedparser.parse(feed_url_content)
            feed_entries = feed["entries"]
            feed_entries_length = len(feed_entries)
            print("==feed_url=>>", feed_url, "==len=>>", feed_entries_length)
            for entrie in feed_entries[0: feed_entries_length-1]:
                title = entrie["title"]
                link = entrie["link"]
                date = time.strftime("%Y-%m-%d", entrie["published_parsed"])
                result["result"].append({
                    "title": title,
                    "link": link,
                    "date": date
                })
            break
        except Exception as e:
            print(feed_url+"第+"+str(i)+"+次请求出错==>>",e)
            pass


    return result["result"]
    
def replace_readme():
    new_edit_readme_md = [""]
    # 读取EditREADME.md
    print("replace_readme")
    with open(os.path.join(os.getcwd(),"EditREADME.md"),'r') as load_f:
        edit_readme_md = load_f.read();
        new_edit_readme_md[0] = edit_readme_md
        # before_info_list =  re.findall(r'\{\{latest_content\}\}.*\[订阅地址\]\(.*\)' ,edit_readme_md)
        before_info_list =  re.findall(r'\*\s\[订阅地址\]\(.*\)\s+\{\{latest_content\}\}' ,edit_readme_md)
        # 填充统计RSS数量
        new_edit_readme_md[0] = new_edit_readme_md[0].replace("{{rss_num}}", str(len(before_info_list)))
        # 填充统计时间
        ga_rss_datetime = datetime.fromtimestamp(int(time.time()),pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
        new_edit_readme_md[0] = new_edit_readme_md[0].replace("{{ga_rss_datetime}}", str(ga_rss_datetime))
        for before_info in before_info_list:
            # 获取link
            link = re.findall(r'\[订阅地址\]\((.*)\)', before_info)[0]
            # 生成超链接
            rss_info = get_rss_info(link)
            latest_content = ""
            parse_result = urlparse(link)
            scheme_netloc_url = str(parse_result.scheme)+"://"+str(parse_result.netloc)

            if(len(rss_info) == 0):
                latest_content = "[更新失败]("+ scheme_netloc_url +")"
            else:
                rss_item_num=0
                for rss_item in rss_info:
                    rss_item["title"] = rss_item["title"].replace("|", "\|")
                    rss_item["title"] = rss_item["title"].replace("[", "\[")
                    rss_item["title"] = rss_item["title"].replace("]", "\]")
                    if (rss_item["date"] == datetime.today().strftime("%Y-%m-%d")):
                        istoday= " new! "
                    else:
                        istoday= "" 
                    latest_content += "    * ["  + rss_item["title"]  +"](" + rss_item["link"] +") "+ istoday +"\n"  
                    rss_item_num+=1
                    if rss_item_num>=10:
                        break               
            
            # 生成after_info
            after_info = before_info.replace("{{latest_content}}", latest_content)
            print("====latest_content==>", latest_content)
            # 替换edit_readme_md中的内容
            new_edit_readme_md[0] = new_edit_readme_md[0].replace(before_info, after_info)
    # 将新内容
    with open(os.path.join(os.getcwd(),"README.md"),'w') as load_f:
        load_f.write(new_edit_readme_md[0])
    
    return new_edit_readme_md[0]

# 将README.md复制到docs中

def cp_readme_md_to_docs():
    shutil.copyfile(os.path.join(os.getcwd(),"README.md"), os.path.join(os.getcwd(), "docs","README.md"))
    
def cp_media_to_docs():
    if os.path.exists(os.path.join(os.getcwd(), "docs","_media")):
        shutil.rmtree(os.path.join(os.getcwd(), "docs","_media"))	
    shutil.copytree(os.path.join(os.getcwd(),"_media"), os.path.join(os.getcwd(), "docs","_media"))


def main():
    readme_md = replace_readme()
    content = markdown.markdown(readme_md, extensions=['tables', 'fenced_code'])
    cp_readme_md_to_docs()
    cp_media_to_docs()



main()
