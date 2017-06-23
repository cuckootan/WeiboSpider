#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Jason'


import re


def injection(input_path, weibo_dir_path):
    ret = []
    with open(input_path, 'r') as fr:
        for line in fr:
            if line.strip() == '':
                continue

            temp_list = re.split(r'\s', line.strip())
            ret.append((temp_list[0], temp_list[1]))

    input_str = '['
    for idx in range(len(ret) - 1):
        input_str += "('{0:s}', '{1:s}'), ".format(ret[idx][0], ret[idx][1])
    input_str += "('{0:s}', '{1:s}')]".format(ret[-1][0], ret[-1][1])

    new_doc = ''
    with open(weibo_dir_path + 'WeiboSpider/settings.py', 'r') as fr:
        for line in fr:
            if re.search('SPEC_WEIBO_ENABLED', line.strip()):
                new_doc += 'SPEC_WEIBO_ENABLED = True\n'
            elif re.search('SPEC_WEIBO_LIST', line.strip()):
                new_doc += 'SPEC_WEIBO_LIST = {0:s}\n'.format(input_str)
            else:
                new_doc += line

    with open(weibo_dir_path + 'WeiboSpider/settings.py', 'w') as fw:
        fw.write(new_doc)


if __name__ == '__main__':
    input_path  = '/home/cuckootan/Desktop/sample.txt'
    weibo_dir_path = '/home/cuckootan/Desktop/WeiboSpider/'

    injection(input_path, weibo_dir_path)
