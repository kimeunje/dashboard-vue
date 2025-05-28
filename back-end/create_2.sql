-- --------------------------------------------------------
-- 호스트:                          127.0.0.1
-- 서버 버전:                        11.7.2-MariaDB - mariadb.org binary distribution
-- 서버 OS:                        Win64
-- HeidiSQL 버전:                  12.10.0.7000
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- 테이블 patch_management.audit_log 구조 내보내기
DROP TABLE IF EXISTS `audit_log`;
CREATE TABLE IF NOT EXISTS `audit_log` (
  `log_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `item_id` int(11) NOT NULL,
  `actual_value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`actual_value`)),
  `passed` tinyint(4) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `checked_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`log_id`),
  KEY `item_id` (`item_id`),
  KEY `user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=718 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- 테이블 데이터 patch_management.audit_log:~11 rows (대략적) 내보내기
DELETE FROM `audit_log`;
INSERT INTO `audit_log` (`log_id`, `user_id`, `item_id`, `actual_value`, `passed`, `notes`, `checked_at`) VALUES
	(719, 3, 1, '{"screenSaverTime": "600", "screenSaverSecure": "1", "screenSaverEnabled": "1"}', 1, '화면 보호기가 정상적으로 설정되어 있습니다.', '2025-05-28 16:35:27'),
	(720, 3, 2, '{"UpToDate": 0, "DisplayName": "백신 미설치", "RealTimeProtection": 0}', 0, '알약 백신이 정상적으로 설치되어 있지 않거나, 실시간 보호가 비활성화되어 있거나, 업데이트가 최신 상태가 아닙니다. 알약 백신을 설치하고 실시간 보호를 활성화한 후 최신 업데이트를 적용해주세요.', '2025-05-28 16:35:19'),
	(721, 3, 3, '{"minimumPasswordLength": "8"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', '2025-05-28 16:35:36'),
	(722, 3, 4, '{"passwordComplexity": "1"}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', '2025-05-28 16:35:36'),
	(723, 3, 5, '{"maximumPasswordAge": "91"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', '2025-05-28 16:35:36'),
	(724, 3, 6, '{"passwordHistorySize": "5"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', '2025-05-28 16:35:36'),
	(725, 3, 7, '{"folders": ["ADMIN$", "C$", "D$", "E$", "F$", "IPC$"]}', 0, '불필요한 공유 폴더가 있습니다. 필요하지 않은 공유 폴더를 제거해주세요.', '2025-05-28 16:35:40'),
	(726, 3, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', '2025-05-28 16:35:42'),
	(727, 3, 25, '{"status": "pending", "message": "검사 대기 중"}', 0, '검사 대기 중', '2025-05-28 16:35:13'),
	(728, 3, 26, '{"status": "pending", "message": "검사 대기 중"}', 1, '검사 대기 중', '2025-05-28 16:35:13'),
	(729, 3, 27, '{"status": "pending", "message": "검사 대기 중"}', 0, '검사 대기 중', '2025-05-28 16:35:13');

-- 테이블 patch_management.checklist_items 구조 내보내기
DROP TABLE IF EXISTS `checklist_items`;
CREATE TABLE IF NOT EXISTS `checklist_items` (
  `item_id` int(11) NOT NULL AUTO_INCREMENT,
  `category` text NOT NULL,
  `item_name` text NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`item_id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- 테이블 데이터 patch_management.checklist_items:~11 rows (대략적) 내보내기
DELETE FROM `checklist_items`;
INSERT INTO `checklist_items` (`item_id`, `category`, `item_name`, `description`, `check_type`, `check_frequency`) VALUES
	(1, '접근 통제', '화면보호기 사용', '비인가자의 PC 사용 예방을 위한 화면보호기 및 잠금설정', 'daily', '매일'),
	(2, '접근 통제', '백신 상태 확인', '백신이 설치되어 있는지 확인', 'daily', '매일'),
	(3, '계정 관리', '패스워드 길이의 적정성', '비인가자의 접근제한을 위해 패스워드는 최소 길이 이상 설정해야한다.', 'daily', '매일'),
	(4, '계정 관리', '패스워드 복잡도 설정', '비인가자의 접근제한을 위해 패스워드는 2가지 이상의 복잡도를 만족해야한다.', 'daily', '매일'),
	(5, '계정 관리', '패스워드 주기적 변경', '안전한 패스워드 관리를 위해 패스워드는 주기적으로 변경해야한다.', 'daily', '매일'),
	(6, '계정 관리', '동일 패스워드 설정 제한', '패스워드 변경 시 최근 사용했던 동일한 암호설정은 제한한다.', 'daily', '매일'),
	(7, '네트워크 점검', '공유폴더 확인', '불필요한 파일 공유는 제한해야한다.', 'daily', '매일'),
	(8, '네트워크 점검', '원격데스크톱 제한', '외부에서 접근이 가능한 원격접속기능은 해제 해야한다.', 'daily', '매일'),
	(25, '물리적 보안', 'PC 봉인씰 상태 확인', 'PC 케이스의 봉인씰 훼손 여부를 육안으로 확인', 'manual', '수시'),
	(26, '악성코드 점검', '악성코드 탐지 이력 확인', '시스템에서 발견된 악성코드 탐지 이력 및 처리 현황 확인', 'manual', '수시'),
	(27, '정보보호', '개인정보 암호화 상태 확인', '개인정보가 포함된 파일의 암호화 적용 여부 확인', 'manual', '수시');

-- 테이블 patch_management.phishing_training 구조 내보내기
DROP TABLE IF EXISTS `phishing_training`;
CREATE TABLE IF NOT EXISTS `phishing_training` (
  `training_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL COMMENT '사용자 UID',
  `training_year` int(11) NOT NULL COMMENT '훈련 연도',
  `training_period` enum('first_half','second_half') NOT NULL COMMENT '훈련 기간 (상반기/하반기)',
  `email_sent_time` datetime DEFAULT NULL COMMENT '모의 메일 발송 시각',
  `action_time` datetime DEFAULT NULL COMMENT '사용자 액션 수행 시각',
  `log_type` varchar(100) DEFAULT NULL COMMENT '로그 유형 (클릭/열람 등)',
  `mail_type` varchar(200) DEFAULT NULL COMMENT '모의 메일 유형',
  `user_email` varchar(100) DEFAULT NULL COMMENT '사용자 이메일',
  `ip_address` varchar(45) DEFAULT NULL COMMENT 'IP 주소',
  `training_result` enum('pass','fail','pending') DEFAULT 'pending' COMMENT '훈련 결과',
  `response_time_minutes` int(11) DEFAULT NULL COMMENT '응답 시간 (분)',
  `training_score` decimal(5,2) DEFAULT NULL COMMENT '훈련 점수',
  `exclude_from_scoring` tinyint(1) DEFAULT 0 COMMENT '점수 계산 제외 여부',
  `notes` text DEFAULT NULL COMMENT '비고',
  `created_at` timestamp NULL DEFAULT current_timestamp() COMMENT '생성일',
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '수정일',
  PRIMARY KEY (`training_id`),
  UNIQUE KEY `unique_training` (`user_id`,`training_year`,`training_period`),
  KEY `idx_training_year` (`training_year`),
  KEY `idx_training_period` (`training_period`),
  KEY `idx_training_result` (`training_result`),
  KEY `idx_email_sent_time` (`email_sent_time`),
  CONSTRAINT `phishing_training_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='악성메일 모의훈련 현황';

-- 테이블 데이터 patch_management.phishing_training:~11 rows (대략적) 내보내기
DELETE FROM `phishing_training`;
INSERT INTO `phishing_training` (`training_id`, `user_id`, `training_year`, `training_period`, `email_sent_time`, `action_time`, `log_type`, `mail_type`, `user_email`, `ip_address`, `training_result`, `response_time_minutes`, `training_score`, `exclude_from_scoring`, `notes`, `created_at`, `updated_at`) VALUES
	(33, 2, 2024, 'first_half', '2024-05-15 10:44:25', '2024-05-15 10:44:59', '스크립트 첨부파일 열람', '퇴직연금 운용상품 안내 (HTML)', 'kim.cs@company.com', '192.168.1.101', 'fail', 1, 0.00, 0, '모의훈련 실패 - 첨부파일 열람', '2025-05-28 00:47:12', '2025-05-28 13:24:01'),
	(34, 2, 2024, 'second_half', '2024-08-22 16:32:25', '2024-08-22 16:42:25', '스크립트 첨부파일 열람', '세금계산서 안내', 'parkchul@test.com', '50.24.11.35', 'fail', 10, 0.00, 0, '', '2025-05-28 00:47:12', '2025-05-28 13:24:02'),
	(37, 4, 2024, 'first_half', '2024-05-18 13:20:10', NULL, NULL, '회사 정책 변경 안내', 'park.ms@company.com', NULL, 'pass', NULL, 0.00, 0, '모의훈련 통과', '2025-05-28 00:47:12', '2025-05-28 13:24:04'),
	(38, 4, 2024, 'second_half', '2024-11-25 16:45:20', '2024-11-25 16:50:35', '첨부파일 다운로드', '세무 관련 서류 검토 요청', 'park.ms@company.com', '192.168.1.103', 'fail', 5, 0.00, 1, '모의훈련 실패 - 점수 계산 제외', '2025-05-28 00:47:12', '2025-05-28 13:24:04'),
	(39, 2, 2025, 'first_half', '2024-05-20 09:15:30', NULL, NULL, 'IT 보안 정책 업데이트', 'kim.cs@company.com', NULL, 'pass', NULL, 0.00, 0, '모의훈련 통과 - 의심스러운 메일 신고', '2025-05-28 00:47:12', '2025-05-28 13:24:03'),
	(41, 4, 2025, 'first_half', '2025-05-25 11:20:15', NULL, NULL, '휴가 신청서 양식 변경', 'park.ms@company.com', NULL, 'pass', NULL, 0.00, 0, '모의훈련 통과', '2025-05-28 00:47:12', '2025-05-28 13:24:04'),
	(43, 1, 2025, 'first_half', '2025-04-22 10:44:25', '2025-04-22 10:34:25', '스크립트 첨부파일 열람', '세금계산서 안내', 'test1@test.com', '103.34.21.35', 'fail', -10, 0.00, 0, '', '2025-05-28 07:59:22', '2025-05-28 13:24:00'),
	(46, 4, 2025, 'second_half', '2025-10-22 10:44:25', '2025-10-22 10:54:25', '악성 메일 클릭', '운용상품 안내', 'kimeunje@test.com', '1.35.2.62', 'fail', 10, 0.00, 0, '', '2025-05-28 07:59:23', '2025-05-28 13:24:05'),
	(51, 3, 2024, 'second_half', '2024-11-15 14:30:00', NULL, NULL, 'IT 보안 정책 업데이트 안내', 'kim.cs@company.com', NULL, 'pass', NULL, 0.00, 0, '모의훈련 통과 - 의심스러운 메일에 대해 액션하지 않음', '2025-05-28 13:20:29', '2025-05-28 13:24:03'),
	(54, 3, 2024, 'first_half', '2024-03-15 14:30:00', NULL, NULL, 'IT 보안 정책 업데이트 안내', 'kim.cs@company.com', NULL, 'pass', NULL, 0.00, 0, '모의훈련 통과 - 의심스러운 메일에 대해 액션하지 않음', '2025-05-28 13:20:51', '2025-05-28 13:24:03'),
	(55, 3, 2025, 'first_half', '2025-03-22 16:32:25', '2025-03-22 16:42:25', '스크립트 첨부파일 열람', '세금계산서 안내', 'parkchul@test.com', '50.24.11.35', 'fail', 10, 0.00, 0, '', '2025-05-28 00:47:12', '2025-05-28 13:24:02');

-- 테이블 patch_management.security_education 구조 내보내기
DROP TABLE IF EXISTS `security_education`;
CREATE TABLE IF NOT EXISTS `security_education` (
  `education_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `education_year` year(4) NOT NULL,
  `education_period` enum('first_half','second_half') NOT NULL COMMENT '상반기/하반기',
  `education_type` varchar(50) NOT NULL DEFAULT '기본교육' COMMENT '교육 유형',
  `education_date` date DEFAULT NULL COMMENT '교육 이수일',
  `completion_status` tinyint(4) NOT NULL DEFAULT 0 COMMENT '0=미이수, 1=이수',
  `score` decimal(4,1) DEFAULT NULL COMMENT '교육 점수',
  `exclude_from_scoring` tinyint(1) NOT NULL DEFAULT 0 COMMENT '점수 계산 제외 여부 (1=제외, 0=포함)',
  `notes` text DEFAULT NULL COMMENT '비고',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`education_id`),
  UNIQUE KEY `unique_user_education_period` (`user_id`,`education_year`,`education_period`),
  KEY `idx_user_year` (`user_id`,`education_year`),
  KEY `idx_completion_status` (`completion_status`),
  KEY `idx_exclude_scoring` (`exclude_from_scoring`),
  CONSTRAINT `security_education_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- 테이블 데이터 patch_management.security_education:~7 rows (대략적) 내보내기
DELETE FROM `security_education`;
INSERT INTO `security_education` (`education_id`, `user_id`, `education_year`, `education_period`, `education_type`, `education_date`, `completion_status`, `score`, `exclude_from_scoring`, `notes`, `created_at`, `updated_at`) VALUES
	(1, 1, '2025', 'first_half', '기본교육', '2025-06-15', 1, 85.0, 0, '상반기 정보보호 기본교육 이수', '2025-05-27 14:09:15', '2025-05-27 14:09:15'),
	(2, 1, '2025', 'second_half', '기본교육', NULL, 0, NULL, 0, '하반기 교육 미이수', '2025-05-27 14:09:15', '2025-05-27 14:09:15'),
	(3, 2, '2025', 'first_half', '기본교육', '2025-06-20', 1, 92.0, 0, '상반기 정보보호 기본교육 이수', '2025-05-27 14:09:15', '2025-05-27 14:09:15'),
	(4, 2, '2025', 'second_half', '기본교육', '2025-12-10', 1, 88.0, 0, '하반기 정보보호 기본교육 이수', '2025-05-27 14:09:15', '2025-05-27 14:09:15'),
	(5, 3, '2025', 'first_half', '기본교육', NULL, 0, NULL, 1, '상반기 교육 미실시 - 점수 계산 제외', '2025-05-27 14:09:15', '2025-05-27 14:09:15'),
	(6, 3, '2025', 'second_half', '기본교육', NULL, 0, NULL, 0, '하반기 교육 미이수', '2025-05-27 14:09:15', '2025-05-27 14:09:15'),
	(7, 4, '2025', 'first_half', '기본교육', '2025-06-18', 1, 78.0, 0, '상반기 정보보호 기본교육 이수', '2025-05-27 14:09:15', '2025-05-27 14:09:15');

-- 테이블 patch_management.security_score_summary 구조 내보내기
DROP TABLE IF EXISTS `security_score_summary`;
CREATE TABLE IF NOT EXISTS `security_score_summary` (
  `summary_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `evaluation_year` year(4) NOT NULL,
  `audit_score` decimal(4,1) DEFAULT 100.0 COMMENT '상시감사 점수 (기본 100점)',
  `education_penalty` decimal(4,1) DEFAULT 0.0 COMMENT '교육 미이수 감점',
  `training_penalty` decimal(4,1) DEFAULT 0.0 COMMENT '모의훈련 감점',
  `total_score` decimal(4,1) DEFAULT 100.0 COMMENT '총 점수',
  `grade` varchar(2) DEFAULT NULL COMMENT '등급 (A+, A, B+, B, C+, C, D, F)',
  `education_completed_count` int(11) DEFAULT 0 COMMENT '교육 이수 횟수',
  `education_total_count` int(11) DEFAULT 0 COMMENT '교육 대상 총 횟수',
  `training_passed_count` int(11) DEFAULT 0 COMMENT '모의훈련 통과 횟수',
  `training_total_count` int(11) DEFAULT 0 COMMENT '모의훈련 대상 총 횟수',
  `last_calculated` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`summary_id`),
  UNIQUE KEY `unique_user_year` (`user_id`,`evaluation_year`),
  KEY `idx_total_score` (`total_score`),
  KEY `idx_grade` (`grade`),
  CONSTRAINT `security_score_summary_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- 테이블 데이터 patch_management.security_score_summary:~0 rows (대략적) 내보내기
DELETE FROM `security_score_summary`;

-- 테이블 patch_management.users 구조 내보내기
DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `uid` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(50) NOT NULL,
  `username` varchar(50) NOT NULL,
  `mail` varchar(255) DEFAULT NULL,
  `department` varchar(50) NOT NULL,
  `last_updated` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`uid`) USING BTREE,
  UNIQUE KEY `uc_user_emp` (`user_id`,`username`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- 테이블 데이터 patch_management.users:~4 rows (대략적) 내보내기
DELETE FROM `users`;
INSERT INTO `users` (`uid`, `user_id`, `username`, `mail`, `department`, `last_updated`) VALUES
	(1, 'test1', '테스터1', 'test1@test.com', '운영실', '2025-05-28 14:58:32'),
	(2, 'parkchul', '박철희', 'parkchul@test.com', '개발팀', '2025-05-21 08:15:45'),
	(3, 'test', '테스터', 'test@test.com', '운영실', '2025-05-28 14:58:43'),
	(4, 'kimeunje', '김은제', 'kimeunje@test.com', '운영실', '2025-05-21 08:15:41');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
