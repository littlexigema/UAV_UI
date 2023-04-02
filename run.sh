#!/bin/sh

(python3 /home/gsr/code_save/qt/pre_run.py) & (python3 /home/gsr/code_save/qt/无人机UI.py 无人机_1) & (python3 /home/gsr/code_save/qt/无人机UI.py 无人机_2)& (python3 /home/gsr/code_save/qt/无人机UI.py 无人机_3)
rm /home/gsr/code_save/qt/temporary_save