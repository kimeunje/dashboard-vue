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


-- patch_management 데이터베이스 구조 내보내기
DROP DATABASE IF EXISTS `patch_management`;
CREATE DATABASE IF NOT EXISTS `patch_management` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci */;
USE `patch_management`;

-- 테이블 patch_management.audit_log 구조 내보내기
DROP TABLE IF EXISTS `audit_log`;
CREATE TABLE IF NOT EXISTS `audit_log` (
  `log_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL COMMENT 'users 테이블의 uid 참조',
  `item_id` int(11) NOT NULL COMMENT 'checklist_items 테이블 참조',
  `actual_value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT '실제 측정값' CHECK (json_valid(`actual_value`)),
  `passed` tinyint(1) DEFAULT NULL COMMENT '통과 여부 (1:통과, 0:실패, NULL:대기)',
  `notes` text DEFAULT NULL COMMENT '비고',
  `exclude_reason` varchar(255) DEFAULT NULL COMMENT '점수 제외 사유',
  `checked_at` timestamp NULL DEFAULT current_timestamp() COMMENT '점검 일시',
  PRIMARY KEY (`log_id`),
  KEY `idx_user_item` (`user_id`,`item_id`),
  KEY `idx_checked_at` (`checked_at`),
  KEY `fk_audit_log_item` (`item_id`),
  KEY `idx_audit_log_user_item_date` (`user_id`,`item_id`,`checked_at`),
  CONSTRAINT `fk_audit_log_item` FOREIGN KEY (`item_id`) REFERENCES `checklist_items` (`item_id`),
  CONSTRAINT `fk_audit_log_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='보안 감사 로그';

-- 테이블 데이터 patch_management.audit_log:~33 rows (대략적) 내보내기
DELETE FROM `audit_log`;
INSERT INTO `audit_log` (`log_id`, `user_id`, `item_id`, `actual_value`, `passed`, `notes`, `exclude_reason`, `checked_at`) VALUES
	(20, 3, 1, '{"screenSaverTime": "600", "screenSaverSecure": "1", "screenSaverEnabled": "1"}', 1, '화면 보호기가 정상적으로 설정되어 있습니다.', NULL, '2025-06-04 01:49:16'),
	(21, 3, 2, '{"UpToDate": 1, "DisplayName": "알약", "RealTimeProtection": 1}', 1, '알약 백신이 정상적으로 설치되어 있으며, 실시간 보호 및 최신 업데이트가 적용되어 있습니다.', NULL, '2025-06-04 01:49:08'),
	(22, 3, 3, '{"minimumPasswordLength": "8"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-06-04 01:49:25'),
	(23, 3, 4, '{"passwordComplexity": "1"}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-06-04 01:49:25'),
	(24, 3, 5, '{"maximumPasswordAge": "90"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다. [제외사유: dqwdqwd]', 'dqwdqwd', '2025-06-04 01:49:25'),
	(25, 3, 6, '{"passwordHistorySize": "5"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-06-04 01:49:25'),
	(26, 3, 7, '{"folders": ["IPC$", "Users", "공유폴더"]}', 0, '불필요한 공유 폴더가 있습니다. 필요하지 않은 공유 폴더를 제거해주세요. [제외사유: 3123123]', '3123123', '2025-06-04 01:49:29'),
	(27, 3, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-06-04 01:49:32'),
	(28, 3, 9, '{"status": "pending", "message": "검사 대기 중"}', 0, '검사 대기 중', NULL, '2025-06-04 01:49:00'),
	(29, 3, 10, '{"status": "pending", "message": "검사 대기 중"}', 0, '검사 대기 중', NULL, '2025-06-04 01:49:00'),
	(30, 3, 11, '{"status": "pending", "message": "검사 대기 중"}', 0, '검사 대기 중', NULL, '2025-06-04 01:49:00'),
	(31, 3, 1, '{"screenSaverTime": "600", "screenSaverSecure": "1", "screenSaverEnabled": "1"}', 1, '화면 보호기가 정상적으로 설정되어 있습니다.', NULL, '2025-06-03 02:29:00'),
	(32, 3, 2, '{"UpToDate": 1, "DisplayName": "알약", "RealTimeProtection": 1}', 1, '알약 백신이 정상적으로 설치되어 있으며, 실시간 보호 및 최신 업데이트가 적용되어 있습니다.', NULL, '2025-06-03 02:28:51'),
	(33, 3, 3, '{"minimumPasswordLength": "8"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-06-03 02:29:12'),
	(34, 3, 4, '{"passwordComplexity": "0"}', 0, '암호 복잡도가 설정되어 있지 않습니다. 암호 복잡도 설정을 활성화해주세요.', NULL, '2025-06-03 02:29:12'),
	(35, 3, 5, '{"maximumPasswordAge": "90"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다. [제외사유: dqwdqwd]', 'dqwdqwd', '2025-06-03 02:29:12'),
	(36, 3, 6, '{"passwordHistorySize": "5"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-06-03 02:29:12'),
	(37, 3, 7, '{"folders": ["IPC$", "Users", "공유폴더"]}', 0, '불필요한 공유 폴더가 있습니다. 필요하지 않은 공유 폴더를 제거해주세요. [제외사유: 3123123]', '3123123', '2025-06-03 02:29:16'),
	(38, 3, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-06-03 02:29:19'),
	(39, 3, 9, '{"status": "pending", "message": "검사 대기 중"}', 0, '검사 대기 중', NULL, '2025-06-03 02:15:16'),
	(40, 3, 10, '{"status": "pending", "message": "검사 대기 중"}', 0, '검사 대기 중', NULL, '2025-06-03 02:15:16'),
	(41, 3, 11, '{"status": "pending", "message": "검사 대기 중"}', 0, '검사 대기 중', NULL, '2025-06-03 02:15:16'),
	(42, 3, 1, '{"screenSaverTime": "600", "screenSaverSecure": "1", "screenSaverEnabled": "1"}', 1, '화면 보호기가 정상적으로 설정되어 있습니다.', NULL, '2025-06-05 06:53:50'),
	(43, 3, 2, '{"UpToDate": 1, "DisplayName": "알약", "RealTimeProtection": 1}', 1, '알약 백신이 정상적으로 설치되어 있으며, 실시간 보호 및 최신 업데이트가 적용되어 있습니다.', NULL, '2025-06-05 06:53:42'),
	(44, 3, 3, '{"minimumPasswordLength": "8"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-06-05 06:54:01'),
	(45, 3, 4, '{"passwordComplexity": "0"}', 0, '암호 복잡도가 설정되어 있지 않습니다. 암호 복잡도 설정을 활성화해주세요. [제외사유: 23435235]', '23435235', '2025-06-05 06:54:01'),
	(46, 3, 5, '{"maximumPasswordAge": "90"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다. [제외사유: dqwdqwd]', 'dqwdqwd', '2025-06-05 06:54:01'),
	(47, 3, 6, '{"passwordHistorySize": "5"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-06-05 06:54:01'),
	(48, 3, 7, '{"folders": ["IPC$", "Users", "공유폴더"]}', 0, '불필요한 공유 폴더가 있습니다. 필요하지 않은 공유 폴더를 제거해주세요. [제외사유: 3123123]', '3123123', '2025-06-05 06:54:04'),
	(49, 3, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-06-05 06:54:08'),
	(50, 3, 9, '{"status": "pending", "message": "검사 대기 중"}', 0, '검사 대기 중', NULL, '2025-06-05 06:53:34'),
	(51, 3, 10, '{"status": "pending", "message": "검사 대기 중"}', 0, '검사 대기 중', NULL, '2025-06-05 06:53:34'),
	(52, 3, 11, '{"status": "pending", "message": "검사 대기 중"}', 0, '검사 대기 중', NULL, '2025-06-05 06:53:34');

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
  KEY `idx_category` (`category`),
  KEY `idx_checklist_items_type` (`check_type`,`item_id`)
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

-- 테이블 patch_management.department_extended_exceptions 구조 내보내기
DROP TABLE IF EXISTS `department_extended_exceptions`;
CREATE TABLE IF NOT EXISTS `department_extended_exceptions` (
  `dept_exception_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `department` varchar(100) NOT NULL COMMENT '부서명',
  `item_id` varchar(100) NOT NULL COMMENT '항목 ID (정수형: 감사항목, 문자형: 교육/훈련)',
  `item_type` enum('audit_item','training_period','education_period') NOT NULL COMMENT '항목 유형',
  `item_name` varchar(255) NOT NULL COMMENT '항목명 (비정규화)',
  `item_category` varchar(100) NOT NULL COMMENT '항목 카테고리 (비정규화)',
  `exclude_reason` varchar(500) NOT NULL COMMENT '제외 사유',
  `exclude_type` enum('permanent','temporary') DEFAULT 'permanent' COMMENT '제외 유형',
  `start_date` date DEFAULT NULL COMMENT '제외 시작일 (temporary인 경우)',
  `end_date` date DEFAULT NULL COMMENT '제외 종료일 (temporary인 경우)',
  `created_by` varchar(50) NOT NULL COMMENT '설정한 관리자',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `is_active` tinyint(1) DEFAULT 1 COMMENT '활성 상태',
  PRIMARY KEY (`dept_exception_id`),
  UNIQUE KEY `uk_dept_extended_exception` (`department`,`item_id`,`item_type`),
  KEY `idx_department_extended` (`department`),
  KEY `idx_item_type_dept_extended` (`item_type`),
  KEY `idx_active_dept_extended` (`is_active`),
  KEY `idx_dept_item_category` (`item_category`),
  KEY `idx_dept_extended_search` (`department`,`item_type`,`is_active`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='부서별 확장 감사 항목 제외 설정 (감사/교육/훈련)';

-- 테이블 데이터 patch_management.department_extended_exceptions:~0 rows (대략적) 내보내기
DELETE FROM `department_extended_exceptions`;

-- 테이블 patch_management.department_item_exceptions 구조 내보내기
DROP TABLE IF EXISTS `department_item_exceptions`;
CREATE TABLE IF NOT EXISTS `department_item_exceptions` (
  `dept_exception_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `department` varchar(100) NOT NULL COMMENT '부서명',
  `item_id` int(11) NOT NULL COMMENT 'checklist_items 테이블 참조',
  `exclude_reason` varchar(255) NOT NULL COMMENT '제외 사유',
  `exclude_type` enum('permanent','temporary') DEFAULT 'permanent' COMMENT '제외 유형',
  `start_date` date DEFAULT NULL COMMENT '제외 시작일 (temporary인 경우)',
  `end_date` date DEFAULT NULL COMMENT '제외 종료일 (temporary인 경우)',
  `created_by` varchar(50) NOT NULL COMMENT '설정한 관리자',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `is_active` tinyint(1) DEFAULT 1 COMMENT '활성 상태',
  `item_type` varchar(50) DEFAULT 'audit' COMMENT '항목 유형 (audit/education/training)',
  `item_name` varchar(255) DEFAULT '' COMMENT '항목명 (중복 저장)',
  `item_category` varchar(100) DEFAULT '' COMMENT '항목 카테고리 (중복 저장)',
  PRIMARY KEY (`dept_exception_id`),
  UNIQUE KEY `uk_dept_item_exception` (`department`,`item_id`),
  KEY `idx_department` (`department`),
  KEY `idx_item_id_dept` (`item_id`),
  KEY `idx_active_dept` (`is_active`),
  KEY `idx_dept_exceptions_type` (`department`,`item_type`,`is_active`),
  CONSTRAINT `fk_dept_exception_item` FOREIGN KEY (`item_id`) REFERENCES `checklist_items` (`item_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='부서별 감사 항목 제외 설정';

-- 테이블 데이터 patch_management.department_item_exceptions:~0 rows (대략적) 내보내기
DELETE FROM `department_item_exceptions`;

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
  `notes` text DEFAULT NULL COMMENT '비고',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`training_id`),
  UNIQUE KEY `uk_user_training` (`user_id`,`training_year`,`training_period`),
  KEY `idx_training_year` (`training_year`),
  CONSTRAINT `fk_training_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=335 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='악성메일 모의훈련 이력';

-- 테이블 데이터 patch_management.phishing_training:~18 rows (대략적) 내보내기
DELETE FROM `phishing_training`;
INSERT INTO `phishing_training` (`training_id`, `user_id`, `training_year`, `training_period`, `email_sent_time`, `action_time`, `log_type`, `mail_type`, `user_email`, `ip_address`, `training_result`, `response_time_minutes`, `notes`, `created_at`, `updated_at`) VALUES
	(47, 5, 2024, 'first_half', '2024-04-22 10:44:25', '2024-10-22 10:45:25', '스크립트 첨부파일 열람', '퇴직연금 운용상품 안내 (HTML)', 'admin@test.com', '1.34.52.46', 'fail', 263521, '', '2025-06-05 07:35:40', '2025-06-05 07:35:40'),
	(49, 3, 2024, 'second_half', '2024-11-20 10:44:25', '2025-04-22 10:34:25', '스크립트 첨부파일 열람', '세금계산서 안내', 'test@test.com', '103.34.21.35', 'fail', 220310, '', '2025-06-05 07:35:40', '2025-06-05 07:35:40'),
	(292, 3, 2024, 'first_half', NULL, NULL, NULL, NULL, NULL, NULL, 'pass', NULL, '기간 완료로 인한 자동 통과 처리', '2025-06-08 10:35:59', '2025-06-08 10:35:59'),
	(293, 4, 2024, 'first_half', NULL, NULL, NULL, NULL, NULL, NULL, 'pass', NULL, '기간 완료로 인한 자동 통과 처리', '2025-06-08 10:35:59', '2025-06-08 10:35:59'),
	(294, 2, 2024, 'first_half', NULL, NULL, NULL, NULL, NULL, NULL, 'pass', NULL, '기간 완료로 인한 자동 통과 처리', '2025-06-08 10:35:59', '2025-06-08 10:35:59'),
	(295, 6, 2024, 'first_half', NULL, NULL, NULL, NULL, NULL, NULL, 'pass', NULL, '기간 완료로 인한 자동 통과 처리', '2025-06-08 10:35:59', '2025-06-08 10:35:59'),
	(296, 1, 2024, 'first_half', NULL, NULL, NULL, NULL, NULL, NULL, 'pass', NULL, '기간 완료로 인한 자동 통과 처리', '2025-06-08 10:35:59', '2025-06-08 10:35:59'),
	(299, 5, 2024, 'second_half', NULL, NULL, NULL, NULL, NULL, NULL, 'pass', NULL, '기간 완료로 인한 자동 통과 처리', '2025-06-08 10:36:00', '2025-06-08 10:36:00'),
	(300, 4, 2024, 'second_half', NULL, NULL, NULL, NULL, NULL, NULL, 'pass', NULL, '기간 완료로 인한 자동 통과 처리', '2025-06-08 10:36:00', '2025-06-08 10:36:00'),
	(301, 2, 2024, 'second_half', NULL, NULL, NULL, NULL, NULL, NULL, 'pass', NULL, '기간 완료로 인한 자동 통과 처리', '2025-06-08 10:36:00', '2025-06-08 10:36:00'),
	(302, 6, 2024, 'second_half', NULL, NULL, NULL, NULL, NULL, NULL, 'pass', NULL, '기간 완료로 인한 자동 통과 처리', '2025-06-08 10:36:00', '2025-06-08 10:36:00'),
	(303, 1, 2024, 'second_half', NULL, NULL, NULL, NULL, NULL, NULL, 'pass', NULL, '기간 완료로 인한 자동 통과 처리', '2025-06-08 10:36:00', '2025-06-08 10:36:00'),
	(319, 5, 2025, 'first_half', '2025-06-03 09:00:00', '2025-06-03 10:33:00', '이메일 열람', '카카오톡', 'admin@test.com', '10.24.11.3', 'fail', 93, '', '2025-06-08 12:31:57', '2025-06-08 12:32:15'),
	(320, 3, 2025, 'first_half', '2025-06-03 09:00:00', '2025-06-03 10:33:00', '스크립트 첨부파일 열람', '세금계산서', 'eunjekim8@test.com', '10.24.11.3', 'fail', 93, '', '2025-06-08 12:31:57', '2025-06-08 12:32:15'),
	(322, 2, 2025, 'first_half', '2025-06-03 09:00:00', '2025-06-03 10:33:00', '스크립트 첨부파일 열람', '퇴직연금 운용', 'parkchul@test.com', '10.24.11.3', 'fail', 93, '', '2025-06-08 12:31:57', '2025-06-09 00:18:57'),
	(332, 4, 2025, 'first_half', NULL, NULL, NULL, NULL, NULL, NULL, 'pass', NULL, '기간 완료로 인한 자동 통과 처리', '2025-06-09 05:10:44', '2025-06-09 05:10:44'),
	(333, 6, 2025, 'first_half', NULL, NULL, NULL, NULL, NULL, NULL, 'pass', NULL, '기간 완료로 인한 자동 통과 처리', '2025-06-09 05:10:44', '2025-06-09 05:10:44'),
	(334, 1, 2025, 'first_half', NULL, NULL, NULL, NULL, NULL, NULL, 'pass', NULL, '기간 완료로 인한 자동 통과 처리', '2025-06-09 05:10:44', '2025-06-09 05:10:44');

-- 테이블 patch_management.phishing_training_periods 구조 내보내기
DROP TABLE IF EXISTS `phishing_training_periods`;
CREATE TABLE IF NOT EXISTS `phishing_training_periods` (
  `period_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `training_year` int(11) NOT NULL COMMENT '훈련 연도',
  `training_period` enum('first_half','second_half') NOT NULL COMMENT '훈련 기간 (상반기/하반기)',
  `start_date` date NOT NULL COMMENT '훈련 시작일',
  `end_date` date NOT NULL COMMENT '훈련 종료일',
  `is_completed` tinyint(1) DEFAULT 0 COMMENT '완료 여부 (0: 미완료, 1: 완료)',
  `completed_at` timestamp NULL DEFAULT NULL COMMENT '완료 처리 시각',
  `completed_by` varchar(50) DEFAULT NULL COMMENT '완료 처리한 관리자',
  `description` text DEFAULT NULL COMMENT '기간 설명',
  `created_by` varchar(50) NOT NULL COMMENT '생성한 관리자',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `is_active` tinyint(1) DEFAULT 1 COMMENT '활성 상태',
  PRIMARY KEY (`period_id`),
  UNIQUE KEY `uk_year_period` (`training_year`,`training_period`),
  KEY `idx_training_year` (`training_year`),
  KEY `idx_is_completed` (`is_completed`),
  KEY `idx_active` (`is_active`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='악성메일 모의훈련 기간 설정';

-- 테이블 데이터 patch_management.phishing_training_periods:~2 rows (대략적) 내보내기
DELETE FROM `phishing_training_periods`;
INSERT INTO `phishing_training_periods` (`period_id`, `training_year`, `training_period`, `start_date`, `end_date`, `is_completed`, `completed_at`, `completed_by`, `description`, `created_by`, `created_at`, `updated_at`, `is_active`) VALUES
	(24, 2025, 'second_half', '2025-07-02', '2025-08-09', 0, NULL, NULL, '', 'admin', '2025-06-08 12:29:43', '2025-06-08 12:29:43', 1),
	(25, 2025, 'first_half', '2025-06-02', '2025-06-04', 1, '2025-06-09 05:10:44', 'admin', '', 'admin', '2025-06-08 12:31:46', '2025-06-09 05:10:44', 1);

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
INSERT INTO `security_education` (`education_id`, `user_id`, `education_year`, `education_period`, `education_type`, `education_date`, `completion_status`, `notes`, `created_at`, `updated_at`) VALUES
	(1, 3, 2025, 'first_half', '기본교육', NULL, 0, '상반기 교육 미이수', '2025-06-03 12:44:38', '2025-06-03 12:44:38'),
	(2, 3, 2025, 'second_half', '기본교육', NULL, 0, '하반기 교육 미실시', '2025-06-03 12:44:38', '2025-06-03 12:44:38'),
	(3, 3, 2024, 'first_half', '기본교육', NULL, 1, '상반기 교육 이수 완료', '2025-06-03 12:44:38', '2025-06-03 12:44:38'),
	(4, 3, 2024, 'second_half', '기본교육', NULL, 1, '하반기 교육 이수 완료', '2025-06-03 12:44:38', '2025-06-03 12:44:38');

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
) ENGINE=InnoDB AUTO_INCREMENT=148 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='KPI 보안 점수 요약 (감점 기준)';

-- 테이블 데이터 patch_management.security_score_summary:~12 rows (대략적) 내보내기
DELETE FROM `security_score_summary`;
INSERT INTO `security_score_summary` (`summary_id`, `user_id`, `evaluation_year`, `audit_penalty`, `education_penalty`, `training_penalty`, `total_penalty`, `audit_failed_count`, `education_incomplete_count`, `training_failed_count`, `last_calculated`, `created_at`) VALUES
	(1, 3, 2025, 2.00, 1.00, 0.50, 3.50, 4, 2, 1, '2025-06-04 05:48:17', '2025-06-03 12:52:56'),
	(2, 3, 2023, 0.00, 1.00, 0.00, 1.00, 0, 2, 0, '2025-06-04 05:48:17', '2025-06-03 12:52:56'),
	(3, 3, 2024, 0.00, 0.00, 0.00, 0.00, 0, 0, 0, '2025-06-04 05:48:17', '2025-06-03 12:52:56'),
	(10, 3, 2022, 0.00, 1.00, 0.00, 1.00, 0, 2, 0, '2025-06-03 13:46:57', '2025-06-03 12:54:03'),
	(57, 3, 2026, 0.00, 1.00, 0.00, 1.00, 0, 2, 0, '2025-06-03 13:47:01', '2025-06-03 13:46:58'),
	(116, 5, 2025, 0.00, 1.00, 0.00, 1.00, 0, 2, 0, '2025-06-04 04:54:38', '2025-06-03 15:02:34'),
	(117, 5, 2023, 0.00, 1.00, 0.00, 1.00, 0, 2, 0, '2025-06-04 01:16:00', '2025-06-03 15:02:34'),
	(118, 5, 2024, 0.00, 1.00, 0.00, 1.00, 0, 2, 0, '2025-06-04 01:16:00', '2025-06-03 15:02:34'),
	(134, 4, 2025, 0.00, 1.00, 0.00, 1.00, 0, 2, 0, '2025-06-04 04:54:38', '2025-06-03 04:46:55'),
	(135, 2, 2025, 0.00, 1.00, 0.00, 1.00, 0, 2, 0, '2025-06-04 04:54:38', '2025-06-03 04:46:55'),
	(136, 6, 2025, 0.00, 1.00, 0.00, 1.00, 0, 2, 0, '2025-06-04 04:54:38', '2025-06-03 04:46:55'),
	(137, 1, 2025, 0.00, 1.00, 0.00, 1.00, 0, 2, 0, '2025-06-04 04:54:38', '2025-06-03 04:46:55');

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
  `ip` text DEFAULT NULL COMMENT 'IP 주소 (여러개인 경우 쉼표로 구분)',
  `mac` text DEFAULT NULL COMMENT 'MAC 주소 (여러개인 경우 쉼표로 구분)',
  PRIMARY KEY (`uid`),
  UNIQUE KEY `uk_user_id` (`user_id`),
  KEY `idx_username` (`username`),
  KEY `idx_department` (`department`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 정보';

-- 테이블 데이터 patch_management.users:~4 rows (대략적) 내보내기
DELETE FROM `users`;
INSERT INTO `users` (`uid`, `user_id`, `username`, `mail`, `department`, `created_at`, `updated_at`, `last_updated`, `ip`, `mac`) VALUES
	(1, 'eunjekim8', '김은제', 'eunjekim8@test.com', '운영실', '2025-06-09 06:39:36', '2025-06-09 06:42:14', '2025-06-09 06:42:14', '10.101.21.32, 10.106.15.129', NULL),
	(2, 'penguin', '펭귄', 'penguin@test.com', '남극', '2025-06-09 06:39:36', '2025-06-09 06:43:14', '2025-06-09 06:43:14', '10.24.13.24', NULL),
	(3, 'dog', '강아지', 'dog@test.com', '동물원', '2025-06-09 06:39:36', '2025-06-09 06:43:19', '2025-06-09 06:43:19', '10.11.42.13', NULL),
	(4, 'admin', '관리자', 'admin@test.com', '관리실', '2025-06-09 06:39:36', '2025-06-09 06:41:07', '2025-06-09 06:41:07', '127.0.0.1', NULL);

-- 테이블 patch_management.user_extended_exceptions 구조 내보내기
DROP TABLE IF EXISTS `user_extended_exceptions`;
CREATE TABLE IF NOT EXISTS `user_extended_exceptions` (
  `exception_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL COMMENT 'users 테이블의 uid 참조',
  `item_id` varchar(100) NOT NULL COMMENT '항목 ID (정수형: 감사항목, 문자형: 교육/훈련)',
  `item_type` enum('audit_item','training_period','education_period') NOT NULL COMMENT '항목 유형',
  `item_name` varchar(255) NOT NULL COMMENT '항목명 (비정규화)',
  `item_category` varchar(100) NOT NULL COMMENT '항목 카테고리 (비정규화)',
  `exclude_reason` varchar(500) NOT NULL COMMENT '제외 사유',
  `exclude_type` enum('permanent','temporary') DEFAULT 'permanent' COMMENT '제외 유형',
  `start_date` date DEFAULT NULL COMMENT '제외 시작일 (temporary인 경우)',
  `end_date` date DEFAULT NULL COMMENT '제외 종료일 (temporary인 경우)',
  `created_by` varchar(50) NOT NULL COMMENT '설정한 관리자',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `is_active` tinyint(1) DEFAULT 1 COMMENT '활성 상태',
  PRIMARY KEY (`exception_id`),
  UNIQUE KEY `uk_user_extended_exception` (`user_id`,`item_id`,`item_type`),
  KEY `idx_user_id_extended` (`user_id`),
  KEY `idx_item_type_extended` (`item_type`),
  KEY `idx_active_extended` (`is_active`),
  KEY `idx_item_category` (`item_category`),
  KEY `idx_user_extended_search` (`user_id`,`item_type`,`is_active`),
  CONSTRAINT `fk_user_extended_exception` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자별 확장 감사 항목 제외 설정 (감사/교육/훈련)';

-- 테이블 데이터 patch_management.user_extended_exceptions:~2 rows (대략적) 내보내기
DELETE FROM `user_extended_exceptions`;
INSERT INTO `user_extended_exceptions` (`exception_id`, `user_id`, `item_id`, `item_type`, `item_name`, `item_category`, `exclude_reason`, `exclude_type`, `start_date`, `end_date`, `created_by`, `created_at`, `updated_at`, `is_active`) VALUES
	(11, 2, 'training_2025_first_half', 'training_period', '2025년 상반기 악성메일 모의훈련', '악성메일 모의훈련', '관리자 설정', 'permanent', NULL, NULL, 'admin', '2025-06-08 13:26:43', '2025-06-09 00:18:47', 0),
	(13, 4, 'training_2025_first_half', 'training_period', '2025년 first_half(상반기) 모의훈련', '모의훈련', '관리자 설정', 'permanent', NULL, NULL, 'admin', '2025-06-08 14:43:00', '2025-06-08 14:44:18', 0);

-- 테이블 patch_management.user_item_exceptions 구조 내보내기
DROP TABLE IF EXISTS `user_item_exceptions`;
CREATE TABLE IF NOT EXISTS `user_item_exceptions` (
  `exception_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL COMMENT 'users 테이블의 uid 참조',
  `item_id` int(11) NOT NULL COMMENT 'checklist_items 테이블 참조',
  `exclude_reason` varchar(255) NOT NULL COMMENT '제외 사유',
  `exclude_type` enum('permanent','temporary') DEFAULT 'permanent' COMMENT '제외 유형',
  `start_date` date DEFAULT NULL COMMENT '제외 시작일 (temporary인 경우)',
  `end_date` date DEFAULT NULL COMMENT '제외 종료일 (temporary인 경우)',
  `created_by` varchar(50) NOT NULL COMMENT '설정한 관리자',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `is_active` tinyint(1) DEFAULT 1 COMMENT '활성 상태',
  `item_type` varchar(50) DEFAULT 'audit' COMMENT '항목 유형 (audit/education/training)',
  `item_name` varchar(255) DEFAULT '' COMMENT '항목명 (중복 저장)',
  `item_category` varchar(100) DEFAULT '' COMMENT '항목 카테고리 (중복 저장)',
  PRIMARY KEY (`exception_id`),
  UNIQUE KEY `uk_user_item_exception` (`user_id`,`item_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_item_id` (`item_id`),
  KEY `idx_active` (`is_active`),
  KEY `idx_user_exceptions_type` (`user_id`,`item_type`,`is_active`),
  CONSTRAINT `fk_exception_item` FOREIGN KEY (`item_id`) REFERENCES `checklist_items` (`item_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_exception_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자별 감사 항목 제외 설정';

-- 테이블 데이터 patch_management.user_item_exceptions:~0 rows (대략적) 내보내기
DELETE FROM `user_item_exceptions`;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;