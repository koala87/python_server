#!/usr/bin/env python
# -*-coding:utf-8 -*-
__author__ = 'yin'
import os
import sys
import glob
import random
import pdb
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
reload(sys)
sys.setdefaultencoding("utf-8")

DB_CONNECT_STR = 'mysql+mysqldb://yqc:yqc2014@192.168.1.233/yiqiding_ktv?charset=utf8'
ENGINE = create_engine(DB_CONNECT_STR)
Session = sessionmaker(bind=ENGINE)
session = Session()
ROOT_PATH = '/Users/yin/Desktop/yin/'


def write_to_file(err_lists, err_type):
    err_fp = open('errResult.txt', 'a')
    err_fp.write('***************** %s ***************** %s' % (err_type, os.linesep))

    if err_type == 'fm' or err_type == 'actor':
        for line_err in err_lists:
            err_fp.write('%s%s' % (line_err, os.linesep))
    else:
        for line_err in err_lists:
            err_str = ''
            for err in line_err:
                err_str += str(err)
                err_str += '   '
            err_fp.write('%s%s' % (err_str, os.linesep))


def get_file_list(dir_path, file_type):
    dir_path = dir_path + '/*' + file_type
    file_list = glob.glob(dir_path)
    # #对文件名排序
    # if len(file_list)>0:
    #     file_list.sort()
    return file_list


def check_mv_video(rand_count=0):
    path_list = ('01', '02', '03', '04', '05', '06', '07', '08')
    for disk_dir in path_list:
        path_num = '/' + disk_dir + '/'
        query_str = 'SELECT  path, mid, serial_id, name FROM media WHERE path like ' + "\'" + path_num + '%' + "\'"
        mv_path = ROOT_PATH + disk_dir
        query_re = session.execute(query_str).fetchall()
        if len(query_re) < 1:
            return

        if rand_count > 0:
            lists = rand_list(query_re, rand_count)
        else:
            lists = query_re

        error_mv = []
        error_jpg = []
        mp4_files = get_file_list(mv_path, '.mp4')
        jpg_files = get_file_list(mv_path, '.jpg')
        for each_path in lists:
            each = each_path[0]
            mp4_name = each.strip(path_num)
            jpg_name = mp4_name.replace('.mp4', '_s.jpg')
            print each
            if mp4_name not in mp4_files:
                error_mv.append(each_path)

            if jpg_name not in jpg_files:
                error_jpg.append(each_path)

        if len(error_mv) > 1:
            write_to_file(error_mv, 'mv  mp4')
        if len(error_jpg) > 1:
            write_to_file(error_jpg, 'mv jpg')


def check_mv_lyric(rand_count=0):
    path_lyric = ROOT_PATH + 'lyrics'
    query_str = 'SELECT  lyric, mid, serial_id, name FROM media WHERE lyric != \'NULL\''
    query_re = session.execute(query_str).fetchall()
    if len(query_re) < 1:
        return

    if rand_count > 0:
        lists = rand_list(query_re, rand_count)
    else:
        lists = query_re

    err_lrc = []
    lyric_files = get_file_list(path_lyric, '.lrc')
    for each_lyric in lists:
        print 'lyric : %s   mid : %s  name : %s ' % (each_lyric[0], each_lyric[1], each_lyric[3])
        if each_lyric[0] not in lyric_files:
            err_lrc.append(each_lyric)

    if len(err_lrc) > 1:
        write_to_file(err_lrc, 'mv   lyric')


def check_mp3_krc(rand_count=0):
    path_p3_lyric = ROOT_PATH + 'lyrics'
    query_str = 'SELECT lyric, mmid, serial_id, name FROM media_music '
    query_re = session.execute(query_str).fetchall()
    if len(query_re) < 1:
        return

    if rand_count > 0:
        lists = rand_list(query_re, rand_count)
    else:
        lists = query_re

    err_krc = []
    lyric_files = get_file_list(path_p3_lyric, '.krc')
    for each_line in lists:
        print 'lyric : %s   mmid : %s  name : %s ' % (each_line[0], each_line[1], each_line[3])
        if each_line[0] not in lyric_files:
            err_krc.append(each_line)

    if len(err_krc) > 1:
        write_to_file(err_krc, 'mp3   lyric')


def check_mp3_video(rand_count=0):
    path_p3_video = ROOT_PATH + '09'

    query_str = 'SELECT path, mmid, serial_id, name FROM media_music '
    query_re = session.execute(query_str).fetchall()
    if len(query_re) < 1:
        return

    if rand_count > 0:
        lists = rand_list(query_re, rand_count)
    else:
        lists = query_re

    err_video = []
    video_files = get_file_list(path_p3_video, '.mp4')
    for each_line in lists:
        print 'path : %s   mmid : %s  name : %s ' % (each_line[0], each_line[1], each_line[3])
        if each_line[0] not in video_files:
            err_video.append(each_line)

    if len(err_video) > 1:
        write_to_file(err_video, 'mp3   mp4')


def check_fm(rand_count=0):
    path_fm = ROOT_PATH + 'fm'
    query_str = 'SELECT lid, serial_id, title FROM songlist;'
    query_re = session.execute(query_str).fetchall()

    err_fm = check_picture(query_re, path_fm, 2, rand_count)
    if len(err_fm) > 1:
        # for err in err_fm:
        write_to_file(err_fm, 'fm')


def check_actor(rand_count=0):
    path_actor = ROOT_PATH + 'avatar'
    query_str = 'SELECT sid, serial_id, name FROM actor;'
    query_re = session.execute(query_str).fetchall()

    err_actor = check_picture(query_re, path_actor, 2, rand_count)
    if len(err_actor) > 1:
        # for err in err_actor:
        write_to_file(err_actor, 'actor')


def check_picture(sql_list, d_path, n_index, rand_count=0):

    err_list = []
    if len(sql_list) > 0:
        files = get_file_list(d_path, '.jpg')

        if rand_count > 0:
            lists = rand_list(sql_list, rand_count)
        else:
            lists = sql_list

        for each_line in lists:
            jpg_name = each_line[n_index]
            jpg_name += '.jpg'
            name = d_path + '/' + jpg_name
            print name
            if name not in files:
                err_list.append(jpg_name)

    return err_list


def rand_list(sql_list, rand_count):

    list_rv = []
    rand = []
    if len(sql_list) < rand_count:
        rand_count = len(sql_list)
    for i in range(rand_count):
        rand.append(random.randint(0, rand_count))

    for index in rand:
        list_rv.append(sql_list[index])
    return list_rv


def main(arg_v):
    type_lists = ['mv',  'mv_video', 'mv_lyric',
                  'mp3', 'mp3_video', 'mp3_lyric',
                  'fm_jpg', 'actor_jpg',
                  'picture', 'video', 'lyric']

    type_dict = {}
    if len(arg_v) > 1:
        for lis in arg_v[1:len(arg_v)]:
            if lis in type_lists:
                type_dict[lis] = 0
                pos = arg_v.index(lis) + 1
                if len(arg_v) - 1 >= pos:
                    if arg_v[pos].isdigit():
                        type_dict[lis] = int(arg_v[pos])
    elif len(arg_v) == 1:
        # check_mv_lyric()
        # check_mv_video()
        check_mp3_krc()
        check_mp3_video()
        # check_fm()
        # check_actor()

    if len(arg_v) != 1 and not type_dict:
        print '默认不带参数检测所有，包括MV和MP3歌词视频图片、FM和歌星头像\n' \
              '[mv]             检测MV  视频图片和歌词\n' \
              '[mv_video]       检测MV  视频和图片\n' \
              '[mv_lyric]       检测MV  歌词\n' \
              '[mp3]            检测MP3 视频和歌词 \n' \
              '[mp3_video]      检测MP3 视频\n' \
              '[mp3_lyric]      检测MP3 歌词\n' \
              '[fm_jpg]         检测FM  图片\n' \
              '[actor_jpg]      检测歌星 头像\n' \
              '[picture]        检测FM和歌星 图片\n' \
              '[video]          检测MV和MP3 视频（包括MV的对应的视频图片）\n' \
              '[lyric]          检测MV和MP3 歌词\n' \
              '选项后面带参数表示 随机抽取的检测数 \n' \
              '例：mv 5000 随机抽取5000条纪录检测'

    for type_sig in type_dict:
        if type_sig == 'mv':
            check_mv_video(type_dict[type_sig])
            check_mv_lyric(type_dict[type_sig])
        elif type_sig == 'mv_video':
            check_mv_video(type_dict[type_sig])
        elif type_sig == 'mv_lyric':
            check_mv_lyric(type_dict[type_sig])
        elif type_sig == 'mp3':
            check_mp3_video(type_dict[type_sig])
            check_mp3_krc(type_dict[type_sig])
        elif type_sig == 'mp3_video':
            check_mp3_video(type_dict[type_sig])
        elif type_sig == 'mp3_lyric':
            check_mp3_krc(type_dict[type_sig])
        elif type_sig == 'fm_jpg':
            check_fm(type_dict[type_sig])
        elif type_sig == 'actor_jpg':
            check_actor(type_dict[type_sig])
        elif type_sig == 'picture':
            check_fm(type_dict[lis])
            check_actor(type_dict[type_sig])
        elif type_sig == 'video':
            check_mv_video(type_dict[type_sig])
            check_mp3_video(type_dict[type_sig])
        elif type_sig == 'lyric':
            check_mp3_krc(type_dict[type_sig])
            check_mv_lyric(type_dict[type_sig])


if __name__ == '__main__':
    main(sys.argv)


