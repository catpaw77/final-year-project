import os, subprocess
from flask_socketio import SocketIO, emit
import time

class Detector:
    def add_module(file_name):
        # input: 使用者上傳的檔案名稱
        # 將 module 資訊加入資料庫(包含檔案位址)
        return
    def get_score(module_id, binary_address, socketio):
        # input: 要測試的模型 ID
        # output: 檢測結果(accuracy, loss ...)
        
        # create new env
        print("環境建置中......")
        print(binary_address)
        env_name = "env" + str(module_id)
        print("1")
        activate_env = ". $CONDA_PREFIX/etc/profile.d/conda.sh && conda activate " + env_name
        print("2")
        os.system("conda create --name " + env_name + " python=3.8.3 -y")
        print("3")
        #os.system(activate_env + " && python3 -m pip install pipreqs")
        #os.system(activate_env + " && pipreqs ./ --encoding=utf8")
        
        os.system(activate_env + " && python -m pip install --no-cache-dir -r detector/modules/current_modules/module_" + str(module_id) + "/requirements.txt")
        # testing
        print("模型預測中......")
        binary_address = str(binary_address)
        benign_files = subprocess.check_output("ls " + binary_address + "/benign", shell=True)
        ori_files = subprocess.check_output("ls " + binary_address + "/ori", shell=True)
        mir_files = subprocess.check_output("ls " + binary_address + "/Mirai", shell=True)
        benign_files = str(benign_files)[2:-1].split('\\n')[:-1]
        ori_files = str(ori_files)[2:-1].split('\\n')[:-1]
        mir_files = str(mir_files)[2:-1].split('\\n')[:-1]
        
        results = []
        benign_results = []
        ori_results = []
        mir_results = []
        counter = 0
        start_time = time.time()
        ori_TP = 0
        TN = 0
        FP = 0
        ori_FN = 0
        mir_TP = 0
        mir_FN = 0
        print("start training benign")
        for benign in benign_files:
            msg = 'testing ' + str(counter) + '/' + str(len(benign_files) + len(ori_files))
            socketio.emit('status_response', {'data': msg})
            print("before result")
            result = int(subprocess.check_output(activate_env + "&& python3 detector/modules/current_modules/module_" + str(module_id) + "/main.py -i " + binary_address + "/benign/" + benign, shell=True))
            if result < 2:
                results += [1 - result]
                if result == 0:
                    TN += 1
                else:
                    FP += 1
            benign_results += [result]
            counter += 1
        for ori in ori_files:
            msg = 'testing ' + str(counter) + '/' + str(len(benign_files) + len(ori_files))
            socketio.emit('status_response', {'data': msg})
            result = int(subprocess.check_output(activate_env + "&& python3 detector/modules/current_modules/module_" + str(module_id) + "/main.py -i " + binary_address + "/ori/" + ori, shell=True))
            if result < 2: 
                results += [result]
                if result == 0:
                    ori_FN += 1
                else:
                    ori_TP += 1
            ori_results += [result]
            counter += 1
        ori_run_time = (time.time() - start_time) / 60.0
#adversalry sample testing
        start_time = time.time()
        for mir in mir_files:
            result = int(subprocess.check_output(activate_env + "&& python3 detector/modules/current_modules/module_" + str(module_id) + "/main.py -i " + binary_address + "/Mirai/" + mir, shell=True))
            if result < 2:
                results += [result]
                if result == 0:
                    mir_FN += 1
                else:
                    mir_TP += 1
            mir_results += [result]
        mir_run_time = (time.time() - start_time) / 60.0

        print("結果分析中......")
        print(benign_results)
        print(ori_results)
        print(mir_results)
        print("acc:", float(ori_TP + TN)/(ori_TP + FP + ori_FN + TN))
        analyze_result = {"ori_TP":ori_TP, "TN":TN, "FP":FP, "ori_FN":ori_FN, "ori_runtime":ori_run_time, "mir_TP":mir_TP, "mir_FN": mir_FN, "mir_runtime":mir_run_time }
        print(analyze_result)
     #   accuracy = sum(results) / len(results)
        return analyze_result
