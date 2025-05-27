# app/utils/constants.py

# 테스트 사용자 데이터
TEST_USERS = {
    "admin": {
        "password": "admin123",
        "name": "관리자",
        "email": "admin@example.com",
        "dept": "IT보안팀",
    },
    "user1": {
        "password": "user123",
        "name": "일반사용자",
        "email": "user1@example.com",
        "dept": "개발팀",
    },
    "kimeunje": {
        "password": "1234",
        "name": "김은제",
        "email": "test@example.com",
        "dept": "품질관리팀",
    },
    "hamtori": {
        "password": "hamtori123",
        "name": "햄토리",
        "email": "test@example.com",
        "dept": "품질관리팀",
    },
    "test": {
        "password": "123",
        "name": "테스트1",
        "email": "test@example.com",
        "dept": "품질관리팀",
    },
}

# 점수 계산 상수
SCORE_WEIGHTS = {
    'EDUCATION_PENALTY': 0.5,  # 정보보호 교육 미이수 시 감점
    'TRAINING_PENALTY': 0.5,  # 모의훈련 미흡 시 감점
    'AUDIT_PENALTY': 0.5,  # 감사 미흡 항목당 감점
}

# 등급 기준
GRADE_CRITERIA = [
    (95, 'A+'),
    (90, 'A'),
    (85, 'B+'),
    (80, 'B'),
    (75, 'C+'),
    (70, 'C'),
    (60, 'D'),
    (0, 'F'),
]

# 검증 예외 항목 목록
EXCEPTION_ITEM_NAMES = [
    "정보자산 물리적 보호조치",
    "인증수단 기밀성 유지",
    "무선AP 확인",
    "정밀검사 이력",
    "실시간 감시",
    "백신 업데이트",
    "개인정보 파일의 암호화 저장",
    "개인정보 보유의 적정성",
    "고유 식별번호 처리 제한",
]

# HTTP 상태 코드
HTTP_STATUS = {
    'OK': 200,
    'CREATED': 201,
    'BAD_REQUEST': 400,
    'UNAUTHORIZED': 401,
    'FORBIDDEN': 403,
    'NOT_FOUND': 404,
    'INTERNAL_SERVER_ERROR': 500,
}

# 메시지 상수
MESSAGES = {
    'UNAUTHORIZED': '인증 토큰이 필요합니다.',
    'INVALID_TOKEN': '유효하지 않은 토큰입니다.',
    'EXPIRED_TOKEN': '토큰이 만료되었습니다.',
    'USER_NOT_FOUND': '사용자 정보를 찾을 수 없습니다.',
    'ADMIN_REQUIRED': '관리자 권한이 필요합니다.',
    'LOGIN_SUCCESS': '로그인 성공',
    'LOGOUT_SUCCESS': '로그아웃 성공',
    'INVALID_CREDENTIALS': '아이디 또는 비밀번호가 올바르지 않습니다.',
    'VERIFICATION_CODE_SENT': '인증 코드가 발송되었습니다.',
    'INVALID_VERIFICATION_CODE': '인증 코드가 일치하지 않거나 만료되었습니다.',
    'EMAIL_REQUIRED': '이메일 주소가 필요합니다.',
    'MISSING_REQUIRED_FIELDS': '필수 필드가 누락되었습니다.',
    'SERVER_ERROR': '서버 오류가 발생했습니다.',
    'ITEM_NOT_FOUND': '체크리스트 항목을 찾을 수 없습니다',
    'VALIDATION_SUCCESS': '검사 항목이 정상적으로 확인되었습니다.',
}

# 기본 인증 코드 (테스트용)
DEFAULT_VERIFICATION_CODE = "123456"