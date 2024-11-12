# AI text filtering model
Python3.10이상

필수 라이브러리 다운로드
pip install -r requirements.txt

메인 서버 파일(ai_server.py) 실행 -> uvicorn ai_server:app --reload

작업 환경 - Python, colab(모델 학습용)

API 통신 - FastAPI

모델 학습 - Pytorch, huggingface


"""
모델 lfs다운로드 & 업로드 과정
"""

git lfs install : 깃 lfs 다운로드 

cd model/koBERT_model_v1.01

git lfs track "*.safetensor" : 대용량 파일 지정

git add .gitattributes

git add *safetensor

git commit -m "커밋메시지"

git push origin main
