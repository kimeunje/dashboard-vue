# Flask 프로젝트 구조화 계획

## 폴더 구조

```
project/
├── app.py                      # 메인 애플리케이션 진입점
├── config.py                   # 설정 파일
├── requirements.txt            # 의존성 목록
│
├── app/
│   ├── __init__.py            # Flask 앱 팩토리
│   ├── models/                # 데이터베이스 모델
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── audit.py
│   │   ├── education.py
│   │   └── training.py
│   │
│   ├── services/              # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── audit_service.py
│   │   ├── education_service.py
│   │   ├── training_service.py
│   │   └── score_service.py
│   │
│   ├── controllers/           # API 컨트롤러
│   │   ├── __init__.py
│   │   ├── auth_controller.py
│   │   ├── audit_controller.py
│   │   ├── education_controller.py
│   │   ├── training_controller.py
│   │   ├── score_controller.py
│   │   └── admin_controller.py
│   │
│   ├── utils/                 # 유틸리티
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── validation.py
│   │   ├── decorators.py
│   │   └── constants.py
│   │
│   └── static/               # Vue 빌드 파일
│       └── templates/        # 템플릿 파일
│
└── logs/                     # 로그 파일
```

## 마이그레이션 순서

1. **config.py** - 설정 관리
2. **app/**init**.py** - Flask 앱 팩토리
3. **app/utils/database.py** - 데이터베이스 연결 관리
4. **app/utils/constants.py** - 상수 관리
5. **app/utils/decorators.py** - 데코레이터 (인증, 관리자 권한)
6. **app/utils/validation.py** - 검증 로직
7. **app/models/\*.py** - 데이터 모델
8. **app/services/\*.py** - 비즈니스 로직
9. **app/controllers/\*.py** - API 컨트롤러
10. **app.py** - 메인 진입점

## 주요 개선사항

- **관심사 분리**: 인증, 감사, 교육, 훈련, 점수 계산을 각각 분리
- **재사용성**: 공통 로직을 서비스 레이어로 추출
- **테스트 용이성**: 각 컴포넌트를 독립적으로 테스트 가능
- **확장성**: 새로운 기능 추가 시 해당 영역만 수정
- **유지보수성**: 코드 위치를 쉽게 찾을 수 있음

# Flask 프로젝트 구조화 마이그레이션 가이드

## 1. 폴더 구조 생성

기존 `mock_app.py`가 있는 디렉토리에서 다음 구조를 생성하세요:

```bash
mkdir -p app/{controllers,services,utils,models,static,templates}
```

## 2. 파일 생성 순서

### 단계 1: 기본 설정 파일들

1. `config.py` - 설정 관리
2. `requirements.txt` - 의존성 목록

### 단계 2: 유틸리티 파일들

3. `app/utils/__init__.py` (빈 파일)
4. `app/utils/constants.py` - 상수 관리
5. `app/utils/database.py` - 데이터베이스 연결 관리
6. `app/utils/decorators.py` - 인증/권한 데코레이터
7. `app/utils/validation.py` - 검증 로직

### 단계 3: 서비스 레이어

8. `app/services/__init__.py` (빈 파일)
9. `app/services/auth_service.py` - 인증 서비스
10. `app/services/audit_service.py` - 감사 서비스
11. `app/services/score_service.py` - 점수 계산 서비스
12. `app/services/education_service.py` - 교육 서비스
13. `app/services/training_service.py` - 훈련 서비스
14. `app/services/admin_service.py` - 관리자 서비스

### 단계 4: 컨트롤러 레이어

15. `app/controllers/__init__.py` (빈 파일)
16. `app/controllers/auth_controller.py` - 인증 컨트롤러
17. `app/controllers/audit_controller.py` - 감사 컨트롤러
18. `app/controllers/score_controller.py` - 점수 컨트롤러
19. `app/controllers/education_controller.py` - 교육 컨트롤러
20. `app/controllers/training_controller.py` - 훈련 컨트롤러
21. `app/controllers/admin_controller.py` - 관리자 컨트롤러

### 단계 5: 앱 팩토리 및 메인 파일

22. `app/__init__.py` - Flask 앱 팩토리
23. `app.py` - 메인 진입점

## 3. 기존 파일 처리

1. **기존 mock_app.py 백업**:

   ```bash
   cp mock_app.py mock_app_backup.py
   ```

2. **Vue 빌드 파일 이동**:

   ```bash
   # 기존 static, templates 폴더가 있다면
   mv static app/static
   mv templates app/templates
   ```

3. **logs 폴더 유지**:
   ```bash
   # logs 폴더가 이미 있다면 그대로 두기
   ```

## 4. 환경 변수 설정 (선택사항)

`.env` 파일을 생성하여 환경별 설정을 관리할 수 있습니다:

```bash
# .env
FLASK_ENV=development
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=dnb123!!
DB_NAME=patch_management
JWT_SECRET=your-secret-key
```

## 5. 실행 방법

### 개발 환경

```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python app.py
```

### 운영 환경

```bash
# 환경 변수 설정
export FLASK_ENV=production

# gunicorn 등을 사용한 운영 서버 실행
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 6. 주요 개선사항

### 코드 구조

- **관심사 분리**: 각 기능별로 파일이 분리됨
- **재사용성**: 공통 로직을 서비스 레이어로 추출
- **테스트 용이성**: 각 컴포넌트를 독립적으로 테스트 가능

### 유지보수성

- **명확한 책임**: 각 파일의 역할이 명확함
- **확장성**: 새로운 기능 추가 시 해당 영역만 수정
- **디버깅**: 문제 발생 시 해당 영역을 쉽게 찾을 수 있음

### 보안 강화

- **중앙화된 인증**: 데코레이터를 통한 일관된 인증 처리
- **입력 검증**: validate_json 데코레이터로 일관된 입력 검증
- **에러 처리**: handle_exceptions 데코레이터로 안전한 에러 처리

## 7. API 엔드포인트 변경사항

### 인증 관련

- `POST /api/auth/check-credentials` - 자격증명 확인
- `POST /api/auth/email-verification` - 이메일 인증 코드 발송
- `POST /api/auth/verify-and-login` - 인증 코드 확인 및 로그인
- `GET /api/auth/me` - 사용자 정보 조회
- `POST /api/auth/logout` - 로그아웃
- `POST /api/auth/authenticate` - 사용자 인증 및 감사 로그 초기화

### 보안 감사 관련

- `GET /api/security-audit/stats` - 보안 통계 조회
- `GET /api/security-audit/logs` - 감사 로그 조회
- `GET /api/security-audit/checklist-items` - 체크리스트 항목 조회
- `POST /api/security-audit/validate_check` - 항목 검증
- `POST /api/security-audit/log` - 클라이언트 로그 수신

### 점수 관련

- `GET /api/security-score/summary` - 종합 보안 점수 조회
- `GET /api/security-score/dashboard/overview` - 대시보드 데이터 조회

### 교육 관련

- `GET /api/security-education/status` - 교육 현황 조회

### 훈련 관련

- `GET /api/phishing-training/status` - 모의훈련 현황 조회

### 관리자 관련

- `GET /api/admin/dashboard` - 관리자 대시보드
- `GET /api/admin/users` - 전체 사용자 목록
- `POST /api/admin/education/bulk-update` - 교육 결과 일괄 등록
- `POST /api/admin/training/bulk-update` - 훈련 결과 일괄 등록
- `POST /api/admin/scores/recalculate` - 전체 점수 재계산
- `GET /api/admin/users/<user_id>/details` - 사용자 상세 정보

## 8. 점수 계산 시스템

### 점수 구성

- **기본 점수**: 100점 (상시감사 통과율 기반)
- **교육 미이수 감점**: 회차당 -0.5점
- **모의훈련 미흡 감점**: 회차당 -0.5점

### 등급 기준

- A+ (95점 이상)
- A (90점 이상)
- B+ (85점 이상)
- B (80점 이상)
- C+ (75점 이상)
- C (70점 이상)
- D (60점 이상)
- F (60점 미만)

## 9. 데이터베이스 테이블 요구사항

구조화된 시스템이 올바르게 작동하려면 다음 테이블들이 필요합니다:

### 기존 테이블

- `users` - 사용자 정보
- `audit_log` - 감사 로그
- `checklist_items` - 체크리스트 항목

### 추가 필요 테이블

```sql
-- 정보보호 교육 관련 테이블
DROP TABLE IF EXISTS `security_education`;
CREATE TABLE IF NOT EXISTS `security_education` (
  `education_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `education_year` year NOT NULL,
  `quarter` tinyint(4) NOT NULL COMMENT '1=1분기, 2=2분기, 3=3분기, 4=4분기',
  `education_type` varchar(50) NOT NULL COMMENT '교육 유형 (기본교육, 심화교육 등)',
  `education_date` date DEFAULT NULL COMMENT '교육 이수일',
  `completion_status` tinyint(4) NOT NULL DEFAULT 0 COMMENT '0=미이수, 1=이수',
  `score` decimal(3,1) DEFAULT NULL COMMENT '교육 점수',
  `notes` text DEFAULT NULL COMMENT '비고',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`education_id`),
  UNIQUE KEY `unique_user_education` (`user_id`, `education_year`, `quarter`),
  KEY `idx_user_year` (`user_id`, `education_year`),
  KEY `idx_completion_status` (`completion_status`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`uid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- 악성메일 모의훈련 관련 테이블
DROP TABLE IF EXISTS `phishing_training`;
CREATE TABLE IF NOT EXISTS `phishing_training` (
  `training_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `training_year` year NOT NULL,
  `quarter` tinyint(4) NOT NULL COMMENT '1=1분기, 2=2분기, 3=3분기, 4=4분기',
  `training_date` date DEFAULT NULL COMMENT '훈련 실시일',
  `training_result` varchar(20) NOT NULL DEFAULT 'pending' COMMENT 'pass=통과, fail=실패, pending=대기',
  `clicked_phishing` tinyint(4) NOT NULL DEFAULT 0 COMMENT '0=안전, 1=피싱메일 클릭',
  `response_time` int(11) DEFAULT NULL COMMENT '신고까지 소요시간(분)',
  `training_score` decimal(3,1) DEFAULT NULL COMMENT '훈련 점수',
  `notes` text DEFAULT NULL COMMENT '비고',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`training_id`),
  UNIQUE KEY `unique_user_training` (`user_id`, `training_year`, `quarter`),
  KEY `idx_user_year` (`user_id`, `training_year`),
  KEY `idx_training_result` (`training_result`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`uid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- 종합 보안 점수 테이블
DROP TABLE IF EXISTS `security_score_summary`;
CREATE TABLE IF NOT EXISTS `security_score_summary` (
  `summary_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `evaluation_year` year NOT NULL,
  `audit_score` decimal(4,1) DEFAULT 0 COMMENT '상시감사 점수',
  `education_penalty` decimal(4,1) DEFAULT 0 COMMENT '교육 미이수 감점',
  `training_penalty` decimal(4,1) DEFAULT 0 COMMENT '모의훈련 감점',
  `total_score` decimal(4,1) DEFAULT 0 COMMENT '총 점수',
  `grade` varchar(2) DEFAULT NULL COMMENT '등급 (A+, A, B+, B, C+, C, D, F)',
  `last_calculated` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`summary_id`),
  UNIQUE KEY `unique_user_year` (`user_id`, `evaluation_year`),
  KEY `idx_total_score` (`total_score`),
  KEY `idx_grade` (`grade`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`uid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- 샘플 데이터 삽입
-- 정보보호 교육 샘플 데이터 (2025년)
INSERT INTO `security_education` (`user_id`, `education_year`, `quarter`, `education_type`, `education_date`, `completion_status`, `score`, `notes`) VALUES
(1, 2025, 1, '기본교육', '2025-03-15', 1, 85.0, '1분기 정보보호 기본교육 이수'),
(1, 2025, 2, '기본교육', NULL, 0, NULL, '2분기 교육 미이수'),
(2, 2025, 1, '기본교육', '2025-03-20', 1, 92.0, '1분기 정보보호 기본교육 이수'),
(2, 2025, 2, '기본교육', '2025-06-10', 1, 88.0, '2분기 정보보호 기본교육 이수'),
(3, 2025, 1, '기본교육', NULL, 0, NULL, '1분기 교육 미이수'),
(3, 2025, 2, '기본교육', NULL, 0, NULL, '2분기 교육 미이수'),
(4, 2025, 1, '기본교육', '2025-03-18', 1, 78.0, '1분기 정보보호 기본교육 이수'),
(4, 2025, 2, '기본교육', NULL, 0, NULL, '2분기 교육 미이수');

-- 악성메일 모의훈련 샘플 데이터 (2025년)
INSERT INTO `phishing_training` (`user_id`, `training_year`, `quarter`, `training_date`, `training_result`, `clicked_phishing`, `response_time`, `training_score`, `notes`) VALUES
(1, 2025, 1, '2025-02-28', 'pass', 0, 15, 95.0, '1분기 모의훈련 통과'),
(1, 2025, 2, '2025-05-30', 'fail', 1, NULL, 40.0, '2분기 모의훈련 실패 - 피싱메일 클릭'),
(2, 2025, 1, '2025-02-28', 'pass', 0, 8, 98.0, '1분기 모의훈련 통과'),
(2, 2025, 2, '2025-05-30', 'pass', 0, 12, 95.0, '2분기 모의훈련 통과'),
(3, 2025, 1, '2025-02-28', 'fail', 1, NULL, 30.0, '1분기 모의훈련 실패 - 피싱메일 클릭'),
(3, 2025, 2, '2025-05-30', 'fail', 1, NULL, 25.0, '2분기 모의훈련 실패 - 피싱메일 클릭'),
(4, 2025, 1, '2025-02-28', 'pass', 0, 20, 90.0, '1분기 모의훈련 통과'),
(4, 2025, 2, '2025-05-30', 'fail', 1, NULL, 35.0, '2분기 모의훈련 실패 - 피싱메일 클릭');

-- 기존 체크리스트 항목에 추가
INSERT INTO `checklist_items` (`item_id`, `category`, `item_name`, `description`) VALUES
(11, '방화벽', '방화벽 활성화 확인', '방화벽이 해제되어 있는지 확인'),
(12, '백신', '백신 상태 확인', '백신이 설치되어 있고 최신 상태인지 확인');
```

## 10. 마이그레이션 체크리스트

- [ ] 폴더 구조 생성
- [ ] 모든 Python 파일 생성
- [ ] requirements.txt 설치
- [ ] 데이터베이스 테이블 생성
- [ ] 기존 static/templates 파일 이동
- [ ] 환경 변수 설정 (선택사항)
- [ ] 테스트 실행
- [ ] 기존 mock_app.py 백업 및 제거

## 11. 트러블슈팅

### 일반적인 문제

1. **Import Error**: Python path 확인 및 `__init__.py` 파일 존재 확인
2. **데이터베이스 연결 오류**: config.py의 DB_CONFIG 설정 확인
3. **CORS 에러**: config.py의 CORS_ORIGINS 설정 확인
4. **토큰 에러**: JWT_SECRET 설정 확인

### 디버깅 팁

- `app.config['DEBUG'] = True`로 디버그 모드 활성화
- 로그 파일(`logs/server.log`) 확인
- 각 서비스를 독립적으로 테스트

이제 기존의 단일 파일 구조를 Spring Boot와 유사한 계층화된 구조로 성공적으로 마이그레이션할 수 있습니다!