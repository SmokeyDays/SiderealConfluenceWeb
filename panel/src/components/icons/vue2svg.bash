#!/bin/bash

# 设置文件夹路径
folder_path='./items/'

# 遍历文件夹中的所有.vue文件
for file in $(find $folder_path -name '*.vue')
do
  # 获取文件名，去掉扩展名
  filename=$(basename "$file" .vue)
  
  # 复制文件并删除第一行和最后一行
  sed '1d;$d' $file > $folder_path$filename.svg
done
