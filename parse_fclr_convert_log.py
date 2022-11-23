import sys
import argparse
import re
from datetime import datetime


def createParser ():
    parser = argparse.ArgumentParser(
        description='Put out information from fclr_convert log file.',
        epilog=f'Example: {sys.argv[0]} -f "./fclr_convert.log" -t "epoch_loss"'
    )
    parser.add_argument ('-f', '--file', default='./fclr_convert.log', help='string path')
    parser.add_argument ('-t', '--tab', default='base_metrics', help='"base_metrics" or "epoch_loss"')
    return parser

def get_message(func):
    # Парсит строку лога и передает дальше ее как сообщение, разделенное на группы, с которыми можно работать
    def inner(line):
        log  = re.match('(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) (?P<level>\w+) (?P<handler>.+?:) (?P<message>.*$)', line)
        return func(log)
    return inner

@get_message
def epoch_loss(message):
    if message is not None:
        epoch_loss = re.match(r"Loss \((?P<epoch>\d+\/\d+)\): train: (?P<train>\d+\.\d+), valid: (?P<valid>\d+\.\d+) (?P<trend>.)", message.group('message'))
        if epoch_loss is not None:
            return (epoch_loss.group('epoch'), epoch_loss.group('train'), epoch_loss.group('valid'), epoch_loss.group('trend'))

@get_message
def loss(message):
    if message is not None:
        loss = re.match(r" loss: (?P<loss>\d+\.\d+)", message.group('message'))
        if loss is not None: return loss.group('loss')

@get_message
def auc(message):
    if message is not None:
        auc = re.match(r" AUC: (?P<auc>\d+\.\d+)", message.group('message'))
        if auc is not None: return auc.group('auc')

@get_message
def date_time(message):
    if message is not None:
        return datetime.fromisoformat(message.group('date') + ' ' + message.group('time'))

def get_epoch_loss(log_file):
    with open(log_file) as f:
        line = f.readline()
        print(f"||epoch||train||valid||trend||")
        while line:
            loss = epoch_loss(line)
            if loss:
                (epoch, train, valid, trend)  = loss
                print(f"|{epoch}|{train}|{valid}|{trend}|")
            line = f.readline()

def get_base_metrics(log_file):
    with open(log_file) as f:
        line = f.readline()
        start_time = date_time(line)
        print(f"||loss||auc||time (min)||")
        while line:
            if loss(line): loss_metric = loss(line)
            if auc(line): auc_metric = auc(line)
            finish_time = date_time(line)
            line = f.readline()
        print(f"|{loss_metric}|{auc_metric}|{(finish_time - start_time).seconds // 60}|")

if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
    if namespace.tab:
        if namespace.tab == 'base_metrics':
            get_base_metrics(namespace.file)
        elif namespace.tab == 'epoch_loss':
            get_epoch_loss(namespace.file)
        else: print('Table must be "base_metrics" or "epoch_loss"')
    else: print('Please, set in the path to fclr_convert log file.')