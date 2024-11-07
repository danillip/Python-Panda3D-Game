# coding=windows-1251
import json
import os
import subprocess

def choose_level():
    print("�������� �������:")
    levels = ["level", "level2", "level3", "testlevel"]
    for index, level in enumerate(levels, start=1):
        print(f"{index}. {level}")
    
    choice = int(input("������� ����� ������: ")) - 1
    
    if 0 <= choice < len(levels):
        selected_level = levels[choice]
        save_selected_level(selected_level)
        print(f"������ �������: {selected_level}")
        
        # �������� ������ ���� � demo.py
        demo_script_path = os.path.join(os.path.dirname(__file__), "demo.py")
        
        # ������ demo.py � ��������� �������
        subprocess.run(["python", demo_script_path])
    else:
        print("������������ �����. ���������� �����.")

def save_selected_level(level):
    config_path = "data/configmap.json"
    data = {"selected_level": level}

    # �������� �����, ���� �� �� ����������
    if not os.path.exists("data"):
        os.makedirs("data")

    with open(config_path, 'w') as config_file:
        json.dump(data, config_file)

if __name__ == "__main__":
    choose_level()
