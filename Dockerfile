# 使用官方Python运行时作为父镜像
FROM python:3.8.10

# 将当前目录内容复制到容器的/app中
ADD ./asset /asset
ADD ./config /config
ADD ./tools /tools
COPY main.py .
COPY requirements.txt .

RUN pip install --upgrade -i https://pypi.tuna.tsinghua.edu.cn/simple pip
# 安装程序需要的包
RUN python3 -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple


# 运行时监听的端口
EXPOSE 3002

# 运行app.py时的命令及其参数
CMD ["python", "main.py"]
