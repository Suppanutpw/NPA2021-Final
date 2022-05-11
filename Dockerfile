FROM python
COPY ./62070186-bot.py /home/myapp/
COPY ./requirement.txt /home/myapp/
RUN pip install -r /home/myapp/requirement.txt
EXPOSE 3000
CMD python3 /home/myapp/62070186-bot.py
