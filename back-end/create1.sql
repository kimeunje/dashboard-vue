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
  `log_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL COMMENT 'users 테이블의 uid 참조',
  `item_id` int(11) NOT NULL COMMENT 'checklist_items 테이블 참조',
  `actual_value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT '실제 측정값' CHECK (json_valid(`actual_value`)),
  `passed` tinyint(1) DEFAULT NULL COMMENT '통과 여부 (1:통과, 0:실패, NULL:대기)',
  `notes` text DEFAULT NULL COMMENT '비고',
  `checked_at` timestamp NULL DEFAULT current_timestamp() COMMENT '점검 일시',
  PRIMARY KEY (`log_id`),
  KEY `idx_user_item` (`user_id`,`item_id`),
  KEY `idx_checked_at` (`checked_at`),
  KEY `fk_audit_log_item` (`item_id`),
  CONSTRAINT `fk_audit_log_item` FOREIGN KEY (`item_id`) REFERENCES `checklist_items` (`item_id`),
  CONSTRAINT `fk_audit_log_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='보안 감사 로그';

-- 테이블 데이터 patch_management.audit_log:~11 rows (대략적) 내보내기
DELETE FROM `audit_log`;
INSERT INTO `audit_log` (`log_id`, `user_id`, `item_id`, `actual_value`, `passed`, `notes`, `checked_at`) VALUES
	(9, 3, 1, '{"screenSaverTime": "600", "screenSaverSecure": "1", "screenSaverEnabled": "1"}', 1, '화면 보호기가 정상적으로 설정되어 있습니다.', '2025-06-03 13:18:17'),
	(10, 3, 2, '{"UpToDate": 0, "DisplayName": "백신 미설치", "RealTimeProtection": 0}', 0, '알약 백신이 정상적으로 설치되어 있지 않거나, 실시간 보호가 비활성화되어 있거나, 업데이트가 최신 상태가 아닙니다. 알약 백신을 설치하고 실시간 보호를 활성화한 후 최신 업데이트를 적용해주세요.', '2025-06-03 13:18:10'),
	(11, 3, 3, '{"minimumPasswordLength": "8"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', '2025-06-03 13:18:27'),
	(12, 3, 4, '{"passwordComplexity": "0"}', 0, '암호 복잡도가 설정되어 있지 않습니다. 암호 복잡도 설정을 활성화해주세요.', '2025-06-03 13:18:27'),
	(13, 3, 5, '{"maximumPasswordAge": "91"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', '2025-06-03 13:18:27'),
	(14, 3, 6, '{"passwordHistorySize": "5"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', '2025-06-03 13:18:27'),
	(15, 3, 7, '{"folders": ["ADMIN$", "C$", "D$", "E$", "F$", "G$", "IPC$"]}', 0, '불필요한 공유 폴더가 있습니다. 필요하지 않은 공유 폴더를 제거해주세요.', '2025-06-03 13:18:30'),
	(16, 3, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', '2025-06-03 13:18:33'),
	(17, 3, 9, '{"status": "pending", "message": "검사 대기 중"}', 0, '검사 대기 중', '2025-06-03 13:18:03'),
	(18, 3, 10, '{"status": "pending", "message": "검사 대기 중"}', 0, '검사 대기 중', '2025-06-03 13:18:03'),
	(19, 3, 11, '{"status": "pending", "message": "검사 대기 중"}', 0, '검사 대기 중', '2025-06-03 13:18:03');

-- 테이블 patch_management.checklist_items 구조 내보내기
DROP TABLE IF EXISTS `checklist_items`;
CREATE TABLE IF NOT EXISTS `checklist_items` (
  `item_id` int(11) NOT NULL AUTO_INCREMENT,
  `item_name` varchar(255) NOT NULL COMMENT '점검 항목명',
  `category` varchar(100) NOT NULL COMMENT '카테고리',
  `description` text DEFAULT NULL COMMENT '상세 설명',
  `check_type` enum('daily','manual') NOT NULL DEFAULT 'daily' COMMENT '점검 유형 (정기/수시)',
  `check_frequency` varchar(50) DEFAULT 'daily' COMMENT '점검 주기',
  `penalty_weight` decimal(3,1) DEFAULT 0.5 COMMENT '감점 가중치 (기본 0.5점)',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`item_id`),
  KEY `idx_check_type` (`check_type`),
  KEY `idx_category` (`category`)
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='보안 점검 항목';

-- 테이블 데이터 patch_management.checklist_items:~11 rows (대략적) 내보내기
DELETE FROM `checklist_items`;
INSERT INTO `checklist_items` (`item_id`, `item_name`, `category`, `description`, `check_type`, `check_frequency`, `penalty_weight`, `created_at`, `updated_at`) VALUES
	(1, '화면보호기 사용', '접근통제', '화면보호기 설정 및 시간 확인', 'daily', 'daily', 0.5, '2025-06-03 12:44:38', '2025-06-03 12:44:38'),
	(2, '백신 상태 확인', '악성코드', '백신 설치 및 업데이트 상태 확인', 'daily', 'daily', 0.5, '2025-06-03 12:44:38', '2025-06-03 13:16:36'),
	(3, '패스워드 길이의 적정성', '접근통제', '최소 패스워드 길이 정책 확인', 'daily', 'daily', 0.5, '2025-06-03 12:44:38', '2025-06-03 13:16:43'),
	(4, '패스워드 복잡도 설정', '접근통제', '패스워드 복잡도 정책 확인', 'daily', 'daily', 0.5, '2025-06-03 12:44:38', '2025-06-03 13:16:47'),
	(5, '패스워드 주기적 변경', '접근통제', '패스워드 주기적 변경 정책 확인', 'daily', 'daily', 0.5, '2025-06-03 12:44:38', '2025-06-03 13:16:51'),
	(6, '동일 패스워드 설정 제한', '접근통제', '동일 패스워드 설정 정책 확인', 'daily', 'daily', 0.5, '2025-06-03 12:44:38', '2025-06-03 13:16:53'),
	(7, '공유폴더 확인', '접근통제', '공유폴더 설정 확인', 'daily', 'daily', 0.5, '2025-06-03 12:44:38', '2025-06-03 13:16:59'),
	(8, '원격데스크톱 제한', '접근통제', '원격 데스크톱 연결 제한 설정', 'daily', 'daily', 0.5, '2025-06-03 12:44:38', '2025-06-03 13:17:02'),
	(9, 'PC 봉인씰 확인', '물리보안', 'PC 봉인씰 상태 점검', 'manual', 'daily', 0.5, '2025-06-03 12:44:38', '2025-06-03 13:17:06'),
	(10, '악성코드 전체 검사', '악성코드', '전체 시스템 악성코드 검사', 'manual', 'daily', 0.5, '2025-06-03 12:44:38', '2025-06-03 13:17:07'),
	(11, '개인정보 파일 암호화', '개인정보보호', '개인정보 파일 암호화 적용 여부', 'manual', 'daily', 0.5, '2025-06-03 12:44:38', '2025-06-03 12:44:38');

-- 테이블 patch_management.phishing_training 구조 내보내기
DROP TABLE IF EXISTS `phishing_training`;
CREATE TABLE IF NOT EXISTS `phishing_training` (
  `training_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL COMMENT 'users 테이블의 uid 참조',
  `training_year` int(11) NOT NULL COMMENT '훈련 연도',
  `training_period` enum('first_half','second_half') NOT NULL COMMENT '훈련 기간 (상반기/하반기)',
  `email_sent_time` datetime DEFAULT NULL COMMENT '메일 발송 시각',
  `action_time` datetime DEFAULT NULL COMMENT '사용자 액션 시각',
  `log_type` varchar(100) DEFAULT NULL COMMENT '로그 유형 (클릭/열람 등)',
  `mail_type` varchar(200) DEFAULT NULL COMMENT '메일 유형',
  `user_email` varchar(255) DEFAULT NULL COMMENT '사용자 이메일',
  `ip_address` varchar(45) DEFAULT NULL COMMENT 'IP 주소',
  `training_result` enum('pass','fail','pending') DEFAULT 'pending' COMMENT '훈련 결과',
  `response_time_minutes` int(11) DEFAULT NULL COMMENT '응답 시간 (분)',
  `training_score` decimal(5,2) DEFAULT NULL COMMENT '훈련 점수',
  `exclude_from_scoring` tinyint(1) DEFAULT 0 COMMENT '점수 계산 제외 여부',
  `notes` text DEFAULT NULL COMMENT '비고',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`training_id`),
  UNIQUE KEY `uk_user_training` (`user_id`,`training_year`,`training_period`),
  KEY `idx_training_year` (`training_year`),
  CONSTRAINT `fk_training_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='악성메일 모의훈련 이력';

-- 테이블 데이터 patch_management.phishing_training:~4 rows (대략적) 내보내기
DELETE FROM `phishing_training`;
INSERT INTO `phishing_training` (`training_id`, `user_id`, `training_year`, `training_period`, `email_sent_time`, `action_time`, `log_type`, `mail_type`, `user_email`, `ip_address`, `training_result`, `response_time_minutes`, `training_score`, `exclude_from_scoring`, `notes`, `created_at`, `updated_at`) VALUES
	(1, 3, 2025, 'first_half', NULL, NULL, '첨부파일 열람', NULL, NULL, NULL, 'fail', NULL, NULL, 0, '상반기 모의훈련 실패 - 첨부파일 열람', '2025-06-03 12:44:38', '2025-06-03 12:44:38'),
	(2, 3, 2025, 'second_half', NULL, NULL, NULL, NULL, NULL, NULL, 'pending', NULL, NULL, 0, '하반기 모의훈련 미실시', '2025-06-03 12:44:38', '2025-06-03 12:44:38'),
	(3, 3, 2024, 'first_half', NULL, NULL, NULL, NULL, NULL, NULL, 'pass', NULL, NULL, 0, '상반기 모의훈련 통과', '2025-06-03 12:44:38', '2025-06-03 12:44:38'),
	(4, 3, 2024, 'second_half', NULL, NULL, NULL, NULL, NULL, NULL, 'pass', NULL, NULL, 0, '하반기 모의훈련 통과', '2025-06-03 12:44:38', '2025-06-03 12:44:38');

-- 테이블 patch_management.security_education 구조 내보내기
DROP TABLE IF EXISTS `security_education`;
CREATE TABLE IF NOT EXISTS `security_education` (
  `education_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL COMMENT 'users 테이블의 uid 참조',
  `education_year` int(11) NOT NULL COMMENT '교육 연도',
  `education_period` enum('first_half','second_half') NOT NULL COMMENT '교육 기간 (상반기/하반기)',
  `education_type` varchar(100) DEFAULT '기본교육' COMMENT '교육 유형',
  `education_date` date DEFAULT NULL COMMENT '교육 수료일',
  `completion_status` tinyint(1) DEFAULT 0 COMMENT '이수 여부 (1:이수, 0:미이수)',
  `score` decimal(5,2) DEFAULT NULL COMMENT '교육 점수',
  `exclude_from_scoring` tinyint(1) DEFAULT 0 COMMENT '점수 계산 제외 여부',
  `notes` text DEFAULT NULL COMMENT '비고',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`education_id`),
  UNIQUE KEY `uk_user_education` (`user_id`,`education_year`,`education_period`),
  KEY `idx_education_year` (`education_year`),
  CONSTRAINT `fk_education_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='정보보호 교육 이력';

-- 테이블 데이터 patch_management.security_education:~4 rows (대략적) 내보내기
DELETE FROM `security_education`;
INSERT INTO `security_education` (`education_id`, `user_id`, `education_year`, `education_period`, `education_type`, `education_date`, `completion_status`, `score`, `exclude_from_scoring`, `notes`, `created_at`, `updated_at`) VALUES
	(1, 3, 2025, 'first_half', '기본교육', NULL, 0, NULL, 0, '상반기 교육 미이수', '2025-06-03 12:44:38', '2025-06-03 12:44:38'),
	(2, 3, 2025, 'second_half', '기본교육', NULL, 0, NULL, 0, '하반기 교육 미실시', '2025-06-03 12:44:38', '2025-06-03 12:44:38'),
	(3, 3, 2024, 'first_half', '기본교육', NULL, 1, NULL, 0, '상반기 교육 이수 완료', '2025-06-03 12:44:38', '2025-06-03 12:44:38'),
	(4, 3, 2024, 'second_half', '기본교육', NULL, 1, NULL, 0, '하반기 교육 이수 완료', '2025-06-03 12:44:38', '2025-06-03 12:44:38');

-- 테이블 patch_management.security_score_summary 구조 내보내기
DROP TABLE IF EXISTS `security_score_summary`;
CREATE TABLE IF NOT EXISTS `security_score_summary` (
  `summary_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL COMMENT 'users 테이블의 uid 참조',
  `evaluation_year` int(11) NOT NULL COMMENT '평가 연도',
  `audit_penalty` decimal(5,2) DEFAULT 0.00 COMMENT '감사 감점 (실패 항목 * 0.5)',
  `education_penalty` decimal(5,2) DEFAULT 0.00 COMMENT '교육 감점 (미이수 * 0.5)',
  `training_penalty` decimal(5,2) DEFAULT 0.00 COMMENT '모의훈련 감점 (실패 * 0.5)',
  `total_penalty` decimal(5,2) DEFAULT 0.00 COMMENT '총 감점 (최대 -5.0점)',
  `audit_failed_count` int(11) DEFAULT 0 COMMENT '감사 실패 항목 수',
  `education_incomplete_count` int(11) DEFAULT 0 COMMENT '교육 미이수 횟수',
  `training_failed_count` int(11) DEFAULT 0 COMMENT '모의훈련 실패 횟수',
  `last_calculated` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`summary_id`),
  UNIQUE KEY `uk_user_year` (`user_id`,`evaluation_year`),
  KEY `idx_evaluation_year` (`evaluation_year`),
  CONSTRAINT `fk_score_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=89 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='KPI 보안 점수 요약 (감점 기준)';

-- 테이블 데이터 patch_management.security_score_summary:~5 rows (대략적) 내보내기
DELETE FROM `security_score_summary`;
INSERT INTO `security_score_summary` (`summary_id`, `user_id`, `evaluation_year`, `audit_penalty`, `education_penalty`, `training_penalty`, `total_penalty`, `audit_failed_count`, `education_incomplete_count`, `training_failed_count`, `last_calculated`, `created_at`) VALUES
	(1, 3, 2025, 3.00, 1.00, 0.50, 4.50, 6, 2, 1, '2025-06-03 14:29:19', '2025-06-03 12:52:56'),
	(2, 3, 2023, 0.00, 1.00, 0.00, 1.00, 0, 2, 0, '2025-06-03 14:29:19', '2025-06-03 12:52:56'),
	(3, 3, 2024, 0.00, 0.00, 0.00, 0.00, 0, 0, 0, '2025-06-03 14:29:19', '2025-06-03 12:52:56'),
	(10, 3, 2022, 0.00, 1.00, 0.00, 1.00, 0, 2, 0, '2025-06-03 13:46:57', '2025-06-03 12:54:03'),
	(57, 3, 2026, 0.00, 1.00, 0.00, 1.00, 0, 2, 0, '2025-06-03 13:47:01', '2025-06-03 13:46:58');

-- 테이블 patch_management.users 구조 내보내기
DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `uid` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'JPA에서 Long 타입으로 매핑',
  `user_id` varchar(50) NOT NULL COMMENT '사용자 로그인 ID',
  `username` varchar(50) NOT NULL COMMENT '사용자 실명',
  `mail` varchar(255) DEFAULT NULL COMMENT '이메일 주소',
  `department` varchar(100) DEFAULT NULL COMMENT '소속 부서',
  `created_at` timestamp NULL DEFAULT current_timestamp() COMMENT '생성일시',
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '수정일시',
  `last_updated` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '최종 업데이트 (기존 호환)',
  PRIMARY KEY (`uid`),
  UNIQUE KEY `uk_user_id` (`user_id`),
  KEY `idx_username` (`username`),
  KEY `idx_department` (`department`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 정보';

-- 테이블 데이터 patch_management.users:~6 rows (대략적) 내보내기
DELETE FROM `users`;
INSERT INTO `users` (`uid`, `user_id`, `username`, `mail`, `department`, `created_at`, `updated_at`, `last_updated`) VALUES
	(1, 'test1', '테스터1', 'test1@test.com', '운영실', '2025-06-03 11:51:13', '2025-06-03 11:51:13', '2025-06-03 11:51:13'),
	(2, 'parkchul', '박철희', 'parkchul@test.com', '개발팀', '2025-06-03 11:51:13', '2025-06-03 11:51:13', '2025-06-03 11:51:13'),
	(3, 'eunjekim8', '김은제', 'test@test.com', '운영실', '2025-06-03 11:51:13', '2025-06-03 11:51:13', '2025-06-03 11:51:13'),
	(4, 'kimeunje', '김은제2', 'kimeunje@test.com', '운영실', '2025-06-03 11:51:13', '2025-06-03 11:51:13', '2025-06-03 11:51:13'),
	(5, 'admin', '관리자', 'admin@test.com', 'IT팀', '2025-06-03 11:51:13', '2025-06-03 11:51:13', '2025-06-03 11:51:13'),
	(6, 'test', '테스터', 'test@test.com', '운영실', '2025-06-03 11:51:13', '2025-06-03 11:51:13', '2025-06-03 11:51:13');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
