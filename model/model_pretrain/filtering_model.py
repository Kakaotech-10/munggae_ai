from transformers import BertForSequenceClassification, AutoTokenizer
from kobert_tokenizer import KoBERTTokenizer
import torch
import os

# 혐오 발언 레이블 정의
unsmile_labels = ["여성/가족", "남성", "성소수자", "인종/국적", "연령", "지역", "종교", "악플/욕설", "clean"]

# 저장된 모델과 토크나이저 불러오기
def load_model():
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_directory = os.path.join(current_dir, "koBERT_model_v1.01")

    # 분류 모델과 토크나이저 로드
    model = BertForSequenceClassification.from_pretrained(model_directory)
    tokenizer = KoBERTTokenizer.from_pretrained(model_directory)
    model.eval()
    return model, tokenizer

# 예측 함수
def predict_hate_speech(model, tokenizer, text: str):
    # 입력 텍스트를 모델 입력 형태로 변환
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)

    # 모델 예측 수행
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

    # 로짓 값을 확률로 변환
    probabilities = torch.sigmoid(logits).squeeze().tolist()

    # 0.5 이상의 확률을 가진 레이블만 선택
    predicted_labels = [unsmile_labels[i] for i, prob in enumerate(probabilities) if prob >= 0.5]

    # 예측된 레이블 반환 (없으면 "clean" 반환)
    return predicted_labels if predicted_labels else ["clean"]
