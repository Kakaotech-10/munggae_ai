from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from model.model_pretrain.filtering_model import load_model, predict_hate_speech
app = FastAPI()


model, tokenizer = load_model()

# 요청 데이터 모델 정의
class TextRequest(BaseModel):
    text: str  # text 

@app.post("/api/v1/comments/")
def text_filtering_api(request: TextRequest):
    result = predict_hate_speech(model, tokenizer, request.text)  
    
    if 'clean' not in result:
        return{
            "origin_text": request.text,
            "filtered_labels": result,
            "message": f"{result}에 위배되는 문장입니다."
        }

    #clean일 경우
    return{
        "origin_text": request.text,
        "filtered_labels": ["clean"],
        "message": f"{request.text}"
    }



#uvicorn ai_server:app --reload
#/opt/homebrew/bin/python3 -m uvicorn ai_server:app --reload -> lucy환경실행