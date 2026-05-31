#!/usr/bin/python
# #encoding=utf-8
import subprocess
import ffmpeg
import os
import xlwt
import xlrd
from xlutils.copy import copy

cc_n = 'prores'
w = 1920
h = 1080

def check_video_info(path):
    rows=["name", "frames"]
    names=[]
    frames=[]
    colums=[]
    video_files=os.listdir(path)
    ecxl_file=os.path.join(path,'video_info.xls')
    if os.path.exists(r"N:\NZTF\F_Animation\EP008\checkmov\video_error.txt"):
        os.remove(r"N:\NZTF\F_Animation\EP008\checkmov\video_error.txt")
        video_files.remove('video_error.txt')

    for v_f in video_files:
        video_file = os.path.join(path,v_f)
        try:
            info = ffmpeg.probe(video_file)
            vs = next(c for c in info['streams'] if c['codec_type'] == 'video')
            codec_name = vs['codec_name']
            print codec_name
            width = vs['width']
            height = vs['height']
            num_frames=vs['nb_frames']
            names.append(os.path.splitext(v_f)[0])
            frames.append(num_frames)
            if codec_name == cc_n and width == w and height == h and v_f.endswith("mov"):
                pass
            elif v_f.endswith("txt") or v_f.endswith("xls"):
                pass
            else:
                f=open(r"N:\NZTF\F_Animation\EP008\checkmov\video_error.txt",mode="a")
                f.write("%s\n"%(v_f))
                f.close()
                print v_f
        except:
            pass
    colums.extend([names, frames])
    if not os.path.exists(ecxl_file):
        print names, frames
        write_excel(ecxl_file, rows,colums)
    else:
        read_excel(ecxl_file)
        write_excel_append(ecxl_file,colums)

def set_style(name,height,bold=False):
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = name
    font.bold = bold
    font.color_index = 4
    font.height = height
    style.font = font
    return style

def write_excel(path,row,colum):
    f = xlwt.Workbook()
    video_info_sheet = f.add_sheet('video_info', cell_overwrite_ok=True)
    row0 = row
    colum0 = colum

    for i in range(0,len(row0)):
        video_info_sheet.write(0,i,row0[i],set_style('Times New Roman',220,True))
        for r in range(0, len(colum0)+1):
            video_info_sheet.write(r + 1, i, colum0[i][r], set_style('Times New Roman', 220, True))

    f.save(path)

def read_excel(path):
    wb = xlrd.open_workbook(filename=path)
    print(wb.sheet_names())
    video_info_sheet = wb.sheet_by_index(0)
    print video_info_sheet.name

    rows = video_info_sheet.row_values(0)
    cols = video_info_sheet.col_values(1)
    print rows,cols

def write_excel_append(path,value):
    index = len(value)
    workbook = xlrd.open_workbook(path)
    sheets = workbook.sheet_names()
    worksheet = workbook.sheet_by_name(sheets[0])
    rows_old = worksheet.nrows
    new_workbook = copy(workbook)
    new_worksheet = new_workbook.get_sheet(0)
    for i in range(0, index):
        for j in range(0, len(value[i])):
            new_worksheet.write(j+rows_old, i, value[i][j],set_style('Times New Roman', 220, True))
    new_workbook.save(path)

check_video_info("N:\NZTF\F_Animation\EP008\checkmov")