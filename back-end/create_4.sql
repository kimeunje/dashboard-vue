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
  `log_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'JPA에서 Long 타입으로 매핑',
  `user_id` bigint(20) NOT NULL COMMENT '사용자 UID (Foreign Key)',
  `item_id` bigint(20) NOT NULL COMMENT '체크리스트 항목 ID (Foreign Key)',
  `actual_value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'JSON 형태의 실제 값',
  `passed` tinyint(1) DEFAULT NULL COMMENT '통과 여부 (Boolean)',
  `notes` text DEFAULT NULL COMMENT '비고',
  `checked_at` timestamp NULL DEFAULT current_timestamp() COMMENT '점검 일시',
  PRIMARY KEY (`log_id`),
  KEY `fk_audit_log_user` (`user_id`),
  KEY `fk_audit_log_item` (`item_id`),
  KEY `idx_checked_at` (`checked_at`),
  KEY `idx_passed` (`passed`),
  CONSTRAINT `fk_audit_log_item` FOREIGN KEY (`item_id`) REFERENCES `checklist_items` (`item_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_audit_log_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=732 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='감사 로그';

-- 테이블 데이터 patch_management.audit_log:~10 rows (대략적) 내보내기
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
	(730, 1, 1, '{"screenSaverTime": "300", "screenSaverSecure": "0", "screenSaverEnabled": "1"}', 0, '화면 보호기 시간이 짧고 암호 설정이 안되어 있습니다.', '2025-06-01 13:49:21'),
	(731, 2, 9, '{"Domain": 1, "Private": 1, "Public": 0}', 0, '일부 방화벽 프로필(Public)이 비활성화되어 있습니다.', '2025-06-01 13:49:21');

-- 테이블 patch_management.checklist_items 구조 내보내기
DROP TABLE IF EXISTS `checklist_items`;
CREATE TABLE IF NOT EXISTS `checklist_items` (
  `item_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'JPA에서 Long 타입으로 매핑',
  `category` varchar(100) NOT NULL COMMENT '카테고리',
  `item_name` varchar(200) NOT NULL COMMENT '항목명',
  `description` text DEFAULT NULL COMMENT '설명',
  `check_type` varchar(20) DEFAULT 'daily' COMMENT '점검 유형 (daily, manual)',
  `check_frequency` varchar(50) DEFAULT '매일' COMMENT '점검 주기',
  PRIMARY KEY (`item_id`),
  KEY `idx_check_type` (`check_type`),
  KEY `idx_category` (`category`),
  KEY `idx_item_name` (`item_name`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='체크리스트 항목';

-- 테이블 데이터 patch_management.checklist_items:~14 rows (대략적) 내보내기
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
	(9, '네트워크 점검', '방화벽 활성화 확인', '방화벽 프로필 활성화 상태 확인', 'daily', '매일'),
	(10, '시스템 보안', 'OS 패치 확인', '운영체제 보안 패치 적용 상태 확인', 'daily', '매일'),
	(25, '물리적 보안', 'PC 봉인씰 상태 확인', 'PC 케이스의 봉인씰 훼손 여부를 육안으로 확인', 'manual', '수시'),
	(26, '악성코드 점검', '악성코드 탐지 이력 확인', '시스템에서 발견된 악성코드 탐지 이력 및 처리 현황 확인', 'manual', '수시'),
	(27, '정보보호', '개인정보 암호화 상태 확인', '개인정보가 포함된 파일의 암호화 적용 여부 확인', 'manual', '수시'),
	(28, '시스템 보안', '이동매체 자동실행 제한', '이동식 미디어 자동실행 제한 상태 확인', 'manual', '주간');

-- 테이블 patch_management.phishing_training 구조 내보내기
DROP TABLE IF EXISTS `phishing_training`;
CREATE TABLE IF NOT EXISTS `phishing_training` (
  `training_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'JPA에서 Long 타입으로 매핑',
  `user_id` bigint(20) NOT NULL COMMENT '사용자 UID (Foreign Key)',
  `training_year` int(11) NOT NULL COMMENT '훈련 연도',
  `training_period` varchar(20) NOT NULL COMMENT '훈련 기간 (first_half, second_half)',
  `email_sent_time` timestamp NULL DEFAULT NULL COMMENT '모의 메일 발송 시각',
  `action_time` timestamp NULL DEFAULT NULL COMMENT '사용자 액션 수행 시각',
  `log_type` varchar(100) DEFAULT NULL COMMENT '로그 유형',
  `mail_type` varchar(200) DEFAULT NULL COMMENT '모의 메일 유형',
  `user_email` varchar(100) DEFAULT NULL COMMENT '사용자 이메일',
  `ip_address` varchar(45) DEFAULT NULL COMMENT 'IP 주소',
  `training_result` varchar(20) DEFAULT 'pending' COMMENT '훈련 결과 (pass, fail, pending)',
  `response_time_minutes` int(11) DEFAULT NULL COMMENT '응답 시간 (분)',
  `training_score` double DEFAULT NULL COMMENT '훈련 점수',
  `exclude_from_scoring` tinyint(1) DEFAULT 0 COMMENT '점수 계산 제외 여부 (Boolean)',
  `notes` text DEFAULT NULL COMMENT '비고',
  `created_at` timestamp NULL DEFAULT current_timestamp() COMMENT '생성일',
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '수정일',
  PRIMARY KEY (`training_id`),
  UNIQUE KEY `uk_training_unique` (`user_id`,`training_year`,`training_period`),
  KEY `idx_training_year` (`training_year`),
  KEY `idx_training_period` (`training_period`),
  KEY `idx_training_result` (`training_result`),
  KEY `idx_email_sent_time` (`email_sent_time`),
  CONSTRAINT `fk_phishing_training_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='악성메일 모의훈련 현황';

-- 테이블 데이터 patch_management.phishing_training:~14 rows (대략적) 내보내기
DELETE FROM `phishing_training`;
INSERT INTO `phishing_training` (`training_id`, `user_id`, `training_year`, `training_period`, `email_sent_time`, `action_time`, `log_type`, `mail_type`, `user_email`, `ip_address`, `training_result`, `response_time_minutes`, `training_score`, `exclude_from_scoring`, `notes`, `created_at`, `updated_at`) VALUES
	(33, 2, 2024, 'first_half', '2024-05-15 10:44:25', '2024-05-15 10:44:59', '스크립트 첨부파일 열람', '퇴직연금 운용상품 안내 (HTML)', 'kim.cs@company.com', '192.168.1.101', 'fail', 1, 40, 0, '모의훈련 실패 - 첨부파일 열람', '2025-05-28 00:47:12', '2025-06-01 13:52:34'),
	(34, 2, 2024, 'second_half', '2024-08-22 16:32:25', '2024-08-22 16:42:25', '스크립트 첨부파일 열람', '세금계산서 안내', 'parkchul@test.com', '50.24.11.35', 'fail', 10, 40, 0, '', '2025-05-28 00:47:12', '2025-06-01 13:52:34'),
	(37, 4, 2024, 'first_half', '2024-05-18 13:20:10', NULL, NULL, '회사 정책 변경 안내', 'park.ms@company.com', NULL, 'pass', NULL, 95, 0, '모의훈련 통과', '2025-05-28 00:47:12', '2025-06-01 13:52:34'),
	(38, 4, 2024, 'second_half', '2024-11-25 16:45:20', '2024-11-25 16:50:35', '첨부파일 다운로드', '세무 관련 서류 검토 요청', 'park.ms@company.com', '192.168.1.103', 'fail', 5, 40, 1, '모의훈련 실패 - 점수 계산 제외', '2025-05-28 00:47:12', '2025-06-01 13:52:34'),
	(39, 2, 2025, 'first_half', '2024-05-20 09:15:30', NULL, NULL, 'IT 보안 정책 업데이트', 'kim.cs@company.com', NULL, 'pass', NULL, 95, 0, '모의훈련 통과 - 의심스러운 메일 신고', '2025-05-28 00:47:12', '2025-06-01 13:52:34'),
	(41, 4, 2025, 'first_half', '2025-05-25 11:20:15', NULL, NULL, '휴가 신청서 양식 변경', 'park.ms@company.com', NULL, 'pass', NULL, 95, 0, '모의훈련 통과', '2025-05-28 00:47:12', '2025-06-01 13:52:34'),
	(43, 1, 2025, 'first_half', '2025-04-22 10:44:25', '2025-04-22 10:34:25', '스크립트 첨부파일 열람', '세금계산서 안내', 'test1@test.com', '103.34.21.35', 'fail', -10, 40, 0, '', '2025-05-28 07:59:22', '2025-06-01 13:52:34'),
	(46, 4, 2025, 'second_half', '2025-10-22 10:44:25', '2025-10-22 10:54:25', '악성 메일 클릭', '운용상품 안내', 'kimeunje@test.com', '1.35.2.62', 'fail', 10, 40, 0, '', '2025-05-28 07:59:23', '2025-06-01 13:52:34'),
	(51, 3, 2024, 'second_half', '2024-11-15 14:30:00', NULL, NULL, 'IT 보안 정책 업데이트 안내', 'kim.cs@company.com', NULL, 'pass', NULL, 95, 0, '모의훈련 통과 - 의심스러운 메일에 대해 액션하지 않음', '2025-05-28 13:20:29', '2025-06-01 13:52:34'),
	(54, 3, 2024, 'first_half', '2024-03-15 14:30:00', NULL, NULL, 'IT 보안 정책 업데이트 안내', 'kim.cs@company.com', NULL, 'pass', NULL, 95, 0, '모의훈련 통과 - 의심스러운 메일에 대해 액션하지 않음', '2025-05-28 13:20:51', '2025-06-01 13:52:34'),
	(55, 3, 2025, 'first_half', '2025-03-22 16:32:25', '2025-03-22 16:42:25', '스크립트 첨부파일 열람', '세금계산서 안내', 'parkchul@test.com', '50.24.11.35', 'fail', 10, 40, 0, '', '2025-05-28 00:47:12', '2025-06-01 13:52:34'),
	(56, 1, 2025, 'second_half', NULL, NULL, NULL, NULL, NULL, NULL, 'pending', NULL, NULL, 0, '훈련 미실시', '2025-06-01 13:49:21', '2025-06-01 13:49:21'),
	(57, 2, 2025, 'second_half', NULL, NULL, NULL, NULL, NULL, NULL, 'pending', NULL, NULL, 0, '훈련 미실시', '2025-06-01 13:49:21', '2025-06-01 13:49:21'),
	(58, 3, 2025, 'second_half', NULL, NULL, NULL, NULL, NULL, NULL, 'pending', NULL, NULL, 0, '훈련 미실시', '2025-06-01 13:49:21', '2025-06-01 13:49:21');

-- 테이블 patch_management.security_education 구조 내보내기
DROP TABLE IF EXISTS `security_education`;
CREATE TABLE IF NOT EXISTS `security_education` (
  `education_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'JPA에서 Long 타입으로 매핑',
  `user_id` bigint(20) NOT NULL COMMENT '사용자 UID (Foreign Key)',
  `education_year` int(11) NOT NULL COMMENT '교육 연도',
  `education_period` varchar(20) NOT NULL COMMENT '교육 기간 (first_half, second_half)',
  `education_type` varchar(50) DEFAULT '기본교육' COMMENT '교육 유형',
  `education_date` date DEFAULT NULL COMMENT '교육 이수일',
  `completion_status` tinyint(1) DEFAULT 0 COMMENT '이수 여부 (Boolean)',
  `score` double DEFAULT NULL COMMENT '교육 점수',
  `exclude_from_scoring` tinyint(1) DEFAULT 0 COMMENT '점수 계산 제외 여부 (Boolean)',
  `notes` text DEFAULT NULL COMMENT '비고',
  `created_at` timestamp NULL DEFAULT current_timestamp() COMMENT '생성일',
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '수정일',
  PRIMARY KEY (`education_id`),
  UNIQUE KEY `uk_education_unique` (`user_id`,`education_year`,`education_period`),
  KEY `idx_education_year` (`education_year`),
  KEY `idx_education_period` (`education_period`),
  KEY `idx_completion_status` (`completion_status`),
  KEY `idx_exclude_scoring` (`exclude_from_scoring`),
  CONSTRAINT `fk_security_education_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='보안 교육 현황';

-- 테이블 데이터 patch_management.security_education:~20 rows (대략적) 내보내기
DELETE FROM `security_education`;
INSERT INTO `security_education` (`education_id`, `user_id`, `education_year`, `education_period`, `education_type`, `education_date`, `completion_status`, `score`, `exclude_from_scoring`, `notes`, `created_at`, `updated_at`) VALUES
	(1, 1, 2025, 'first_half', '기본교육', '2025-06-15', 1, 85, 0, '상반기 정보보호 기본교육 이수', '2025-05-27 14:09:15', '2025-05-27 14:09:15'),
	(2, 1, 2025, 'second_half', '기본교육', NULL, 0, NULL, 0, '하반기 교육 미이수', '2025-05-27 14:09:15', '2025-05-27 14:09:15'),
	(3, 2, 2025, 'first_half', '기본교육', '2025-06-20', 1, 92, 0, '상반기 정보보호 기본교육 이수', '2025-05-27 14:09:15', '2025-05-27 14:09:15'),
	(4, 2, 2025, 'second_half', '기본교육', '2025-12-10', 1, 88, 0, '하반기 정보보호 기본교육 이수', '2025-05-27 14:09:15', '2025-05-27 14:09:15'),
	(5, 3, 2025, 'first_half', '기본교육', NULL, 0, NULL, 1, '상반기 교육 미실시 - 점수 계산 제외', '2025-05-27 14:09:15', '2025-05-27 14:09:15'),
	(6, 3, 2025, 'second_half', '기본교육', NULL, 0, NULL, 0, '하반기 교육 미이수', '2025-05-27 14:09:15', '2025-05-27 14:09:15'),
	(7, 4, 2025, 'first_half', '기본교육', '2025-06-18', 1, 78, 0, '상반기 정보보호 기본교육 이수', '2025-05-27 14:09:15', '2025-05-27 14:09:15'),
	(8, 4, 2025, 'second_half', '기본교육', NULL, 0, NULL, 0, '하반기 교육 미이수', '2025-05-27 14:09:15', '2025-05-27 14:09:15'),
	(9, 5, 2025, 'first_half', '관리자교육', '2025-06-10', 1, 95, 0, '관리자 대상 심화 정보보호 교육 이수', '2025-06-01 13:50:42', '2025-06-01 13:50:42'),
	(10, 5, 2025, 'second_half', '관리자교육', '2025-12-05', 1, 98, 0, '관리자 대상 심화 정보보호 교육 이수', '2025-06-01 13:50:42', '2025-06-01 13:50:42'),
	(11, 6, 2025, 'first_half', '기본교육', '2025-06-25', 1, 82, 0, '상반기 정보보호 기본교육 이수', '2025-06-01 13:50:42', '2025-06-01 13:50:42'),
	(12, 6, 2025, 'second_half', '기본교육', NULL, 0, NULL, 0, '하반기 교육 미이수', '2025-06-01 13:50:42', '2025-06-01 13:50:42'),
	(13, 1, 2024, 'first_half', '기본교육', '2024-06-15', 1, 88, 0, '2024년 상반기 정보보호 기본교육 이수', '2024-06-15 14:09:15', '2024-06-15 14:09:15'),
	(14, 1, 2024, 'second_half', '기본교육', '2024-12-10', 1, 90, 0, '2024년 하반기 정보보호 기본교육 이수', '2024-12-10 14:09:15', '2024-12-10 14:09:15'),
	(15, 2, 2024, 'first_half', '기본교육', '2024-06-18', 1, 85, 0, '2024년 상반기 정보보호 기본교육 이수', '2024-06-18 14:09:15', '2024-06-18 14:09:15'),
	(16, 2, 2024, 'second_half', '기본교육', '2024-12-08', 1, 87, 0, '2024년 하반기 정보보호 기본교육 이수', '2024-12-08 14:09:15', '2024-12-08 14:09:15'),
	(17, 3, 2024, 'first_half', '기본교육', '2024-06-20', 1, 80, 0, '2024년 상반기 정보보호 기본교육 이수', '2024-06-20 14:09:15', '2024-06-20 14:09:15'),
	(18, 3, 2024, 'second_half', '기본교육', NULL, 0, NULL, 0, '2024년 하반기 교육 미이수', '2024-12-31 14:09:15', '2024-12-31 14:09:15'),
	(19, 4, 2024, 'first_half', '기본교육', '2024-06-22', 1, 75, 0, '2024년 상반기 정보보호 기본교육 이수', '2024-06-22 14:09:15', '2024-06-22 14:09:15'),
	(20, 4, 2024, 'second_half', '기본교육', '2024-12-12', 1, 79, 0, '2024년 하반기 정보보호 기본교육 이수', '2024-12-12 14:09:15', '2024-12-12 14:09:15');

-- 테이블 patch_management.security_score_summary 구조 내보내기
DROP TABLE IF EXISTS `security_score_summary`;
CREATE TABLE IF NOT EXISTS `security_score_summary` (
  `summary_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'JPA에서 Long 타입으로 매핑',
  `user_id` bigint(20) NOT NULL COMMENT '사용자 UID (Foreign Key)',
  `evaluation_year` int(11) NOT NULL COMMENT '평가 연도',
  `audit_score` double DEFAULT 100 COMMENT '상시감사 점수',
  `education_penalty` double DEFAULT 0 COMMENT '교육 미이수 감점',
  `training_penalty` double DEFAULT 0 COMMENT '모의훈련 감점',
  `total_score` double DEFAULT 100 COMMENT '총 점수',
  `grade` varchar(2) DEFAULT NULL COMMENT '등급',
  `education_completed_count` int(11) DEFAULT 0 COMMENT '교육 이수 횟수',
  `education_total_count` int(11) DEFAULT 0 COMMENT '교육 대상 총 횟수',
  `training_passed_count` int(11) DEFAULT 0 COMMENT '모의훈련 통과 횟수',
  `training_total_count` int(11) DEFAULT 0 COMMENT '모의훈련 대상 총 횟수',
  `last_calculated` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '최종 계산일',
  PRIMARY KEY (`summary_id`),
  UNIQUE KEY `uk_score_unique` (`user_id`,`evaluation_year`),
  KEY `idx_total_score` (`total_score`),
  KEY `idx_grade` (`grade`),
  CONSTRAINT `fk_security_score_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`uid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='보안 점수 요약';

-- 테이블 데이터 patch_management.security_score_summary:~10 rows (대략적) 내보내기
DELETE FROM `security_score_summary`;
INSERT INTO `security_score_summary` (`summary_id`, `user_id`, `evaluation_year`, `audit_score`, `education_penalty`, `training_penalty`, `total_score`, `grade`, `education_completed_count`, `education_total_count`, `training_passed_count`, `training_total_count`, `last_calculated`) VALUES
	(1, 1, 2025, 85.5, 0.5, 0.5, 84.5, 'B+', 1, 2, 0, 1, '2025-06-01 13:52:34'),
	(2, 2, 2025, 92, 0, 0.5, 91.5, 'A', 2, 2, 1, 2, '2025-06-01 13:52:34'),
	(3, 3, 2025, 78, 0.5, 0.5, 77, 'C+', 0, 1, 1, 2, '2025-06-01 13:52:34'),
	(4, 4, 2025, 88.5, 0.5, 0, 88, 'B+', 1, 2, 1, 2, '2025-06-01 13:52:34'),
	(5, 5, 2025, 95, 0, 0, 95, 'A+', 2, 2, 0, 0, '2025-06-01 13:52:34'),
	(6, 6, 2025, 82, 0.5, 0, 81.5, 'B', 1, 2, 0, 0, '2025-06-01 13:52:34'),
	(7, 1, 2024, 90, 0, 0, 90, 'A', 2, 2, 0, 0, '2024-12-31 23:59:59'),
	(8, 2, 2024, 88.5, 0, 1, 87.5, 'B+', 2, 2, 0, 2, '2024-12-31 23:59:59'),
	(9, 3, 2024, 85, 0.5, 0, 84.5, 'B+', 1, 2, 1, 2, '2024-12-31 23:59:59'),
	(10, 4, 2024, 92, 0, 0.5, 91.5, 'A', 2, 2, 1, 2, '2024-12-31 23:59:59');

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
	(1, 'test1', '테스터1', 'test1@test.com', '운영실', '2025-05-28 14:58:32', '2025-05-28 14:58:32', '2025-05-28 14:58:32'),
	(2, 'parkchul', '박철희', 'parkchul@test.com', '개발팀', '2025-05-21 08:15:45', '2025-05-21 08:15:45', '2025-05-21 08:15:45'),
	(3, 'eunjekim8', '김은제', 'test@test.com', '운영실', '2025-05-30 14:12:17', '2025-05-30 14:12:17', '2025-05-30 14:12:17'),
	(4, 'kimeunje', '김은제2', 'kimeunje@test.com', '운영실', '2025-05-21 08:15:41', '2025-05-21 08:15:41', '2025-05-21 08:15:41'),
	(5, 'admin', '관리자', 'admin@test.com', 'IT팀', '2025-06-01 13:49:21', '2025-06-01 13:49:21', '2025-06-01 13:49:21'),
	(6, 'test', '테스터', 'test@test.com', '운영실', '2025-06-01 13:49:21', '2025-06-01 13:49:21', '2025-06-01 13:49:21');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
