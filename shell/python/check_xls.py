#!/usr/bin/env python3
#coding:utf-8

import sys
import os


def regfile(key, XLS):
    import re
    import xlrd
    data  = xlrd.open_workbook(XLS)
    reg = re.compile(key)
    for names in data.sheet_names():
        reg_temp = []
        print()
        print ("<<<<<<<<<<<" + XLS+ " 表 " + names + " >>>>>>>>>>")
        sheet = data.sheet_by_name(names)
        for row_num in range(sheet.nrows):
            row_content = '|'.join( str(i) for i in sheet.row_values(row_num) )
            if reg.search(row_content):
                reg_temp.append(row_content)
        for line in reg_temp:
            print(line)

def get_xls_file(dir):
    files =[]
    files = [ dir+x for x in os.listdir(dir) if os.path.splitext(x)[-1] in ['.xls', '.xlsx']  ]
    return files


if __name__ == "__main__":
    key = sys.argv[1]
    dir = sys.argv[2]
    xls_file = get_xls_file(dir)
    for xls in xls_file:
        regfile(key,xls)
