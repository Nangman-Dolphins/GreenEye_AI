import os
import requests
import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# 환경 변수 로드
load_dotenv()

# Flask 앱 생성
app = Flask(__name__)

# --- 설정 부분 ---
GEMINI_API_KEY = os.getenv('SECRET_KEY')  # .env 파일에서 API 키를 가져옵니다.
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
print(f"GEMINI_API_KEY: {GEMINI_API_KEY}")  # 디버깅용 출력
# --- 설정 끝 ---


@app.route('/ask-gemini', methods=['POST'])
def ask_gemini():
    # 1. 프론트엔드에서 보낸 JSON 데이터 받기
    #    예: {"prompt": "이 식물 이름이 뭐야?", "image": "base64인코딩된문자열..."}
    data = request.get_json()

    if not data or 'prompt' not in data:
        return jsonify({"error": "No prompt provided"}), 400

    user_prompt = data['prompt']
    # 'image'는 필수가 아닐 수 있으므로 .get()을 사용
    image_base64 = data.get('image')

    # 2. Gemini API에 보낼 데이터 형식 준비 (멀티모달)
    #    'parts' 리스트에 텍스트와 이미지를 각각의 객체로 추가
    parts = [{"text": user_prompt}]
    
    # 이미지 데이터가 있는 경우에만 parts 리스트에 추가
    if image_base64:
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",  # 또는 "image/png" 등 이미지 형식에 맞게
                "data": image_base64
            }
        })

    gemini_payload = {
        "contents": [{"parts": parts}]
    }
    
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        # 3. Gemini API에 요청 보내기
        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(gemini_payload))
        response.raise_for_status()

        gemini_response = response.json()
        
        # 4. Gemini의 답변을 프론트엔드에 돌려주기
        answer = gemini_response['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"answer": answer})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    except (KeyError, IndexError) as e:
        print("Unexpected Gemini response format:", gemini_response)
        return jsonify({"error": "Failed to parse Gemini response"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)