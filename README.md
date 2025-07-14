# 🧠 LLM4Game

LLM 기반 에이전트를 사용해 게임 환경에서 전략적 의사결정 능력을 실험하고 평가하는 프레임워크입니다.

---

## 📦 설치 방법

### 가상환경 생성 및 활성화

```bash
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install --frozen
```

---

## ▶️ 실행 방법

### 서버 실행

```bash
python server.py
```

### Visual Tool 실행

```bash
python app.py
```

### 콘솔 클라이언트 실행

```bash
python console_client.py
```

### 실험 실행

```bash
python exp.py
```

---

## 📂 주요 디렉토리 구조

```
LLM4Game/
├── analysis/     
├── client/       
├── config/       
├── log/          
├── pyautobattle/ 
├── ui/           
│
├── app.py           
├── server.py        
├── console_client.py
├── llm_agent.py     
├── random_agent.py  
├── exp.py           
│
├── pyproject.toml  
├── uv.lock         
├── .python-version 
└── README.md       
```