import os
import pandas as pd

# 현재 파일의 절대 경로를 기준으로 상대 경로 설정
train_tsv_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'text', 'train', 'unsmile_train_v1.0.tsv')

# TSV 파일 읽기 (delimiter 설정 필요시 추가)
train_data = pd.read_csv(train_tsv_file_path, delimiter='\t')

