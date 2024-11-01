import pandas as pd
import os

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HateScore_file_path = os.path.join(base_dir, 'ai', 'data', 'text', 'train', 'HateScore.csv')
unsmile_file_path = os.path.join(base_dir, 'ai', 'data', 'text', 'train', 'unsmile_train_v1.0.tsv')

hatescore_data = pd.read_csv(HateScore_file_path)
unsmile_data= pd.read_csv(unsmile_file_path, delimiter='\t') #tsv 파일이므로 delimiter함수 적용

# Display first few rows of both datasets to understand the structure
unsmile_data.head(), hatescore_data.head()

# Define a mapping from HateScore's 'microlabel' to Unsmile's label columns
label_mapping = {
    '여성/가족': '여성/가족',
    '남성': '남성',
    '성소수자': '성소수자',
    '인종/국적': '인종/국적',
    '연령': '연령',
    '지역': '지역',
    '종교': '종교',
    '기타 혐오': '기타 혐오',
    '악플/욕설': '악플/욕설',
    'clean': 'clean'
}

# Initialize a new DataFrame with the same structure as the Unsmile dataset
# Set all labels to 0 by default
hatescore_mapped_df = pd.DataFrame(columns=unsmile_data.columns)

# Fill the new DataFrame with the text from HateScore and map labels accordingly
hatescore_mapped_df['문장'] = hatescore_data['comment']

# For each 'microlabel', assign the corresponding column a 1
for unsmile_label in unsmile_data.columns[1:]:
    hatescore_mapped_df[unsmile_label] = 0  # Default is 0 for each label

# Update labels according to the microlabel in HateScore
for index, row in hatescore_data.iterrows():
    microlabel = row['microlabel']
    if microlabel in label_mapping:
        hatescore_mapped_df.at[index, label_mapping[microlabel]] = 1
    else:
        hatescore_mapped_df.at[index, 'clean'] = 1  # If it's not in the mapping, mark it as 'clean'

# Show the transformed hatescore_mapped_df DataFrame
hatescore_mapped_df.head()


# 두 데이터셋을 결합 (Unsmile 데이터와 전처리된 HateScore 데이터)
combined_dataset = pd.concat([unsmile_data, hatescore_mapped_df], ignore_index=True)

# 결합된 데이터셋 확인
print(combined_dataset.head())
print(combined_dataset.tail())

output_file_path = os.path.join(base_dir, 'ai', 'data', 'text', 'train', 'combined_unsmile_hatescore_fixed.csv')
combined_dataset.to_csv(output_file_path, index= False)
print(f"CSV 파일이 {output_file_path}에 저장되었습니다.")