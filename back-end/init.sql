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
) ENGINE=InnoDB AUTO_INCREMENT=93 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='보안 감사 로그';

-- 테이블 데이터 patch_management.audit_log:~16 rows (대략적) 내보내기
DELETE FROM `audit_log`;
INSERT INTO `audit_log` (`log_id`, `user_id`, `item_id`, `actual_value`, `passed`, `notes`, `exclude_reason`, `checked_at`) VALUES
	(77, 1, 1, '{"screenSaverTime": "600", "screenSaverSecure": "1", "screenSaverEnabled": "1"}', 1, '화면 보호기가 정상적으로 설정되어 있습니다.', NULL, '2025-06-19 05:16:22'),
	(78, 1, 2, '{"UpToDate": 1, "DisplayName": "알약", "RealTimeProtection": 1}', 1, '알약 백신이 정상적으로 설치되어 있으며, 실시간 보호 및 최신 업데이트가 적용되어 있습니다.', NULL, '2025-06-19 05:16:20'),
	(79, 1, 3, '{"minimumPasswordLength": "8"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-06-19 05:16:23'),
	(80, 1, 4, '{"passwordComplexity": "1"}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-06-19 05:16:23'),
	(81, 1, 5, '{"maximumPasswordAge": "90"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-06-19 05:16:23'),
	(82, 1, 6, '{"passwordHistorySize": "5"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-06-19 05:16:24'),
	(83, 1, 7, '{"folders": ["IPC$", "Users", "공유폴더"]}', 0, '불필요한 공유 폴더가 있습니다. 필요하지 않은 공유 폴더를 제거해주세요.', NULL, '2025-06-19 05:16:25'),
	(84, 1, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-06-19 05:16:27'),
	(85, 1, 1, '{"screenSaverTime": "600", "screenSaverSecure": "1", "screenSaverEnabled": "1"}', 1, '화면 보호기가 정상적으로 설정되어 있습니다.', NULL, '2025-06-25 01:10:25'),
	(86, 1, 2, '{"UpToDate": 1, "DisplayName": "알약", "RealTimeProtection": 1}', 1, '알약 백신이 정상적으로 설치되어 있으며, 실시간 보호 및 최신 업데이트가 적용되어 있습니다.', NULL, '2025-06-25 01:10:20'),
	(87, 1, 3, '{"minimumPasswordLength": "8"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-06-25 01:10:30'),
	(88, 1, 4, '{"passwordComplexity": "1"}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-06-25 01:10:30'),
	(89, 1, 5, '{"maximumPasswordAge": "90"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-06-25 01:10:30'),
	(90, 1, 6, '{"passwordHistorySize": "5"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-06-25 01:10:30'),
	(91, 1, 7, '{"folders": ["IPC$", "Users", "공유폴더"]}', 0, '불필요한 공유 폴더가 있습니다. 필요하지 않은 공유 폴더를 제거해주세요. [제외사유: 테스트]', '테스트', '2025-06-25 01:10:36'),
	(92, 1, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-06-25 01:10:40');

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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='보안 점검 항목';

-- 테이블 데이터 patch_management.checklist_items:~8 rows (대략적) 내보내기
DELETE FROM `checklist_items`;
INSERT INTO `checklist_items` (`item_id`, `item_name`, `category`, `description`, `check_type`, `check_frequency`, `penalty_weight`, `created_at`, `updated_at`) VALUES
	(1, '화면보호기 사용', '접근통제', '화면보호기 설정 및 시간 확인', 'daily', 'daily', 0.5, '2025-06-03 12:44:38', '2025-06-03 12:44:38'),
	(2, '백신 상태 확인', '악성코드', '백신 설치 및 업데이트 상태 확인', 'daily', 'daily', 0.5, '2025-06-03 12:44:38', '2025-06-03 13:16:36'),
	(3, '패스워드 길이의 적정성', '접근통제', '최소 패스워드 길이 정책 확인', 'daily', 'daily', 0.5, '2025-06-03 12:44:38', '2025-06-03 13:16:43'),
	(4, '패스워드 복잡도 설정', '접근통제', '패스워드 복잡도 정책 확인', 'daily', 'daily', 0.5, '2025-06-03 12:44:38', '2025-06-03 13:16:47'),
	(5, '패스워드 주기적 변경', '접근통제', '패스워드 주기적 변경 정책 확인', 'daily', 'daily', 0.5, '2025-06-03 12:44:38', '2025-06-03 13:16:51'),
	(6, '동일 패스워드 설정 제한', '접근통제', '동일 패스워드 설정 정책 확인', 'daily', 'daily', 0.5, '2025-06-03 12:44:38', '2025-06-03 13:16:53'),
	(7, '공유폴더 확인', '접근통제', '공유폴더 설정 확인', 'daily', 'daily', 0.5, '2025-06-03 12:44:38', '2025-06-03 13:16:59'),
	(8, '원격데스크톱 제한', '접근통제', '원격 데스크톱 연결 제한 설정', 'daily', 'daily', 0.5, '2025-06-03 12:44:38', '2025-06-03 13:17:02');

-- 테이블 patch_management.department_exceptions 구조 내보내기
DROP TABLE IF EXISTS `department_exceptions`;
CREATE TABLE IF NOT EXISTS `department_exceptions` (
  `exception_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `department` varchar(100) NOT NULL COMMENT '부서명',
  `item_id` varchar(255) NOT NULL COMMENT '항목 ID (audit: 숫자, education/training: 문자열)',
  `item_type` enum('audit','education','training') NOT NULL COMMENT '항목 유형',
  `item_name` varchar(255) NOT NULL COMMENT '항목명',
  `item_category` varchar(100) NOT NULL COMMENT '항목 카테고리',
  `exclude_reason` varchar(255) NOT NULL COMMENT '제외 사유',
  `exclude_type` enum('permanent','temporary') DEFAULT 'permanent' COMMENT '제외 유형',
  `start_date` date DEFAULT NULL COMMENT '제외 시작일 (temporary인 경우)',
  `end_date` date DEFAULT NULL COMMENT '제외 종료일 (temporary인 경우)',
  `created_by` varchar(50) NOT NULL COMMENT '설정한 관리자',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `is_active` tinyint(1) DEFAULT 1 COMMENT '활성 상태',
  PRIMARY KEY (`exception_id`),
  UNIQUE KEY `uk_dept_item_exception` (`department`,`item_id`,`item_type`),
  KEY `idx_department` (`department`),
  KEY `idx_item_type` (`item_type`),
  KEY `idx_active` (`is_active`),
  KEY `idx_dept_exceptions_search` (`department`,`item_type`,`is_active`),
  KEY `idx_item_search` (`item_id`,`item_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='통합 부서별 예외 설정 테이블';

-- 테이블 데이터 patch_management.department_exceptions:~0 rows (대략적) 내보내기
DELETE FROM `department_exceptions`;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='부서별 확장 감사 항목 제외 설정 (감사/교육/훈련)';

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
  KEY `idx_dept_exceptions_type` (`department`,`item_type`,`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='부서별 감사 항목 제외 설정';

-- 테이블 데이터 patch_management.department_item_exceptions:~0 rows (대략적) 내보내기
DELETE FROM `department_item_exceptions`;

-- 테이블 patch_management.manual_check_items 구조 내보내기
DROP TABLE IF EXISTS `manual_check_items`;
CREATE TABLE IF NOT EXISTS `manual_check_items` (
  `item_id` int(11) NOT NULL AUTO_INCREMENT,
  `item_code` varchar(50) NOT NULL COMMENT '항목 코드',
  `item_name` varchar(255) NOT NULL COMMENT '점검 항목명',
  `item_category` varchar(100) NOT NULL COMMENT '카테고리',
  `description` text DEFAULT NULL COMMENT '상세 설명',
  `penalty_weight` decimal(3,1) DEFAULT 0.5 COMMENT '감점 가중치',
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`item_id`),
  UNIQUE KEY `uk_item_code` (`item_code`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='수시 점검 항목';

-- 테이블 데이터 patch_management.manual_check_items:~3 rows (대략적) 내보내기
DELETE FROM `manual_check_items`;
INSERT INTO `manual_check_items` (`item_id`, `item_code`, `item_name`, `item_category`, `description`, `penalty_weight`, `is_active`, `created_at`) VALUES
	(9, 'seal_check', 'PC 봉인씰 확인', '물리보안', 'PC 봉인씰 상태 점검', 0.5, 1, '2025-06-11 00:33:57'),
	(10, 'malware_scan', '악성코드 전체 검사', '악성코드', '전체 시스템 악성코드 검사', 0.5, 1, '2025-06-11 00:33:57'),
	(11, 'file_encryption', '개인정보 파일 암호화', '개인정보보호', '개인정보 파일 암호화 적용 여부', 0.5, 1, '2025-06-11 00:33:57');

-- 테이블 patch_management.manual_check_periods 구조 내보내기
DROP TABLE IF EXISTS `manual_check_periods`;
CREATE TABLE IF NOT EXISTS `manual_check_periods` (
  `period_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `check_type` enum('seal_check','malware_scan','file_encryption') NOT NULL COMMENT '점검 유형',
  `period_year` int(11) NOT NULL COMMENT '점검 연도',
  `period_name` varchar(50) NOT NULL COMMENT '기간명 (Q1, Q2, 상반기 등)',
  `start_date` date NOT NULL COMMENT '점검 시작일',
  `end_date` date NOT NULL COMMENT '점검 종료일',
  `is_completed` tinyint(1) DEFAULT 0 COMMENT '완료 여부 (0: 미완료, 1: 완료)',
  `completed_at` timestamp NULL DEFAULT NULL COMMENT '완료 처리 시각',
  `completed_by` varchar(50) DEFAULT NULL COMMENT '완료 처리한 관리자',
  `description` text DEFAULT NULL COMMENT '기간 설명',
  `auto_pass_setting` tinyint(1) DEFAULT 1 COMMENT '자동 통과 처리 여부',
  `created_by` varchar(50) NOT NULL COMMENT '생성한 관리자',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `is_active` tinyint(1) DEFAULT 1 COMMENT '활성 상태',
  PRIMARY KEY (`period_id`),
  UNIQUE KEY `uk_type_year_period` (`check_type`,`period_year`,`period_name`),
  KEY `idx_check_type` (`check_type`),
  KEY `idx_period_year` (`period_year`),
  KEY `idx_is_completed` (`is_completed`),
  KEY `idx_active` (`is_active`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='수시 점검 기간 설정';

-- 테이블 데이터 patch_management.manual_check_periods:~5 rows (대략적) 내보내기
DELETE FROM `manual_check_periods`;
INSERT INTO `manual_check_periods` (`period_id`, `check_type`, `period_year`, `period_name`, `start_date`, `end_date`, `is_completed`, `completed_at`, `completed_by`, `description`, `auto_pass_setting`, `created_by`, `created_at`, `updated_at`, `is_active`) VALUES
	(14, 'seal_check', 2025, '상반기', '2025-07-10', '2025-07-30', 1, '2025-06-25 00:45:57', 'eunjekim8', '', 1, 'admin', '2025-06-14 10:56:12', '2025-06-25 00:45:57', 1),
	(15, 'seal_check', 2025, '3월', '2025-04-03', '2025-04-13', 1, '2025-06-25 00:45:54', 'eunjekim8', '', 1, 'admin', '2025-06-14 11:19:26', '2025-06-25 00:45:54', 1),
	(16, 'file_encryption', 2025, '2323', '2025-01-01', '2025-04-01', 1, '2025-06-26 01:55:24', 'eunjekim8', '', 1, 'admin', '2025-06-14 11:46:46', '2025-06-26 01:55:24', 1),
	(17, 'seal_check', 2025, '42342', '2025-05-10', '2025-06-16', 1, '2025-06-25 00:45:55', 'eunjekim8', '', 1, 'admin', '2025-06-14 11:47:18', '2025-06-25 00:45:55', 1),
	(18, 'file_encryption', 2025, '6월 검사', '2025-06-13', '2025-06-15', 1, '2025-06-25 00:45:58', 'eunjekim8', '', 1, 'admin', '2025-06-14 14:38:58', '2025-06-25 00:45:58', 1);

-- 테이블 patch_management.manual_check_results 구조 내보내기
DROP TABLE IF EXISTS `manual_check_results`;
CREATE TABLE IF NOT EXISTS `manual_check_results` (
  `check_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL COMMENT 'users 테이블 참조',
  `check_item_code` varchar(50) NOT NULL DEFAULT 'seal_check' COMMENT '점검 항목 코드 (seal_check, malware_scan, file_encryption)',
  `source_ip` varchar(45) DEFAULT NULL COMMENT '출처 IP (악성코드/암호화에서 사용)',
  `check_year` int(11) NOT NULL COMMENT '점검 연도',
  `check_period` varchar(20) NOT NULL COMMENT '점검 기간',
  `check_date` datetime NOT NULL COMMENT '점검 실시 일시',
  `checker_name` varchar(100) NOT NULL COMMENT '점검자명',
  `seal_status` enum('normal','damaged','missing','replacement_needed') DEFAULT NULL COMMENT '봉인씰 상태',
  `seal_number` varchar(50) DEFAULT NULL COMMENT '봉인 번호',
  `seal_notes` text DEFAULT NULL COMMENT '봉인씰 관련 비고',
  `malware_scan_result` enum('clean','infected','scan_failed','not_performed') DEFAULT NULL COMMENT '악성코드 검사 결과',
  `threats_found` int(11) DEFAULT 0 COMMENT '발견된 위협 수',
  `threats_cleaned` tinyint(1) DEFAULT 0 COMMENT '치료 완료 여부',
  `antivirus_version` varchar(100) DEFAULT NULL COMMENT '백신 엔진 버전',
  `malware_notes` text DEFAULT NULL COMMENT '악성코드 검사 관련 비고',
  `malware_name` varchar(255) DEFAULT NULL COMMENT '악성코드명',
  `malware_classification` varchar(100) DEFAULT NULL COMMENT '악성코드 분류',
  `malware_path` text DEFAULT NULL COMMENT '악성코드 경로',
  `detection_item` varchar(255) DEFAULT NULL COMMENT '탐지 항목',
  `encryption_status` enum('fully_encrypted','not_encrypted','partially_encrypted','not_applicable') DEFAULT NULL COMMENT '암호화 상태',
  `files_scanned` int(11) DEFAULT 0 COMMENT '검사된 파일 수',
  `unencrypted_files` int(11) DEFAULT 0 COMMENT '미암호화 파일 수',
  `encryption_completed` tinyint(1) DEFAULT 0 COMMENT '암호화 조치 완료 여부',
  `encryption_notes` text DEFAULT NULL COMMENT '암호화 관련 비고',
  `round_number` varchar(20) DEFAULT NULL COMMENT '회차 정보 (161회차 등)',
  `ssn_included` tinyint(1) DEFAULT 0 COMMENT '주민등록번호 포함 여부',
  `overall_result` enum('pass','fail','partial') NOT NULL COMMENT '종합 점검 결과',
  `total_score` decimal(5,2) DEFAULT 0.00 COMMENT '총점',
  `penalty_points` decimal(5,2) DEFAULT 0.00 COMMENT '감점',
  `notes` text DEFAULT NULL COMMENT '전체 비고',
  `exclude_from_scoring` tinyint(1) DEFAULT 0 COMMENT '점수 산정 제외 여부',
  `exclude_reason` varchar(500) DEFAULT NULL COMMENT '제외 사유',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `period_id` bigint(20) DEFAULT NULL COMMENT '연결된 기간 ID',
  PRIMARY KEY (`check_id`),
  KEY `idx_user_period` (`user_id`,`check_year`,`check_period`),
  KEY `idx_check_date` (`check_date`),
  KEY `idx_overall_result` (`overall_result`),
  KEY `period_id` (`period_id`),
  KEY `idx_check_item_code` (`check_item_code`),
  KEY `idx_check_type_year_period` (`check_item_code`,`check_year`,`check_period`),
  KEY `idx_check_type_result` (`check_item_code`,`overall_result`),
  CONSTRAINT `manual_check_results_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`),
  CONSTRAINT `manual_check_results_ibfk_2` FOREIGN KEY (`period_id`) REFERENCES `manual_check_periods` (`period_id`)
) ENGINE=InnoDB AUTO_INCREMENT=95 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='수시 점검 결과';

-- 테이블 데이터 patch_management.manual_check_results:~25 rows (대략적) 내보내기
DELETE FROM `manual_check_results`;
INSERT INTO `manual_check_results` (`check_id`, `user_id`, `check_item_code`, `source_ip`, `check_year`, `check_period`, `check_date`, `checker_name`, `seal_status`, `seal_number`, `seal_notes`, `malware_scan_result`, `threats_found`, `threats_cleaned`, `antivirus_version`, `malware_notes`, `malware_name`, `malware_classification`, `malware_path`, `detection_item`, `encryption_status`, `files_scanned`, `unencrypted_files`, `encryption_completed`, `encryption_notes`, `round_number`, `ssn_included`, `overall_result`, `total_score`, `penalty_points`, `notes`, `exclude_from_scoring`, `exclude_reason`, `created_at`, `updated_at`, `period_id`) VALUES
	(8, 4, 'seal_check', NULL, 2025, 'auto_complete', '2025-06-25 09:45:54', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-25 00:45:54', '2025-06-25 00:45:54', 15),
	(9, 3, 'seal_check', NULL, 2025, 'auto_complete', '2025-06-25 09:45:54', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-25 00:45:54', '2025-06-25 00:45:54', 15),
	(10, 1, 'seal_check', NULL, 2025, 'auto_complete', '2025-06-25 09:45:54', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-25 00:45:54', '2025-06-25 00:45:54', 15),
	(11, 5, 'seal_check', NULL, 2025, 'auto_complete', '2025-06-25 09:45:54', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-25 00:45:54', '2025-06-25 00:45:54', 15),
	(12, 2, 'seal_check', NULL, 2025, 'auto_complete', '2025-06-25 09:45:54', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-25 00:45:54', '2025-06-25 00:45:54', 15),
	(15, 4, 'seal_check', NULL, 2025, 'auto_complete', '2025-06-25 09:45:55', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-25 00:45:55', '2025-06-25 00:45:55', 17),
	(16, 3, 'seal_check', NULL, 2025, 'auto_complete', '2025-06-25 09:45:55', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-25 00:45:55', '2025-06-25 00:45:55', 17),
	(17, 1, 'seal_check', NULL, 2025, 'auto_complete', '2025-06-25 09:45:55', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-25 00:45:55', '2025-06-25 00:45:55', 17),
	(18, 5, 'seal_check', NULL, 2025, 'auto_complete', '2025-06-25 09:45:55', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-25 00:45:55', '2025-06-25 00:45:55', 17),
	(19, 2, 'seal_check', NULL, 2025, 'auto_complete', '2025-06-25 09:45:55', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-25 00:45:55', '2025-06-25 00:45:55', 17),
	(22, 4, 'seal_check', NULL, 2025, 'auto_complete', '2025-06-25 09:45:57', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-25 00:45:57', '2025-06-25 00:45:57', 14),
	(23, 3, 'seal_check', NULL, 2025, 'auto_complete', '2025-06-25 09:45:57', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-25 00:45:57', '2025-06-25 00:45:57', 14),
	(24, 1, 'seal_check', NULL, 2025, 'auto_complete', '2025-06-25 09:45:57', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-25 00:45:57', '2025-06-25 00:45:57', 14),
	(25, 5, 'seal_check', NULL, 2025, 'auto_complete', '2025-06-25 09:45:57', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-25 00:45:57', '2025-06-25 00:45:57', 14),
	(26, 2, 'seal_check', NULL, 2025, 'auto_complete', '2025-06-25 09:45:57', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-25 00:45:57', '2025-06-25 00:45:57', 14),
	(29, 4, 'file_encryption', NULL, 2025, 'auto_complete', '2025-06-25 09:45:58', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-25 00:45:58', '2025-06-25 00:45:58', 18),
	(30, 3, 'file_encryption', NULL, 2025, 'auto_complete', '2025-06-25 09:45:58', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-25 00:45:58', '2025-06-25 00:45:58', 18),
	(31, 1, 'file_encryption', NULL, 2025, 'auto_complete', '2025-06-25 09:45:58', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-25 00:45:58', '2025-06-25 00:45:58', 18),
	(32, 5, 'file_encryption', NULL, 2025, 'auto_complete', '2025-06-25 09:45:58', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-25 00:45:58', '2025-06-25 00:45:58', 18),
	(33, 2, 'file_encryption', NULL, 2025, 'auto_complete', '2025-06-25 09:45:58', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-25 00:45:58', '2025-06-25 00:45:58', 18),
	(90, 4, 'file_encryption', NULL, 2025, 'auto_complete', '2025-06-26 10:55:24', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-26 01:55:24', '2025-06-26 01:55:24', 16),
	(91, 3, 'file_encryption', NULL, 2025, 'auto_complete', '2025-06-26 10:55:24', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-26 01:55:24', '2025-06-26 01:55:24', 16),
	(92, 1, 'file_encryption', NULL, 2025, 'auto_complete', '2025-06-26 10:55:24', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-26 01:55:24', '2025-06-26 01:55:24', 16),
	(93, 5, 'file_encryption', NULL, 2025, 'auto_complete', '2025-06-26 10:55:24', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-26 01:55:24', '2025-06-26 01:55:24', 16),
	(94, 2, 'file_encryption', NULL, 2025, 'auto_complete', '2025-06-26 10:55:24', '자동완료', NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0, 'pass', 100.00, 0.00, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-26 01:55:24', '2025-06-26 01:55:24', 16);

-- 테이블 patch_management.phishing_training 구조 내보내기
DROP TABLE IF EXISTS `phishing_training`;
CREATE TABLE IF NOT EXISTS `phishing_training` (
  `training_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL COMMENT 'users 테이블의 uid 참조',
  `period_id` bigint(20) NOT NULL COMMENT '훈련 기간 ID 참조',
  `training_year` int(11) NOT NULL COMMENT '훈련 연도',
  `email_sent_time` timestamp NULL DEFAULT NULL COMMENT '메일발송시각',
  `action_time` timestamp NULL DEFAULT NULL COMMENT '수행시각 (사용자가 행동한 시간)',
  `log_type` varchar(100) DEFAULT NULL COMMENT '로그유형 (스크립트 첨부파일 열람, 이메일 열람2 등)',
  `mail_type` varchar(100) DEFAULT NULL COMMENT '메일유형 (퇴직연금 운용, 세금계산서, 카카오톡 등)',
  `target_email` varchar(255) DEFAULT NULL COMMENT '대상 이메일 주소',
  `training_result` enum('success','fail','no_response') DEFAULT 'no_response' COMMENT '훈련 결과 (성공, 실패, 무응답)',
  `response_time_minutes` int(11) DEFAULT NULL COMMENT '응답 시간 (분 단위)',
  `notes` text DEFAULT NULL COMMENT '비고',
  `exclude_from_scoring` tinyint(1) DEFAULT 0 COMMENT '점수 계산 제외 여부',
  `exclude_reason` text DEFAULT NULL COMMENT '제외 사유',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`training_id`),
  UNIQUE KEY `uk_user_period_email` (`user_id`,`period_id`,`target_email`),
  KEY `idx_training_year` (`training_year`),
  KEY `idx_training_result` (`training_result`),
  KEY `idx_log_type` (`log_type`),
  KEY `idx_mail_type` (`mail_type`),
  KEY `period_id` (`period_id`),
  KEY `idx_email_sent_time` (`email_sent_time`),
  KEY `idx_action_time` (`action_time`),
  KEY `idx_user_year_result` (`user_id`,`training_year`,`training_result`),
  KEY `idx_target_email` (`target_email`),
  CONSTRAINT `phishing_training_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`) ON DELETE CASCADE,
  CONSTRAINT `phishing_training_ibfk_2` FOREIGN KEY (`period_id`) REFERENCES `phishing_training_periods` (`period_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='피싱 훈련 이력 (엑셀 업로드 매핑)';

-- 테이블 데이터 patch_management.phishing_training:~5 rows (대략적) 내보내기
DELETE FROM `phishing_training`;
INSERT INTO `phishing_training` (`training_id`, `user_id`, `period_id`, `training_year`, `email_sent_time`, `action_time`, `log_type`, `mail_type`, `target_email`, `training_result`, `response_time_minutes`, `notes`, `exclude_from_scoring`, `exclude_reason`, `created_at`, `updated_at`) VALUES
	(57, 5, 3, 2025, '2025-06-03 00:00:10', '2025-06-03 01:33:22', '스크립트 첨부파일 열람', '퇴직연금 운용', 'hamtori@test.com', 'fail', 93, NULL, 0, NULL, '2025-06-29 11:50:28', '2025-06-29 11:50:28'),
	(58, 1, 3, 2025, '2025-06-03 00:00:10', '2025-06-03 01:33:22', '스크립트 첨부파일 열람', '세금계산서', 'eunjekim8@test.com', 'fail', 93, NULL, 0, NULL, '2025-06-29 11:50:28', '2025-06-29 11:50:28'),
	(59, 4, 3, 2025, '2025-06-03 00:00:10', '2025-06-04 01:33:22', '이메일 열람2', '카카오톡', 'admin@test.com', 'success', 1533, NULL, 0, NULL, '2025-06-29 11:50:28', '2025-06-29 11:50:28'),
	(90, 2, 3, 2025, '2025-06-29 12:40:20', NULL, '자동 완료', '자동 통과', 'penguin@test.com', 'success', NULL, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-29 12:40:20', '2025-06-29 12:40:20'),
	(91, 3, 3, 2025, '2025-06-29 12:40:20', NULL, '자동 완료', '자동 통과', 'dog@test.com', 'success', NULL, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-29 12:40:20', '2025-06-29 12:40:20'),
	(93, 1, 7, 2025, '2025-06-29 12:40:21', NULL, '자동 완료', '자동 통과', 'eunjekim8@test.com', 'success', NULL, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-29 12:40:21', '2025-06-29 12:40:21'),
	(94, 2, 7, 2025, '2025-06-29 12:40:21', NULL, '자동 완료', '자동 통과', 'penguin@test.com', 'success', NULL, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-29 12:40:21', '2025-06-29 12:40:21'),
	(95, 3, 7, 2025, '2025-06-29 12:40:21', NULL, '자동 완료', '자동 통과', 'dog@test.com', 'success', NULL, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-29 12:40:21', '2025-06-29 12:40:21'),
	(96, 4, 7, 2025, '2025-06-29 12:40:21', NULL, '자동 완료', '자동 통과', 'admin@test.com', 'success', NULL, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-29 12:40:21', '2025-06-29 12:40:21'),
	(97, 5, 7, 2025, '2025-06-29 12:40:21', NULL, '자동 완료', '자동 통과', 'hamtori@test.com', 'success', NULL, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-06-29 12:40:21', '2025-06-29 12:40:21');

-- 테이블 patch_management.phishing_training_periods 구조 내보내기
DROP TABLE IF EXISTS `phishing_training_periods`;
CREATE TABLE IF NOT EXISTS `phishing_training_periods` (
  `period_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `training_year` int(11) NOT NULL COMMENT '훈련 연도',
  `period_name` varchar(50) NOT NULL COMMENT '기간명 (1차 피싱 훈련, 2차 피싱 훈련 등)',
  `training_type` varchar(100) NOT NULL COMMENT '훈련 유형 (이메일 피싱, SMS 피싱, 전화 피싱 등)',
  `start_date` date NOT NULL COMMENT '훈련 시작일',
  `end_date` date NOT NULL COMMENT '훈련 종료일',
  `is_completed` tinyint(1) DEFAULT 0 COMMENT '완료 여부',
  `completed_at` timestamp NULL DEFAULT NULL COMMENT '완료 처리 시각',
  `completed_by` varchar(50) DEFAULT NULL COMMENT '완료 처리한 관리자',
  `description` text DEFAULT NULL COMMENT '훈련 설명',
  `auto_pass_setting` tinyint(1) DEFAULT 1 COMMENT '자동 통과 처리 여부',
  `created_by` varchar(50) NOT NULL COMMENT '생성한 관리자',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`period_id`),
  UNIQUE KEY `uk_year_period_type` (`training_year`,`period_name`,`training_type`),
  KEY `idx_training_year` (`training_year`),
  KEY `idx_training_type` (`training_type`),
  KEY `idx_is_completed` (`is_completed`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='피싱 훈련 기간 설정';

-- 테이블 데이터 patch_management.phishing_training_periods:~2 rows (대략적) 내보내기
DELETE FROM `phishing_training_periods`;
INSERT INTO `phishing_training_periods` (`period_id`, `training_year`, `period_name`, `training_type`, `start_date`, `end_date`, `is_completed`, `completed_at`, `completed_by`, `description`, `auto_pass_setting`, `created_by`, `created_at`, `updated_at`) VALUES
	(3, 2025, '1차 SMS 훈련', 'SMS 피싱', '2025-03-01', '2025-03-31', 1, '2025-06-29 12:40:20', 'admin', '2025년 1차 SMS 피싱 모의훈련', 1, 'admin', '2025-06-26 06:16:33', '2025-06-29 12:40:20'),
	(7, 2025, '2차 SMS 훈련', 'SMS 피싱', '2025-03-01', '2025-03-31', 1, '2025-06-29 12:40:21', 'admin', '2025년 2차 SMS 피싱 모의훈련', 1, 'admin', '2025-06-26 06:16:33', '2025-06-29 12:40:21');

-- 뷰 patch_management.phishing_training_stats 구조 내보내기
DROP VIEW IF EXISTS `phishing_training_stats`;
-- VIEW 종속성 오류를 극복하기 위해 임시 테이블을 생성합니다.
CREATE TABLE `phishing_training_stats` (
	`training_year` INT(11) NOT NULL COMMENT '훈련 연도',
	`period_id` BIGINT(20) NOT NULL COMMENT '훈련 기간 ID 참조',
	`period_name` VARCHAR(1) NOT NULL COMMENT '기간명 (1차 피싱 훈련, 2차 피싱 훈련 등)' COLLATE 'utf8mb4_unicode_ci',
	`training_type` VARCHAR(1) NOT NULL COMMENT '훈련 유형 (이메일 피싱, SMS 피싱, 전화 피싱 등)' COLLATE 'utf8mb4_unicode_ci',
	`total_targets` BIGINT(21) NOT NULL,
	`success_count` BIGINT(21) NOT NULL,
	`fail_count` BIGINT(21) NOT NULL,
	`no_response_count` BIGINT(21) NOT NULL,
	`success_rate` DECIMAL(26,2) NULL,
	`fail_rate` DECIMAL(26,2) NULL
) ENGINE=MyISAM;

-- 테이블 patch_management.security_education 구조 내보내기
DROP TABLE IF EXISTS `security_education`;
CREATE TABLE IF NOT EXISTS `security_education` (
  `education_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL COMMENT 'users 테이블의 uid 참조',
  `education_year` int(11) NOT NULL COMMENT '교육 연도',
  `course_name` varchar(200) NOT NULL COMMENT 'CSV의 수강과정 컬럼 값',
  `completed_count` int(11) DEFAULT 0 COMMENT 'CSV의 수료 컬럼 값',
  `incomplete_count` int(11) DEFAULT 0 COMMENT 'CSV의 미수료 컬럼 값',
  `total_courses` int(11) GENERATED ALWAYS AS (`completed_count` + `incomplete_count`) STORED COMMENT '전체 과정 수',
  `completion_rate` decimal(5,2) GENERATED ALWAYS AS (case when `completed_count` + `incomplete_count` = 0 then 0 else round(`completed_count` / (`completed_count` + `incomplete_count`) * 100,2) end) STORED COMMENT '수료율 (%)',
  `education_type` varchar(100) DEFAULT '기본교육' COMMENT '교육 유형 (참고용)',
  `education_date` date DEFAULT NULL COMMENT '교육 수료일',
  `notes` text DEFAULT NULL COMMENT '비고',
  `period_id` bigint(20) DEFAULT NULL COMMENT '교육 기간 ID 참조',
  `exclude_from_scoring` tinyint(1) DEFAULT 0 COMMENT '점수 계산 제외 여부',
  `exclude_reason` text DEFAULT NULL COMMENT '제외 사유',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`education_id`),
  UNIQUE KEY `uk_user_period_course` (`user_id`,`period_id`,`course_name`),
  KEY `idx_education_year` (`education_year`),
  KEY `idx_completion_rate` (`completion_rate`),
  KEY `period_id` (`period_id`),
  CONSTRAINT `security_education_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`) ON DELETE CASCADE,
  CONSTRAINT `security_education_ibfk_2` FOREIGN KEY (`period_id`) REFERENCES `security_education_periods` (`period_id`),
  CONSTRAINT `CONSTRAINT_1` CHECK (`completed_count` >= 0),
  CONSTRAINT `CONSTRAINT_2` CHECK (`incomplete_count` >= 0),
  CONSTRAINT `CONSTRAINT_3` CHECK (`completed_count` + `incomplete_count` > 0)
) ENGINE=InnoDB AUTO_INCREMENT=554 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='정보보호 교육 이력 (CSV 매핑 개선 버전)';

-- 테이블 데이터 patch_management.security_education:~14 rows (대략적) 내보내기
DELETE FROM `security_education`;
INSERT INTO `security_education` (`education_id`, `user_id`, `education_year`, `course_name`, `completed_count`, `incomplete_count`, `education_type`, `education_date`, `notes`, `period_id`, `exclude_from_scoring`, `exclude_reason`, `created_at`, `updated_at`) VALUES
	(487, 1, 2025, '1차 오프라인 교육', 2, 0, '오프라인', NULL, 'CSV 업로드 - admin', 25, 1, '관리자 설정', '2025-06-26 04:38:11', '2025-06-26 04:48:51'),
	(515, 3, 2025, '1차 오프라인 교육', 1, 0, '오프라인', NULL, '기간 완료로 인한 자동 통과 처리', 25, 0, NULL, '2025-06-26 04:39:11', '2025-06-26 04:39:11'),
	(516, 4, 2025, '1차 오프라인 교육', 1, 0, '오프라인', NULL, '기간 완료로 인한 자동 통과 처리', 25, 0, NULL, '2025-06-26 04:39:11', '2025-06-26 04:39:11'),
	(517, 2, 2025, '1차 오프라인 교육', 1, 0, '오프라인', NULL, '기간 완료로 인한 자동 통과 처리', 25, 0, NULL, '2025-06-26 04:39:11', '2025-06-26 04:39:11'),
	(518, 5, 2025, '1차 오프라인 교육', 1, 0, '오프라인', NULL, '기간 완료로 인한 자동 통과 처리', 25, 0, NULL, '2025-06-26 04:39:11', '2025-06-26 04:39:11'),
	(544, 3, 2025, '3차 오프라인 교육', 1, 0, '오프라인', NULL, '기간 완료로 인한 자동 통과 처리', 27, 0, NULL, '2025-06-26 05:37:46', '2025-06-26 05:37:46'),
	(545, 4, 2025, '3차 오프라인 교육', 1, 0, '오프라인', NULL, '기간 완료로 인한 자동 통과 처리', 27, 0, NULL, '2025-06-26 05:37:46', '2025-06-26 05:37:46'),
	(546, 1, 2025, '3차 오프라인 교육', 1, 4, '오프라인', NULL, '기간 완료로 인한 자동 통과 처리', 27, 0, '', '2025-06-26 05:37:46', '2025-06-26 05:40:41'),
	(547, 2, 2025, '3차 오프라인 교육', 1, 0, '오프라인', NULL, '기간 완료로 인한 자동 통과 처리', 27, 0, NULL, '2025-06-26 05:37:46', '2025-06-26 05:37:46'),
	(548, 5, 2025, '3차 오프라인 교육', 1, 0, '오프라인', NULL, '기간 완료로 인한 자동 통과 처리', 27, 0, NULL, '2025-06-26 05:37:46', '2025-06-26 05:37:46'),
	(549, 3, 2025, '2차 온라인 교육', 1, 0, '온라인', NULL, '기간 완료로 인한 자동 통과 처리', 28, 0, NULL, '2025-06-26 05:37:53', '2025-06-26 05:37:53'),
	(550, 4, 2025, '2차 온라인 교육', 1, 0, '온라인', NULL, '기간 완료로 인한 자동 통과 처리', 28, 0, NULL, '2025-06-26 05:37:53', '2025-06-26 05:37:53'),
	(552, 2, 2025, '2차 온라인 교육', 1, 0, '온라인', NULL, '기간 완료로 인한 자동 통과 처리', 28, 0, NULL, '2025-06-26 05:37:53', '2025-06-26 05:37:53'),
	(553, 5, 2025, '2차 온라인 교육', 1, 0, '온라인', NULL, '기간 완료로 인한 자동 통과 처리', 28, 0, NULL, '2025-06-26 05:37:53', '2025-06-26 05:37:53');

-- 테이블 patch_management.security_education_periods 구조 내보내기
DROP TABLE IF EXISTS `security_education_periods`;
CREATE TABLE IF NOT EXISTS `security_education_periods` (
  `period_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `education_year` int(11) NOT NULL COMMENT '교육 연도',
  `period_name` varchar(50) NOT NULL COMMENT '기간명 (1차 오프라인, 2차 온라인 등)',
  `education_type` varchar(100) NOT NULL COMMENT '교육 유형 (오프라인, 온라인, 신입교육 등)',
  `start_date` date NOT NULL COMMENT '교육 시작일',
  `end_date` date NOT NULL COMMENT '교육 종료일',
  `is_completed` tinyint(1) DEFAULT 0 COMMENT '완료 여부',
  `completed_at` timestamp NULL DEFAULT NULL COMMENT '완료 처리 시각',
  `completed_by` varchar(50) DEFAULT NULL COMMENT '완료 처리한 관리자',
  `description` text DEFAULT NULL COMMENT '교육 설명',
  `auto_pass_setting` tinyint(1) DEFAULT 1 COMMENT '자동 통과 처리 여부',
  `created_by` varchar(50) NOT NULL COMMENT '생성한 관리자',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`period_id`),
  UNIQUE KEY `uk_year_period_type` (`education_year`,`period_name`,`education_type`),
  KEY `idx_education_year` (`education_year`),
  KEY `idx_education_type` (`education_type`),
  KEY `idx_is_completed` (`is_completed`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='정보보호 교육 기간 설정';

-- 테이블 데이터 patch_management.security_education_periods:~4 rows (대략적) 내보내기
DELETE FROM `security_education_periods`;
INSERT INTO `security_education_periods` (`period_id`, `education_year`, `period_name`, `education_type`, `start_date`, `end_date`, `is_completed`, `completed_at`, `completed_by`, `description`, `auto_pass_setting`, `created_by`, `created_at`, `updated_at`) VALUES
	(24, 2025, '13535', '온라인', '2025-06-05', '2025-06-13', 0, NULL, NULL, '', 1, 'admin', '2025-06-26 04:24:55', '2025-06-26 05:59:43'),
	(25, 2025, '1차 오프라인 교육', '오프라인', '2025-02-05', '2025-03-02', 1, '2025-06-26 04:39:11', 'admin', '', 1, 'admin', '2025-06-26 04:37:53', '2025-06-26 04:39:11'),
	(27, 2025, '3차 오프라인 교육', '오프라인', '2025-11-13', '2025-11-15', 1, '2025-06-26 05:37:46', 'admin', '', 1, 'admin', '2025-06-26 04:39:39', '2025-06-26 05:37:46'),
	(28, 2025, '2차 온라인 교육', '온라인', '2025-12-11', '2025-12-13', 1, '2025-06-26 05:37:53', 'admin', '', 1, 'admin', '2025-06-26 04:41:47', '2025-06-26 05:37:53');

-- 테이블 patch_management.security_score_summary 구조 내보내기
DROP TABLE IF EXISTS `security_score_summary`;
CREATE TABLE IF NOT EXISTS `security_score_summary` (
  `summary_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL COMMENT 'users 테이블의 uid 참조',
  `evaluation_year` int(11) NOT NULL COMMENT '평가 연도',
  `audit_penalty` decimal(5,2) DEFAULT 0.00 COMMENT '감사 감점 (실패 항목 * 0.5)',
  `education_penalty` decimal(5,2) DEFAULT 0.00 COMMENT '교육 감점 (미완료 기간당 0.5점)',
  `training_penalty` decimal(5,2) DEFAULT 0.00 COMMENT '모의훈련 감점 (실패 * 0.5)',
  `total_penalty` decimal(5,2) DEFAULT 0.00 COMMENT '총 감점 (최대 -5.0점)',
  `audit_failed_count` int(11) DEFAULT 0 COMMENT '감사 실패 항목 수',
  `education_incomplete_count` int(11) DEFAULT 0 COMMENT '미완료 교육 기간 수 (0.5점씩 감점)',
  `training_failed_count` int(11) DEFAULT 0 COMMENT '모의훈련 실패 횟수',
  `last_calculated` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`summary_id`),
  UNIQUE KEY `uk_user_year` (`user_id`,`evaluation_year`),
  KEY `idx_evaluation_year` (`evaluation_year`),
  CONSTRAINT `fk_score_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=200 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='KPI 보안 점수 요약 (교육 기간별 감점 기준)';

-- 테이블 데이터 patch_management.security_score_summary:~5 rows (대략적) 내보내기
DELETE FROM `security_score_summary`;
INSERT INTO `security_score_summary` (`summary_id`, `user_id`, `evaluation_year`, `audit_penalty`, `education_penalty`, `training_penalty`, `total_penalty`, `audit_failed_count`, `education_incomplete_count`, `training_failed_count`, `last_calculated`, `created_at`) VALUES
	(195, 1, 2025, 1.00, 0.50, 0.00, 1.50, 1, 1, 0, '2025-06-29 12:13:27', '2025-06-24 01:49:05'),
	(196, 2, 2025, 0.00, 0.00, 0.00, 0.00, 0, 0, 0, '2025-06-24 01:49:05', '2025-06-24 01:49:05'),
	(197, 3, 2025, 0.00, 0.00, 0.00, 0.00, 0, 0, 0, '2025-06-24 01:49:05', '2025-06-24 01:49:05'),
	(198, 4, 2025, 0.00, 0.00, 0.00, 0.00, 0, 0, 0, '2025-06-24 01:49:05', '2025-06-24 01:49:05'),
	(199, 5, 2025, 0.00, 0.00, 0.00, 0.00, 0, 0, 0, '2025-06-24 01:49:05', '2025-06-24 01:49:05');

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
  `role` enum('admin','user') DEFAULT 'user',
  PRIMARY KEY (`uid`),
  UNIQUE KEY `uk_user_id` (`user_id`),
  KEY `idx_username` (`username`),
  KEY `idx_department` (`department`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 정보';

-- 테이블 데이터 patch_management.users:~5 rows (대략적) 내보내기
DELETE FROM `users`;
INSERT INTO `users` (`uid`, `user_id`, `username`, `mail`, `department`, `created_at`, `updated_at`, `last_updated`, `ip`, `mac`, `role`) VALUES
	(1, 'eunjekim8', '김은제', 'eunjekim8@test.com', '운영실', '2025-06-09 06:39:36', '2025-06-20 02:39:12', '2025-06-20 02:39:12', '127.0.0.1, 10.106.15.129', NULL, 'admin'),
	(2, 'penguin', '펭귄', 'penguin@test.com', '남극', '2025-06-09 06:39:36', '2025-06-09 06:43:14', '2025-06-09 06:43:14', '10.24.13.24', NULL, 'user'),
	(3, 'dog', '강아지', 'dog@test.com', '동물원', '2025-06-09 06:39:36', '2025-06-20 04:55:49', '2025-06-20 04:55:49', '10.106.15.108', NULL, 'user'),
	(4, 'admin', '관리자', 'admin@test.com', '관리실', '2025-06-09 06:39:36', '2025-06-20 02:39:07', '2025-06-20 02:39:07', '10.101.21.32', NULL, 'user'),
	(5, 'hamtori', '햄토리', 'hamtori@test.com', '개발실', '2025-06-09 06:39:36', '2025-06-14 09:29:24', '2025-06-14 09:29:24', '32.13.4.23, 172.30.1.38', NULL, 'user');

-- 테이블 patch_management.user_exceptions 구조 내보내기
DROP TABLE IF EXISTS `user_exceptions`;
CREATE TABLE IF NOT EXISTS `user_exceptions` (
  `exception_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL COMMENT 'users 테이블의 uid 참조',
  `item_id` varchar(255) NOT NULL COMMENT '항목 ID (audit: 숫자, education/training: 문자열)',
  `item_type` enum('audit','education','training') NOT NULL COMMENT '항목 유형',
  `item_name` varchar(255) NOT NULL COMMENT '항목명',
  `item_category` varchar(100) NOT NULL COMMENT '항목 카테고리',
  `exclude_reason` varchar(255) NOT NULL COMMENT '제외 사유',
  `exclude_type` enum('permanent','temporary') DEFAULT 'permanent' COMMENT '제외 유형',
  `start_date` date DEFAULT NULL COMMENT '제외 시작일 (temporary인 경우)',
  `end_date` date DEFAULT NULL COMMENT '제외 종료일 (temporary인 경우)',
  `created_by` varchar(50) NOT NULL COMMENT '설정한 관리자',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `is_active` tinyint(1) DEFAULT 1 COMMENT '활성 상태',
  PRIMARY KEY (`exception_id`),
  UNIQUE KEY `uk_user_item_exception` (`user_id`,`item_id`,`item_type`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_item_type` (`item_type`),
  KEY `idx_active` (`is_active`),
  KEY `idx_user_exceptions_search` (`user_id`,`item_type`,`is_active`),
  KEY `idx_item_search` (`item_id`,`item_type`),
  CONSTRAINT `fk_user_exception` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='통합 사용자별 예외 설정 테이블';

-- 테이블 데이터 patch_management.user_exceptions:~0 rows (대략적) 내보내기
DELETE FROM `user_exceptions`;

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
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자별 확장 감사 항목 제외 설정 (감사/교육/훈련)';

-- 테이블 데이터 patch_management.user_extended_exceptions:~4 rows (대략적) 내보내기
DELETE FROM `user_extended_exceptions`;
INSERT INTO `user_extended_exceptions` (`exception_id`, `user_id`, `item_id`, `item_type`, `item_name`, `item_category`, `exclude_reason`, `exclude_type`, `start_date`, `end_date`, `created_by`, `created_at`, `updated_at`, `is_active`) VALUES
	(18, 5, 'training_2025_first_half', 'training_period', '2025년 상반기 악성메일 모의훈련', '악성메일 모의훈련', '135', 'permanent', NULL, NULL, 'admin', '2025-06-15 14:28:10', '2025-06-15 14:41:08', 0),
	(19, 5, 'training_period', 'training_period', '2025년 first_half(상반기) 모의훈련', '모의훈련', '관리자 설정', 'permanent', NULL, NULL, 'admin', '2025-06-15 14:41:14', '2025-06-15 14:41:49', 1),
	(20, 3, 'training_period', 'training_period', '2025년 first_half(상반기) 모의훈련', '모의훈련', '관리자 설정', 'permanent', NULL, NULL, 'eunjekim8', '2025-06-25 00:47:46', '2025-06-25 00:47:46', 1),
	(21, 4, 'training_period', 'training_period', '2025년 first_half(상반기) 모의훈련', '모의훈련', '관리자 설정', 'permanent', NULL, NULL, 'eunjekim8', '2025-06-25 00:47:48', '2025-06-25 00:47:48', 1);

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
  CONSTRAINT `fk_exception_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자별 감사 항목 제외 설정';

-- 테이블 데이터 patch_management.user_item_exceptions:~4 rows (대략적) 내보내기
DELETE FROM `user_item_exceptions`;
INSERT INTO `user_item_exceptions` (`exception_id`, `user_id`, `item_id`, `exclude_reason`, `exclude_type`, `start_date`, `end_date`, `created_by`, `created_at`, `updated_at`, `is_active`, `item_type`, `item_name`, `item_category`) VALUES
	(19, 5, 9, '135', 'permanent', NULL, NULL, 'admin', '2025-06-15 14:03:27', '2025-06-15 14:41:57', 0, 'manual', 'PC 봉인씰 확인', '물리보안'),
	(20, 5, 6, '135', 'permanent', NULL, NULL, 'admin', '2025-06-15 14:03:49', '2025-06-15 14:24:12', 0, 'audit', '동일 패스워드 설정 제한', '접근통제'),
	(21, 5, 8, '135', 'permanent', NULL, NULL, 'admin', '2025-06-15 14:24:55', '2025-06-15 14:24:55', 1, 'audit', '원격데스크톱 제한', '접근통제'),
	(22, 1, 7, '테스트', 'permanent', NULL, NULL, 'eunjekim8', '2025-06-25 00:44:23', '2025-06-25 00:44:23', 1, 'audit', '공유폴더 확인', '접근통제');

-- 뷰 patch_management.user_phishing_summary 구조 내보내기
DROP VIEW IF EXISTS `user_phishing_summary`;
-- VIEW 종속성 오류를 극복하기 위해 임시 테이블을 생성합니다.
CREATE TABLE `user_phishing_summary` (
	`user_id` BIGINT(20) NOT NULL COMMENT 'JPA에서 Long 타입으로 매핑',
	`username` VARCHAR(1) NOT NULL COMMENT '사용자 로그인 ID' COLLATE 'utf8mb4_unicode_ci',
	`department` VARCHAR(1) NULL COMMENT '소속 부서' COLLATE 'utf8mb4_unicode_ci',
	`email` VARCHAR(1) NULL COMMENT '이메일 주소' COLLATE 'utf8mb4_unicode_ci',
	`training_year` INT(11) NULL COMMENT '훈련 연도',
	`total_trainings` BIGINT(21) NOT NULL,
	`success_count` BIGINT(21) NOT NULL,
	`fail_count` BIGINT(21) NOT NULL,
	`no_response_count` BIGINT(21) NOT NULL,
	`success_rate` DECIMAL(26,2) NULL,
	`penalty_score` DECIMAL(22,1) NOT NULL
) ENGINE=MyISAM;

-- 임시 테이블을 제거하고 최종 VIEW 구조를 생성
DROP TABLE IF EXISTS `phishing_training_stats`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `phishing_training_stats` AS select `pt`.`training_year` AS `training_year`,`pt`.`period_id` AS `period_id`,`ptp`.`period_name` AS `period_name`,`ptp`.`training_type` AS `training_type`,count(0) AS `total_targets`,count(case when `pt`.`training_result` = 'success' then 1 end) AS `success_count`,count(case when `pt`.`training_result` = 'fail' then 1 end) AS `fail_count`,count(case when `pt`.`training_result` = 'no_response' then 1 end) AS `no_response_count`,round(count(case when `pt`.`training_result` = 'success' then 1 end) / count(0) * 100,2) AS `success_rate`,round(count(case when `pt`.`training_result` = 'fail' then 1 end) / count(0) * 100,2) AS `fail_rate` from (`phishing_training` `pt` join `phishing_training_periods` `ptp` on(`pt`.`period_id` = `ptp`.`period_id`)) where `pt`.`exclude_from_scoring` = 0 group by `pt`.`training_year`,`pt`.`period_id`,`ptp`.`period_name`,`ptp`.`training_type`
;

-- 임시 테이블을 제거하고 최종 VIEW 구조를 생성
DROP TABLE IF EXISTS `user_phishing_summary`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `user_phishing_summary` AS select `u`.`uid` AS `user_id`,`u`.`user_id` AS `username`,`u`.`department` AS `department`,`u`.`mail` AS `email`,`pt`.`training_year` AS `training_year`,count(0) AS `total_trainings`,count(case when `pt`.`training_result` = 'success' then 1 end) AS `success_count`,count(case when `pt`.`training_result` = 'fail' then 1 end) AS `fail_count`,count(case when `pt`.`training_result` = 'no_response' then 1 end) AS `no_response_count`,round(count(case when `pt`.`training_result` = 'success' then 1 end) / count(0) * 100,2) AS `success_rate`,count(case when `pt`.`training_result` = 'fail' then 1 end) * 0.5 AS `penalty_score` from (`users` `u` left join `phishing_training` `pt` on(`u`.`uid` = `pt`.`user_id` and `pt`.`exclude_from_scoring` = 0)) group by `u`.`uid`,`u`.`user_id`,`u`.`department`,`u`.`mail`,`pt`.`training_year`
;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
