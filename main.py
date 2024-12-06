import datetime
import time
import tkinter as tk
from tkinter import messagebox
import subprocess
import json
import os
import sys

import threading
import signal
import psutil
data_path = os.path.join(os.path.dirname(sys.executable), "_internal",'data.json')
# os.environ['DATA_PATH'] = data_path



try:
    print(data_path)
except Exception as e:
    print(f"Error reading data: {e}")


class BotThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(BotThread, self).__init__(*args, **kwargs)
        self.daemon = True  # 设置线程为守护线程，确保主程序退出时自动终止
        self.process = None  # 存储子进程对象
        self.stopped = threading.Event()  # 创建一个事件标志，用于指示线程是否已停止

    def run(self):
        # 获取 bot.exe 的路径
        bot_path = os.path.join(os.path.dirname(sys.executable), "_internal", 'bot.exe')

        # 检查 bot.exe 是否存在
        if not os.path.exists(bot_path):
            print(f"Error: {bot_path} does not exist.")
            return

        # 使用创建新进程组的标志启动 bot.exe 进程
        self.process = subprocess.Popen([bot_path], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        # 等待子进程完成
        self.process.wait()
        # 当进程结束时，设置事件标志为已停止
        self.stopped.set()

    def stop(self):
        try:
            if self.process is not None:
                parent = psutil.Process(self.process.pid)  # 获取父进程对象
                for child in parent.children(recursive=True):  # 递归获取所有子进程
                    child.terminate()  # 尝试终止子进程

                parent.terminate()  # 终止父进程

                # 等待子进程终止，设置超时时间为3秒
                gone, still_alive = psutil.wait_procs(parent.children(recursive=True), timeout=3)
                for p in still_alive:
                    p.kill()  # 强制终止仍在运行的子进程
                parent.kill()  # 强制终止父进程
        except psutil.NoSuchProcess:
            print("The process does not exist or is already terminated.")
        except Exception as e:
            print(f"An error occurred while stopping the process: {e}")
        finally:
            self.stopped.set()  # 设置事件，表示进程已经停止

        # 确保进程对象被清理
        self.process = None

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(padx=10, pady=10)
        self.create_widgets()
        self.process = None
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.is_running = False  # 添加一个标志位，表示程序是否正在运行
        self.start_time = datetime.datetime.now()  # 记录程序开始运行的时间

    def create_widgets(self):
        self.create_labels_entries()
        self.create_buttons()
        self.create_status_text()
        self.create_info_text()

    def create_labels_entries(self):
        self.qq_label = tk.Label(self, text="你的QQ小号:")
        self.qq_label.grid(row=0, column=0, pady=5, sticky='e')
        self.qq_entry = tk.Entry(self)
        self.qq_entry.grid(row=0, column=1, pady=5)

        self.keyword_label = tk.Label(self, text="抢活关键词:")
        self.keyword_label.grid(row=1, column=0, pady=5, sticky='e')
        self.keyword_entry = tk.Entry(self)
        self.keyword_entry.grid(row=1, column=1, pady=5)

        self.group_label = tk.Label(self, text="抢活目标群号:")
        self.group_label.grid(row=2, column=0, pady=5, sticky='e')
        self.group_entry = tk.Entry(self)
        self.group_entry.grid(row=2, column=1, pady=5)

        self.send_label = tk.Label(self, text="你想扣什么:")
        self.send_label.grid(row=3, column=0, pady=5, sticky='e')
        self.send_entry = tk.Entry(self)
        self.send_entry.grid(row=3, column=1, pady=5)

    def create_buttons(self):
        self.send_button = tk.Button(self, text="更改发送词", command=self.change_send)
        self.send_button.grid(row=3, column=3, pady=5, sticky='ew')

        self.change_button = tk.Button(self, text="更改QQ号", command=self.change_qq)
        self.change_button.grid(row=0, column=3, pady=5, sticky='ew')

        self.add_keyword_button = tk.Button(self, text="添加关键词", command=self.add_keyword)
        self.add_keyword_button.grid(row=1, column=2, pady=5, sticky='ew')

        self.delete_keyword_button = tk.Button(self, text="删除关键词", command=self.delete_keyword)
        self.delete_keyword_button.grid(row=1, column=3, pady=5, sticky='ew')

        self.add_group_button = tk.Button(self, text="添加群号", command=self.add_group)
        self.add_group_button.grid(row=2, column=2, pady=5, sticky='ew')

        self.delete_group_button = tk.Button(self, text="删除群号", command=self.delete_group)
        self.delete_group_button.grid(row=2, column=3, pady=5, sticky='ew')

        self.start_button = tk.Button(self, text="开始抢活！", command=self.start_bot)
        self.start_button.grid(row=4, column=0, pady=5, sticky='ew')

        self.stop_button = tk.Button(self, text="停止抢活！", command=self.stop_bot)
        self.stop_button.grid(row=4, column=1, pady=5, sticky='ew')





    def create_status_text(self):
        self.status_text = tk.Text(self, height=5, width=50)
        self.status_text.grid(row=5, column=0, columnspan=4, pady=10)

    def create_info_text(self):
        self.group_info_text = tk.Text(self, height=5, width=50)
        self.group_info_text.grid(row=6, column=0, columnspan=4, pady=10)
        self.group_info_text.insert(tk.END, "当前检测的所有群号与反馈的QQ号还有发送词:\n")

        self.keyword_info_text = tk.Text(self, height=5, width=50)
        self.keyword_info_text.grid(row=7, column=0, columnspan=4, pady=10)
        self.keyword_info_text.insert(tk.END, "目前检测的所有关键词:\n")

        self.status_info_text = tk.Text(self, height=13, width=50)
        self.status_info_text.grid(row=8, column=0, columnspan=4, pady=10)
        self.status_info_text.insert(tk.END, "使用提示！！！！(必先看):\n1.首先设置你的QQ小号，这是抢到活时或者扣了发送词以后会提示你要不要撤回的。可以设置成QQ小号，或者男/女朋友的号，当然也可以不设置。\n2.设置触发关键词，一次只能设置一个，可以多次设置。这个你可以看你们组长每次发任务时一般会有个什么重复出现的词语，默认关键词：扣一，扣1\n3.设置检测的群号，就是你们支部派任务的群，该脚本只会在你设置的群号里面扣发送词，也可以设置多个。\n4.设置你想扣什么，就是在检测到关键词时扣什么例如：1，你可更改为数字，中文以及等等。\n还有什么问题可以咨询qq:2900153778，但是咨询了我也不一定理Y(^o^)Y")

    def on_closing(self):
        if self.is_running:  # 如果程序正在运行，弹出警告消息
            messagebox.showwarning("警告", "请先停止抢活再退出")
        else:  # 否则，正常关闭窗口
            self.master.destroy()

    def change_send(self):
        if self.is_running:
            messagebox.showwarning("警告", "正在抢活中，请先停止抢活再进行数据修改")
            return
        send = self.send_entry.get()
        if not send:
            messagebox.showwarning("输入错误", "请输入有效的内容")
            return
        data = self.load_data()
        data['send_word'] = send
        self.save_data(data)
        messagebox.showinfo("成功", "发送词已更改")
        self.status_text.insert(tk.END, f"发送词已保存，现在开始扣{send}\n")
        self.load_data()  # 更新文本框的内容

    def change_qq(self):
        if self.is_running:
            messagebox.showwarning("警告", "正在抢活中，请先停止抢活再进行数据修改")
            return
        qq = self.qq_entry.get()
        if not qq:
            messagebox.showwarning("输入错误", "请输入一个有效的QQ号")
            return
        data = self.load_data()
        data['qq'] = qq
        self.save_data(data)
        messagebox.showinfo("成功", "QQ号已更新")
        self.status_text.insert(tk.END, "QQ号已更新\n")
        self.load_data()  # 更新文本框的内容

    def add_keyword(self):
        if self.is_running:
            messagebox.showwarning("警告", "正在抢活中，请先停止抢活再进行数据修改")
            return
        keyword = self.keyword_entry.get()
        if not keyword:
            messagebox.showwarning("输入错误", "请输入有效的关键词")
            return
        data = self.load_data()
        if keyword in data['keyword']:
            messagebox.showwarning("输入错误", "关键词已存在")
            return
        data['keyword'].append(keyword)
        self.save_data(data)
        messagebox.showinfo("成功", "关键词已添加")
        self.status_text.insert(tk.END, "关键词已添加\n")
        self.load_data()  # 更新文本框的内容

    def delete_keyword(self):
        if self.is_running:
            messagebox.showwarning("警告", "正在抢活中，请先停止抢活再进行数据修改")
            return
        keyword = self.keyword_entry.get().strip()  # 去除前后空格
        if not keyword:
            messagebox.showwarning("输入错误", "请输入有效的关键词")
            return
        data = self.load_data()
        if keyword not in data['keyword']:  # 检查关键词是否存在
            messagebox.showwarning("删除错误", "关键词不存在")
            return
        data['keyword'].remove(keyword)
        self.save_data(data)
        messagebox.showinfo("成功", "关键词已删除")
        self.status_text.insert(tk.END, "关键词已删除\n")
        self.load_data()  # 更新文本框的内容

    def add_group(self):
        if self.is_running:
            messagebox.showwarning("警告", "正在抢活中，请先停止抢活再进行数据修改")
            return
        group = self.group_entry.get()
        if not group:
            messagebox.showwarning("输入错误", "请输入有效的群号")
            return
        data = self.load_data()
        if group in data['group']:
            messagebox.showwarning("输入错误", "群号已存在")
            return
        data['group'].append(group)
        self.save_data(data)
        messagebox.showinfo("成功", "群号已添加")
        self.status_text.insert(tk.END, "群号已添加\n")
        self.load_data()  # 更新文本框的内容

    def delete_group(self):
        if self.is_running:
            messagebox.showwarning("警告", "正在抢活中，请先停止抢活再进行数据修改")
            return
        group = self.group_entry.get().strip()  # 去除前后空格
        if not group:
            messagebox.showwarning("输入错误", "请输入有效的群号")
            return
        data = self.load_data()
        if group not in data['group']:  # 检查群号是否存在
            messagebox.showwarning("删除错误", "群号不存在")
            return
        data['group'].remove(group)
        self.save_data(data)
        messagebox.showinfo("成功", "群号已删除")
        self.status_text.insert(tk.END, "群号已删除\n")
        self.load_data()  # 更新文本框的内容

    def start_bot(self):
        data = self.load_data()
        start_date = data.get('start_date')
        if not start_date:
            start_date = datetime.datetime.now().strftime('%Y-%m-%d')
            data['start_date'] = start_date
            self.save_data(data)
        else:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            if (datetime.datetime.now() - start_date).days >= 31:
                messagebox.showinfo("更新提示", "该程序需要更新，请联系qq:2900153778，获取新版程序")
                return

        if not self.is_running:  # 检查是否已经有一个线程在运行
            try:
                self.bot_thread = BotThread()
                self.bot_thread.start()
            except Exception as e:
                messagebox.showerror("启动失败", f"无法启动机器人: {e}")
                self.start_button["text"] = "开始抢活！"
                self.start_button.config(state='normal')  # 启用“开始抢活！”按钮
                return
            self.start_button["text"] = "正在运行中..."
            self.start_button.config(state='disabled')  # 禁用“开始抢活！”按钮
            messagebox.showinfo("启动成功", "机器人已启动")
            self.status_text.insert(tk.END, "机器人已启动\n")
            self.load_data()  # 更新文本框的内容
            self.is_running = True  # 当程序运行时，设置标志位为True

    # def stop_bot(self):
    #     if self.is_running:
    #         def stop_and_update():
    #             self.bot_thread.stop()
    #             while not self.bot_thread.stopped.is_set():  # 等待线程停止
    #                 time.sleep(0.1)
    #             messagebox.showinfo("以点击停止，准备检查是否停止")
    #             if self.bot_thread.stopped.is_set():  # 检查进程是否已经停止
    #                 self.start_button["text"] = "开始抢活！"
    #                 self.start_button.config(state='normal')  # 启用“开始抢活！”按钮
    #                 messagebox.showinfo("停止成功", "机器人已停止")
    #                 self.status_text.insert(tk.END, "机器人已停止\n")
    #                 self.is_running = False  # 当程序停止运行时，设置标志位为False
    #             else:
    #                 messagebox.showerror("停止失败", "机器人未能成功停止")
    #
    #         # 使用一个新的线程来停止进程并更新UI
    #         threading.Thread(target=stop_and_update).start()
    #     else:
    #         messagebox.showinfo("停止失败", "机器人已经停止")
    #

    def stop_bot(self):
        if self.is_running:
            def stop_and_update():
                self.bot_thread.stop()
                while not self.bot_thread.stopped.is_set():  # 等待线程停止
                    time.sleep(0.1)
                messagebox.showerror("以点击停止", "这是一个浪费时间的弹窗，主要是防止线程阻塞，线程管理就是一坨大便（T_T）呜呜呜")
                if self.bot_thread.stopped.is_set():  # 检查进程是否已经停止
                    self.start_button["text"] = "开始抢活！"
                    self.start_button.config(state='normal')  # 启用“开始抢活！”按钮
                    messagebox.showinfo("停止成功", "机器人已停止")
                    self.status_text.insert(tk.END, "机器人已停止\n")
                    self.is_running = False  # 当程序停止运行时，设置标志位为False
                else:
                    messagebox.showerror("停止失败", "机器人未能成功停止")

            # 使用一个新的线程来停止进程并更新UI
            threading.Thread(target=stop_and_update).start()
        else:
            messagebox.showinfo("停止失败", "机器人已经停止")


    def load_data(self):
        if os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.group_info_text.delete(1.0, tk.END)
                self.group_info_text.insert(tk.END,
                                            "当前所有监测群号:\n" + ', '.join(
                                                map(str, data['group'])) + "\nQQ号: " +
                                            data['qq']+
                                            "\n当前的发送词为: " + data['send_word'] + "\n")
                # send = data.get('send_word', '')  # 获取 send 字段的值
                # self.group_info_text.insert(tk.END, f"当前扣的内容为: {send}\n")  # 在文本框中显示 send 字段的值
                self.keyword_info_text.delete(1.0, tk.END)
                self.keyword_info_text.insert(tk.END, "目前检测的所有关键词:\n" + ', '.join(data['keyword']))
                return data
        else:
            return {'qq': '', 'keyword': [], 'group': [], 'send_word': ''}

    def save_data(self, data):
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

def main():
    root = tk.Tk()
    root.title("自动抢活神器v1.1.0 design by 风间琉璃")
    app = Application(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()