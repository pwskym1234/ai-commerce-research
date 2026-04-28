"""
GEO 파이프라인 설정 — 샘플

실제 키를 채워 `pipeline/config.py` 로 복사해 사용하세요.
`pipeline/config.py` 는 `.gitignore` 에 등록되어 있습니다.
"""

# ========== API 키 ==========
# 03_run_audit.py 가 사용
OPENAI_API_KEY = ""

# 02_generate_prompts.py / 04_parse_responses.py / 06_neutral_brand_ranking.py 가 사용
ANTHROPIC_API_KEY = ""


# ========== 모델 ==========
# 03_run_audit.py 가 사용 (실제 사용자 질문에 답하는 역할 — 웹서치 사용)
MODEL = "gpt-4o-search-preview"

# 02/04/06 이 사용하는 Claude 보조 모델
CLAUDE_MODEL = "claude-sonnet-4-6"

# (legacy) 04 의 evidence URL 인용 fallback 호환용
PARSE_MODEL = "gpt-4o-mini"


# ========== 실행 옵션 ==========
# 프롬프트 1개당 몇 번 반복 호출할지 (결과 분산 측정용)
REPEAT_COUNT = 2

# API 호출 간 대기 시간 (초). 웹서치 모델은 응답이 느리므로 1.0 권장
REQUEST_DELAY = 1.0

# 03_run_audit.py 병렬 worker 수
MAX_WORKERS = 8

# 메타데이터 기록용 — 실제 API 호출에는 직접 전달되지 않음
SEED_BASE = 1000
TEMPERATURE = 1.0
