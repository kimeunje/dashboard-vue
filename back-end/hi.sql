/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

DROP DATABASE IF EXISTS `audit_management`;
CREATE DATABASE IF NOT EXISTS `audit_management` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci */;
USE `audit_management`;

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
) ENGINE=InnoDB AUTO_INCREMENT=427 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='보안 감사 로그';

DELETE FROM `audit_log`;
INSERT INTO `audit_log` (`log_id`, `user_id`, `item_id`, `actual_value`, `passed`, `notes`, `exclude_reason`, `checked_at`) VALUES
	(93, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "600", "screenSaverSecure": "1"}', 1, '화면 보호기가 정상적으로 설정되어 있습니다.', NULL, '2025-08-20 07:38:05'),
	(94, 6, 2, '{"DisplayName": "알약", "RealTimeProtection": 1, "UpToDate": 1}', 1, '알약 백신이 정상적으로 설치되어 있으며, 실시간 보호 및 최신 업데이트가 적용되어 있습니다.', NULL, '2025-08-20 07:38:04'),
	(95, 6, 3, '{"minimumPasswordLength": "8"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-08-20 07:38:05'),
	(96, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-08-20 07:38:05'),
	(97, 6, 5, '{"maximumPasswordAge": "90"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-08-20 07:38:05'),
	(98, 6, 6, '{"passwordHistorySize": "5"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-08-20 07:38:05'),
	(99, 6, 7, '{"folders": ["ADMIN$", "C$", "IPC$"]}', 0, '불필요한 공유 폴더가 있습니다. 필요하지 않은 공유 폴더를 제거해주세요.', NULL, '2025-08-20 06:56:51'),
	(100, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-08-20 07:38:06'),
	(101, 6, 1, '{"screenSaverTime": "600", "screenSaverSecure": "1", "screenSaverEnabled": "1"}', 1, '화면 보호기가 정상적으로 설정되어 있습니다.', NULL, '2025-08-21 05:17:54'),
	(102, 6, 2, '{"UpToDate": 1, "DisplayName": "알약", "RealTimeProtection": 1}', 1, '알약 백신이 정상적으로 설치되어 있으며, 실시간 보호 및 최신 업데이트가 적용되어 있습니다.', NULL, '2025-08-21 05:17:53'),
	(103, 6, 3, '{"minimumPasswordLength": "8"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-08-21 05:17:55'),
	(104, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-08-21 05:17:55'),
	(105, 6, 5, '{"maximumPasswordAge": "90"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-08-21 05:17:56'),
	(106, 6, 6, '{"passwordHistorySize": "5"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-08-21 05:17:57'),
	(107, 6, 7, '{"folders": ["IPC$"]}', 1, '불필요한 공유 폴더가 없습니다.', NULL, '2025-08-21 05:17:58'),
	(108, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-08-21 05:17:59'),
	(109, 7, 1, '{"screenSaverTime": "600", "screenSaverSecure": "1", "screenSaverEnabled": "1"}', 1, '화면 보호기가 정상적으로 설정되어 있습니다.', NULL, '2025-08-21 05:27:47'),
	(110, 7, 2, '{"UpToDate": 1, "DisplayName": "알약", "RealTimeProtection": 1}', 1, '알약 백신이 정상적으로 설치되어 있으며, 실시간 보호 및 최신 업데이트가 적용되어 있습니다.', NULL, '2025-08-21 05:27:47'),
	(111, 7, 3, '{"minimumPasswordLength": "8"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-08-21 05:27:48'),
	(112, 7, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-08-21 05:27:49'),
	(113, 7, 5, '{"maximumPasswordAge": "90"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-08-21 05:27:50'),
	(114, 7, 6, '{"passwordHistorySize": "5"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-08-21 05:27:50'),
	(115, 7, 7, '{"folders": ["IPC$"]}', 1, '불필요한 공유 폴더가 없습니다.', NULL, '2025-08-21 05:27:52'),
	(116, 7, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-08-21 05:27:52'),
	(139, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "600", "screenSaverSecure": "1"}', 1, '화면 보호기가 정상적으로 설정되어 있습니다.', NULL, '2025-07-01 09:15:30'),
	(140, 6, 2, '{"DisplayName": "V3", "RealTimeProtection": 1, "UpToDate": 1}', 1, 'V3 백신이 정상적으로 설치되어 있으며, 실시간 보호 및 최신 업데이트가 적용되어 있습니다.', NULL, '2025-07-01 09:16:45'),
	(141, 6, 3, '{"minimumPasswordLength": "8"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-07-01 09:17:20'),
	(142, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-01 09:18:10'),
	(143, 6, 5, '{"maximumPasswordAge": "90"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-01 09:19:05'),
	(144, 6, 6, '{"passwordHistorySize": "5"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-01 09:20:15'),
	(145, 6, 7, '{"folders": ["ADMIN$", "C$", "IPC$", "공유폴더1"]}', 0, '불필요한 공유 폴더가 있습니다. 필요하지 않은 공유 폴더를 제거해주세요.', NULL, '2025-07-01 09:21:30'),
	(146, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-01 09:22:45'),
	(147, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "900", "screenSaverSecure": "1"}', 0, '화면 보호기 시간이 15분으로 설정되어 있어 보안 정책(10분)을 초과합니다.', NULL, '2025-07-02 14:30:20'),
	(148, 6, 2, '{"DisplayName": "알약", "RealTimeProtection": 1, "UpToDate": 1}', 1, '알약 백신이 정상적으로 설치되어 있으며, 실시간 보호 및 최신 업데이트가 적용되어 있습니다.', NULL, '2025-07-02 14:31:15'),
	(149, 6, 3, '{"minimumPasswordLength": "6"}', 0, '암호 길이가 6자로 설정되어 있어 정책(8자 이상)에 미달합니다.', NULL, '2025-07-02 14:32:40'),
	(150, 6, 4, '{"passwordComplexity": 0}', 0, '암호 복잡도가 비활성화되어 있습니다. 대소문자, 숫자, 특수문자 조합이 필요합니다.', NULL, '2025-07-02 14:33:25'),
	(151, 6, 5, '{"maximumPasswordAge": "120"}', 0, '암호 변경 주기가 120일로 설정되어 있어 정책(90일)을 초과합니다.', NULL, '2025-07-02 14:34:50'),
	(152, 6, 6, '{"passwordHistorySize": "3"}', 0, '암호 이력 관리가 3개로 설정되어 있어 정책(5개 이상) 미달입니다.', NULL, '2025-07-02 14:35:30'),
	(153, 6, 7, '{"folders": ["IPC$"]}', 1, '불필요한 공유 폴더가 없습니다.', NULL, '2025-07-02 14:36:45'),
	(154, 6, 8, '{"fDenyTSConnections": 0}', 0, '원격 데스크톱이 활성화되어 있어 보안상 위험합니다.', NULL, '2025-07-02 14:37:20'),
	(155, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "600", "screenSaverSecure": "1"}', 1, '화면 보호기 설정이 개선되었습니다.', NULL, '2025-07-03 08:45:15'),
	(156, 6, 2, '{"DisplayName": "Windows Defender", "RealTimeProtection": 0, "UpToDate": 1}', 0, 'Windows Defender의 실시간 보호가 비활성화되어 있습니다.', NULL, '2025-07-03 08:46:30'),
	(157, 6, 3, '{"minimumPasswordLength": "8"}', 1, '암호 길이 정책이 개선되었습니다.', NULL, '2025-07-03 08:47:20'),
	(158, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도 설정이 개선되었습니다.', NULL, '2025-07-03 08:48:40'),
	(159, 6, 5, '{"maximumPasswordAge": "90"}', 1, '암호 변경 주기가 정책에 맞게 수정되었습니다.', NULL, '2025-07-03 08:49:25'),
	(160, 6, 6, '{"passwordHistorySize": "5"}', 1, '암호 이력 관리가 정책에 맞게 설정되었습니다.', NULL, '2025-07-03 08:50:15'),
	(161, 6, 7, '{"folders": ["IPC$", "PRINT$"]}', 1, '시스템 필수 공유만 유지되고 있습니다.', NULL, '2025-07-03 08:51:30'),
	(162, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱 제한이 재설정되었습니다.', NULL, '2025-07-03 08:52:45'),
	(163, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "600", "screenSaverSecure": "1"}', 1, '화면 보호기가 정상적으로 설정되어 있습니다.', NULL, '2025-07-04 11:20:30'),
	(164, 6, 2, '{"DisplayName": "Kaspersky", "RealTimeProtection": 1, "UpToDate": 1}', 1, 'Kaspersky 백신이 정상적으로 설치되어 있으며, 실시간 보호 및 최신 업데이트가 적용되어 있습니다.', NULL, '2025-07-04 11:21:45'),
	(165, 6, 3, '{"minimumPasswordLength": "8"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-07-04 11:22:15'),
	(166, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-04 11:23:30'),
	(167, 6, 5, '{"maximumPasswordAge": "90"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-04 11:24:20'),
	(168, 6, 6, '{"passwordHistorySize": "5"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-04 11:25:40'),
	(169, 6, 7, '{"folders": ["IPC$"]}', 1, '불필요한 공유 폴더가 없습니다.', NULL, '2025-07-04 11:26:15'),
	(170, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-04 11:27:50'),
	(171, 6, 1, '{"checking": "in_progress"}', NULL, '화면 보호기 설정 점검 진행 중입니다.', NULL, '2025-07-05 09:30:20'),
	(172, 6, 2, '{"DisplayName": "알약", "RealTimeProtection": 1, "UpToDate": 1}', 1, '알약 백신이 정상적으로 설치되어 있으며, 실시간 보호 및 최신 업데이트가 적용되어 있습니다.', NULL, '2025-07-05 09:31:35'),
	(173, 6, 3, '{"scanning": "in_progress"}', NULL, '암호 정책 점검 진행 중입니다.', NULL, '2025-07-05 09:32:15'),
	(174, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-05 09:33:45'),
	(175, 6, 5, '{"maximumPasswordAge": "90"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-05 09:34:20'),
	(176, 6, 6, '{"passwordHistorySize": "5"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-05 09:35:30'),
	(177, 6, 7, '{"folders": ["IPC$"]}', 1, '불필요한 공유 폴더가 없습니다.', NULL, '2025-07-05 09:36:45'),
	(178, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-05 09:37:20'),
	(179, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "600", "screenSaverSecure": "1"}', 1, '화면 보호기가 정상적으로 설정되어 있습니다.', NULL, '2025-07-06 13:15:30'),
	(180, 6, 2, '{"DisplayName": "V3", "RealTimeProtection": 1, "UpToDate": 0}', 0, 'V3 백신이 설치되어 있으나 업데이트가 필요합니다.', NULL, '2025-07-06 13:16:45'),
	(181, 6, 3, '{"minimumPasswordLength": "8"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-07-06 13:17:20'),
	(182, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-06 13:18:10'),
	(183, 6, 5, '{"maximumPasswordAge": "90"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-06 13:19:05'),
	(184, 6, 6, '{"passwordHistorySize": "5"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-06 13:20:15'),
	(185, 6, 7, '{"folders": ["IPC$", "NETLOGON", "SYSVOL"]}', 0, '도메인 관련 공유 폴더가 발견되었습니다. 정책 확인이 필요합니다.', NULL, '2025-07-06 13:21:30'),
	(186, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-06 13:22:45'),
	(187, 6, 1, '{"screenSaverEnabled": "0", "screenSaverTime": "0", "screenSaverSecure": "0"}', 0, '화면 보호기가 비활성화되어 있습니다. 즉시 활성화가 필요합니다.', NULL, '2025-07-07 16:30:20'),
	(188, 6, 2, '{"DisplayName": "V3", "RealTimeProtection": 1, "UpToDate": 1}', 1, 'V3 백신 업데이트가 완료되었습니다.', NULL, '2025-07-07 16:31:35'),
	(189, 6, 3, '{"minimumPasswordLength": "8"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-07-07 16:32:15'),
	(190, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-07 16:33:45'),
	(191, 6, 5, '{"maximumPasswordAge": "90"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-07 16:34:20'),
	(192, 6, 6, '{"passwordHistorySize": "5"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-07 16:35:30'),
	(193, 6, 7, '{"folders": ["IPC$"]}', 1, '불필요한 공유 폴더 정리가 완료되었습니다.', NULL, '2025-07-07 16:36:45'),
	(194, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-07 16:37:20'),
	(195, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "600", "screenSaverSecure": "1"}', 1, '화면 보호기 설정이 복구되었습니다.', NULL, '2025-07-08 10:45:30'),
	(196, 6, 2, '{"DisplayName": "알약", "RealTimeProtection": 1, "UpToDate": 1}', 1, '알약 백신이 정상적으로 설치되어 있으며, 실시간 보호 및 최신 업데이트가 적용되어 있습니다.', NULL, '2025-07-08 10:46:45'),
	(197, 6, 3, '{"minimumPasswordLength": "10"}', 1, '암호 길이가 10자로 설정되어 더욱 강화되었습니다.', NULL, '2025-07-08 10:47:20'),
	(198, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-08 10:48:10'),
	(199, 6, 5, '{"maximumPasswordAge": "60"}', 1, '암호 변경 주기가 60일로 더욱 강화되었습니다.', NULL, '2025-07-08 10:49:05'),
	(200, 6, 6, '{"passwordHistorySize": "10"}', 1, '암호 이력 관리가 10개로 강화되었습니다.', NULL, '2025-07-08 10:50:15'),
	(201, 6, 7, '{"folders": ["IPC$"]}', 1, '불필요한 공유 폴더가 없습니다.', NULL, '2025-07-08 10:51:30'),
	(202, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-08 10:52:45'),
	(203, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "300", "screenSaverSecure": "1"}', 1, '화면 보호기가 5분으로 더욱 강화 설정되었습니다.', NULL, '2025-07-09 14:20:30'),
	(204, 6, 2, '{"DisplayName": "Kaspersky", "RealTimeProtection": 1, "UpToDate": 1}', 1, 'Kaspersky 백신으로 변경되어 보안이 강화되었습니다.', NULL, '2025-07-09 14:21:45'),
	(205, 6, 3, '{"minimumPasswordLength": "12"}', 1, '암호 길이가 12자로 더욱 강화되었습니다.', NULL, '2025-07-09 14:22:15'),
	(206, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-09 14:23:30'),
	(207, 6, 5, '{"maximumPasswordAge": "45"}', 1, '암호 변경 주기가 45일로 최대한 강화되었습니다.', NULL, '2025-07-09 14:24:20'),
	(208, 6, 6, '{"passwordHistorySize": "12"}', 1, '암호 이력 관리가 12개로 최대한 강화되었습니다.', NULL, '2025-07-09 14:25:40'),
	(209, 6, 7, '{"folders": ["IPC$"]}', 1, '불필요한 공유 폴더가 없습니다.', NULL, '2025-07-09 14:26:15'),
	(210, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-09 14:27:50'),
	(211, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "600", "screenSaverSecure": "1"}', 1, '화면 보호기가 정상적으로 설정되어 있습니다.', NULL, '2025-07-10 08:30:20'),
	(212, 6, 2, '{"DisplayName": "Norton", "RealTimeProtection": 1, "UpToDate": 1}', 1, 'Norton 백신이 정상적으로 설치되어 있으며, 실시간 보호 및 최신 업데이트가 적용되어 있습니다.', NULL, '2025-07-10 08:31:35'),
	(213, 6, 3, '{"minimumPasswordLength": "8"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-07-10 08:32:15'),
	(214, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-10 08:33:45'),
	(215, 6, 5, '{"maximumPasswordAge": "90"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-10 08:34:20'),
	(216, 6, 6, '{"passwordHistorySize": "5"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-10 08:35:30'),
	(217, 6, 7, '{"folders": ["IPC$", "Users"]}', 0, '사용자 공유 폴더가 활성화되어 있어 검토가 필요합니다.', NULL, '2025-07-10 08:36:45'),
	(218, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-10 08:37:20'),
	(219, 6, 1, '{"systemUpdate": "rebooting"}', NULL, '시스템 업데이트로 인해 재부팅 중입니다.', NULL, '2025-07-11 09:00:00'),
	(220, 6, 2, '{"checking": "post_update"}', NULL, '업데이트 후 백신 상태 확인 중입니다.', NULL, '2025-07-11 09:15:30'),
	(221, 6, 3, '{"minimumPasswordLength": "8"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-07-11 09:30:15'),
	(222, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-11 09:31:45'),
	(223, 6, 5, '{"maximumPasswordAge": "90"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-11 09:32:20'),
	(224, 6, 6, '{"passwordHistorySize": "5"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-11 09:33:30'),
	(225, 6, 7, '{"folders": ["IPC$"]}', 1, '업데이트 후 공유 폴더 정리가 완료되었습니다.', NULL, '2025-07-11 09:34:45'),
	(226, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-11 09:35:20'),
	(227, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "600", "screenSaverSecure": "1"}', 1, '화면 보호기가 정상적으로 설정되어 있습니다.', NULL, '2025-07-12 11:15:30'),
	(228, 6, 2, '{"DisplayName": "알약", "RealTimeProtection": 1, "UpToDate": 1}', 1, '알약 백신이 정상적으로 설치되어 있으며, 실시간 보호 및 최신 업데이트가 적용되어 있습니다.', NULL, '2025-07-12 11:16:45'),
	(229, 6, 3, '{"minimumPasswordLength": "8"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-07-12 11:17:20'),
	(230, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-12 11:18:10'),
	(231, 6, 5, '{"maximumPasswordAge": "90"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-12 11:19:05'),
	(232, 6, 6, '{"passwordHistorySize": "5"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-12 11:20:15'),
	(233, 6, 7, '{"folders": ["IPC$"]}', 1, '불필요한 공유 폴더가 없습니다.', NULL, '2025-07-12 11:21:30'),
	(234, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-12 11:22:45'),
	(235, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "900", "screenSaverSecure": "1"}', 0, '화면 보호기 시간이 15분으로 설정되어 있어 보안 정책을 초과합니다. 10분 이하로 설정해주세요.', NULL, '2025-07-13 08:45:20'),
	(236, 6, 2, '{"DisplayName": "V3", "RealTimeProtection": 1, "UpToDate": 0}', 0, 'V3 백신의 실시간 보호는 활성화되어 있으나 바이러스 정의 파일이 오래되었습니다. 즉시 업데이트가 필요합니다.', NULL, '2025-07-13 08:46:35'),
	(237, 6, 3, '{"minimumPasswordLength": "8"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-07-13 08:47:15'),
	(238, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-13 08:48:40'),
	(239, 6, 5, '{"maximumPasswordAge": "90"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-13 08:49:25'),
	(240, 6, 6, '{"passwordHistorySize": "5"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-13 08:50:15'),
	(241, 6, 7, '{"folders": ["IPC$", "공유문서", "프로젝트파일"]}', 0, '업무용 공유 폴더가 다수 발견되었습니다. 보안 정책에 따라 승인된 공유만 허용됩니다.', NULL, '2025-07-13 08:51:30'),
	(242, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-13 08:52:45'),
	(243, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "600", "screenSaverSecure": "1"}', 1, '화면 보호기 설정이 정책에 맞게 복구되었습니다.', NULL, '2025-07-14 20:30:20'),
	(244, 6, 2, '{"DisplayName": "V3", "RealTimeProtection": 1, "UpToDate": 1}', 1, 'V3 백신 업데이트가 완료되어 최신 상태를 유지하고 있습니다.', NULL, '2025-07-14 20:31:35'),
	(245, 6, 3, '{"minimumPasswordLength": "8"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-07-14 20:32:15'),
	(246, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-14 20:33:45'),
	(247, 6, 5, '{"maximumPasswordAge": "90"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-14 20:34:20'),
	(248, 6, 6, '{"passwordHistorySize": "5"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-14 20:35:30'),
	(249, 6, 7, '{"folders": ["IPC$"]}', 1, '불필요한 공유 폴더가 정리되었습니다.', NULL, '2025-07-14 20:36:45'),
	(250, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-14 20:37:20'),
	(251, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "600", "screenSaverSecure": "1"}', 1, '화면 보호기가 정상적으로 설정되어 있습니다.', NULL, '2025-07-15 13:10:30'),
	(252, 6, 2, '{"DisplayName": "Kaspersky", "RealTimeProtection": 1, "UpToDate": 1, "FirewallEnabled": 1}', 1, 'Kaspersky 백신으로 교체되었으며 실시간 보호, 방화벽 기능이 모두 정상 작동하고 있습니다.', NULL, '2025-07-15 13:11:45'),
	(253, 6, 3, '{"minimumPasswordLength": "10"}', 1, '암호 길이가 10자로 더욱 강화되어 설정되었습니다.', NULL, '2025-07-15 13:12:20'),
	(254, 6, 4, '{"passwordComplexity": 1, "mixedCase": 1, "numbers": 1, "symbols": 1}', 1, '암호 복잡도가 대소문자, 숫자, 특수문자 모든 요소를 포함하도록 설정되었습니다.', NULL, '2025-07-15 13:13:10'),
	(255, 6, 5, '{"maximumPasswordAge": "60"}', 1, '암호 변경 주기가 60일로 더욱 강화되었습니다.', NULL, '2025-07-15 13:14:05'),
	(256, 6, 6, '{"passwordHistorySize": "8"}', 1, '암호 이력 관리가 8개로 강화되어 설정되었습니다.', NULL, '2025-07-15 13:15:15'),
	(257, 6, 7, '{"folders": ["IPC$"]}', 1, '불필요한 공유 폴더가 없습니다.', NULL, '2025-07-15 13:16:30'),
	(258, 6, 8, '{"fDenyTSConnections": 1, "RDPPort": "disabled"}', 1, '원격 데스크톱이 완전히 비활성화되어 보안이 강화되었습니다.', NULL, '2025-07-15 13:17:45'),
	(259, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "300", "screenSaverSecure": "1"}', 1, '화면 보호기가 5분으로 더욱 강화 설정되어 보안성이 향상되었습니다.', NULL, '2025-07-16 09:25:30'),
	(260, 6, 2, '{"DisplayName": "Kaspersky", "RealTimeProtection": 1, "UpToDate": 1, "LastScan": "2025-07-16T01:00:00Z"}', 1, 'Kaspersky 백신이 새벽 1시에 정기 스캔을 완료했으며 위협이 발견되지 않았습니다.', NULL, '2025-07-16 09:26:45'),
	(261, 6, 3, '{"minimumPasswordLength": "10"}', 1, '암호 길이가 10자로 적절하게 설정되어 있습니다.', NULL, '2025-07-16 09:27:20'),
	(262, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-16 09:28:10'),
	(263, 6, 5, '{"maximumPasswordAge": "60"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-16 09:29:05'),
	(264, 6, 6, '{"passwordHistorySize": "8"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-16 09:30:15'),
	(265, 6, 7, '{"folders": ["IPC$"]}', 1, '불필요한 공유 폴더가 없습니다.', NULL, '2025-07-16 09:31:30'),
	(266, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-16 09:32:45'),
	(267, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "300", "screenSaverSecure": "1"}', 1, '화면 보호기가 강화된 설정으로 정상 작동하고 있습니다.', NULL, '2025-07-17 14:40:20'),
	(268, 6, 2, '{"DisplayName": "Kaspersky", "RealTimeProtection": 1, "UpToDate": 1}', 1, 'Kaspersky 백신이 정상적으로 설치되어 있으며, 실시간 보호 및 최신 업데이트가 적용되어 있습니다.', NULL, '2025-07-17 14:41:35'),
	(269, 6, 3, '{"minimumPasswordLength": "10"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-07-17 14:42:15'),
	(270, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-17 14:43:45'),
	(271, 6, 5, '{"maximumPasswordAge": "60"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-17 14:44:20'),
	(272, 6, 6, '{"passwordHistorySize": "8"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-17 14:45:30'),
	(273, 6, 7, '{"folders": ["IPC$", "TEMP_SHARE"]}', 0, '임시 공유 폴더가 발견되었습니다. 사용 후 즉시 제거가 필요합니다.', NULL, '2025-07-17 14:46:45'),
	(274, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-17 14:47:20'),
	(275, 6, 1, '{"checking": "hardware_update"}', NULL, '하드웨어 점검으로 인해 화면 보호기 설정 확인이 지연되고 있습니다.', NULL, '2025-07-18 11:00:00'),
	(276, 6, 2, '{"DisplayName": "Kaspersky", "RealTimeProtection": 1, "UpToDate": 1}', 1, 'Kaspersky 백신이 정상적으로 설치되어 있으며, 실시간 보호 및 최신 업데이트가 적용되어 있습니다.', NULL, '2025-07-18 11:15:35'),
	(277, 6, 3, '{"validating": "policy_update"}', NULL, '새로운 암호 정책 적용으로 인해 현재 설정을 검증 중입니다.', NULL, '2025-07-18 11:30:15'),
	(278, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-18 11:45:45'),
	(279, 6, 5, '{"maximumPasswordAge": "60"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-18 12:00:20'),
	(280, 6, 6, '{"passwordHistorySize": "8"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-18 12:15:30'),
	(281, 6, 7, '{"folders": ["IPC$"]}', 1, '임시 공유 폴더가 제거되어 정상 상태입니다.', NULL, '2025-07-18 12:30:45'),
	(282, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-18 12:45:20'),
	(283, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "300", "screenSaverSecure": "1"}', 1, '하드웨어 점검 완료 후 화면 보호기가 정상 작동하고 있습니다.', NULL, '2025-07-19 08:20:30'),
	(284, 6, 2, '{"DisplayName": "Kaspersky", "RealTimeProtection": 1, "UpToDate": 1, "QuarantineItems": 1}', 1, 'Kaspersky 백신이 의심스러운 파일 1개를 격리 처리했으며 시스템이 안전한 상태입니다.', NULL, '2025-07-19 08:21:45'),
	(285, 6, 3, '{"minimumPasswordLength": "12"}', 1, '새로운 정책에 따라 암호 길이가 12자로 더욱 강화되었습니다.', NULL, '2025-07-19 08:22:20'),
	(286, 6, 4, '{"passwordComplexity": 1, "specialCharacters": 2}', 1, '암호 복잡도가 특수문자 2개 이상 포함하도록 강화되었습니다.', NULL, '2025-07-19 08:23:10'),
	(287, 6, 5, '{"maximumPasswordAge": "45"}', 1, '암호 변경 주기가 45일로 더욱 강화되었습니다.', NULL, '2025-07-19 08:24:05'),
	(288, 6, 6, '{"passwordHistorySize": "10"}', 1, '암호 이력 관리가 10개로 최대한 강화되었습니다.', NULL, '2025-07-19 08:25:15'),
	(289, 6, 7, '{"folders": ["IPC$"]}', 1, '불필요한 공유 폴더가 없습니다.', NULL, '2025-07-19 08:26:30'),
	(290, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-19 08:27:45'),
	(291, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "300", "screenSaverSecure": "1"}', 1, '화면 보호기가 강화된 정책에 따라 정상 작동하고 있습니다.', NULL, '2025-07-20 16:50:30'),
	(292, 6, 2, '{"DisplayName": "Kaspersky", "RealTimeProtection": 1, "UpToDate": 1}', 1, 'Kaspersky 백신이 정상적으로 설치되어 있으며, 실시간 보호 및 최신 업데이트가 적용되어 있습니다.', NULL, '2025-07-20 16:51:45'),
	(293, 6, 3, '{"minimumPasswordLength": "12"}', 1, '암호 길이가 강화된 정책에 맞게 설정되어 있습니다.', NULL, '2025-07-20 16:52:20'),
	(294, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-20 16:53:10'),
	(295, 6, 5, '{"maximumPasswordAge": "45"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-20 16:54:05'),
	(296, 6, 6, '{"passwordHistorySize": "10"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-20 16:55:15'),
	(297, 6, 7, '{"folders": ["IPC$", "BACKUP_SHARE"]}', 0, '백업용 임시 공유 폴더가 발견되었으나 업무상 필요하여 제외 처리합니다.', '백업 업무용', '2025-07-20 16:56:30'),
	(298, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-20 16:57:45'),
	(299, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "300", "screenSaverSecure": "1"}', 1, '화면 보호기가 5분 강화 설정으로 정상 작동하고 있습니다.', NULL, '2025-07-21 15:15:30'),
	(300, 6, 2, '{"DisplayName": "Norton 360", "RealTimeProtection": 1, "UpToDate": 1, "CloudBackup": 1}', 1, 'Norton 360으로 업그레이드되어 실시간 보호와 클라우드 백업 기능이 추가되었습니다.', NULL, '2025-07-21 15:16:45'),
	(301, 6, 3, '{"minimumPasswordLength": "12"}', 1, '암호 길이가 12자로 강화된 정책에 맞게 설정되어 있습니다.', NULL, '2025-07-21 15:17:20'),
	(302, 6, 4, '{"passwordComplexity": 1, "specialCharacters": 2}', 1, '암호 복잡도가 강화된 정책에 맞게 설정되어 있습니다.', NULL, '2025-07-21 15:18:10'),
	(303, 6, 5, '{"maximumPasswordAge": "45"}', 1, '암호 변경 주기가 45일로 강화되어 적절하게 설정되어 있습니다.', NULL, '2025-07-21 15:19:05'),
	(304, 6, 6, '{"passwordHistorySize": "10"}', 1, '암호 이력 관리가 10개로 강화되어 적절하게 설정되어 있습니다.', NULL, '2025-07-21 15:20:15'),
	(305, 6, 7, '{"folders": ["IPC$", "개발공유", "프로젝트협업공간"]}', 0, '개발팀 전용 공유 폴더와 프로젝트 협업 공간이 있습니다. 업무상 필요하여 제외 처리됩니다.', '업무상 필요', '2025-07-21 15:21:30'),
	(306, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-21 15:22:45'),
	(307, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "300", "screenSaverSecure": "1"}', 1, '화면 보호기가 정상적으로 설정되어 있습니다.', NULL, '2025-07-22 09:30:20'),
	(308, 6, 2, '{"DisplayName": "Norton 360", "RealTimeProtection": 1, "UpToDate": 1, "ThreatsStopped": 3}', 1, 'Norton 360이 오늘 3개의 위협을 차단했으며 시스템이 안전하게 보호되고 있습니다.', NULL, '2025-07-22 09:31:35'),
	(309, 6, 3, '{"minimumPasswordLength": "12"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-07-22 09:32:15'),
	(310, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-22 09:33:45'),
	(311, 6, 5, '{"maximumPasswordAge": "45"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-22 09:34:20'),
	(312, 6, 6, '{"passwordHistorySize": "10"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-22 09:35:30'),
	(313, 6, 7, '{"folders": ["IPC$"]}', 1, '업무용 공유 폴더가 정리되어 불필요한 공유가 없습니다.', NULL, '2025-07-22 09:36:45'),
	(314, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-22 09:37:20'),
	(315, 6, 1, '{"screenSaverEnabled": "0", "userModified": "true"}', 0, '사용자가 화면 보호기를 임의로 비활성화했습니다. 정책에 따라 즉시 복구가 필요합니다.', NULL, '2025-07-23 13:45:30'),
	(316, 6, 2, '{"DisplayName": "Norton 360", "RealTimeProtection": 1, "UpToDate": 0, "LastUpdate": "2025-07-20"}', 0, 'Norton 360의 바이러스 정의 파일이 3일간 업데이트되지 않았습니다. 네트워크 연결을 확인하고 수동 업데이트를 실행해주세요.', NULL, '2025-07-23 13:46:45'),
	(317, 6, 3, '{"minimumPasswordLength": "12"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-07-23 13:47:20'),
	(318, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-23 13:48:10'),
	(319, 6, 5, '{"maximumPasswordAge": "45"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-23 13:49:05'),
	(320, 6, 6, '{"passwordHistorySize": "10"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-23 13:50:15'),
	(321, 6, 7, '{"folders": ["IPC$", "긴급업무공유", "임시프로젝트파일"]}', 0, '긴급 업무 처리를 위한 임시 공유 폴더들이 생성되었습니다. 업무 완료 후 즉시 제거 예정입니다.', NULL, '2025-07-23 13:51:30'),
	(322, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-23 13:52:45'),
	(323, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "300", "screenSaverSecure": "1", "autoRestore": "true"}', 1, '화면 보호기가 자동 복구 정책에 의해 재설정되었습니다.', NULL, '2025-07-24 10:15:30'),
	(324, 6, 2, '{"DisplayName": "Norton 360", "RealTimeProtection": 1, "UpToDate": 1, "ManualUpdate": "2025-07-24T09:00:00Z"}', 1, 'Norton 360 수동 업데이트가 완료되어 최신 상태로 복구되었습니다.', NULL, '2025-07-24 10:16:45'),
	(325, 6, 3, '{"minimumPasswordLength": "12"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-07-24 10:17:20'),
	(326, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-24 10:18:10'),
	(327, 6, 5, '{"maximumPasswordAge": "45"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-24 10:19:05'),
	(328, 6, 6, '{"passwordHistorySize": "10"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-24 10:20:15'),
	(329, 6, 7, '{"folders": ["IPC$"]}', 1, '긴급 업무용 임시 공유 폴더가 정리되었습니다.', NULL, '2025-07-24 10:21:30'),
	(330, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-24 10:22:45'),
	(331, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "300", "screenSaverSecure": "1", "biometricLock": "true"}', 1, '화면 보호기에 생체인식 잠금 기능이 추가되어 보안이 더욱 강화되었습니다.', NULL, '2025-07-25 10:30:20'),
	(332, 6, 2, '{"DisplayName": "Bitdefender Total Security", "RealTimeProtection": 1, "UpToDate": 1, "AdvancedThreatDefense": 1, "WebProtection": 1}', 1, 'Bitdefender Total Security로 변경되어 고급 위협 방어와 웹 보호 기능이 추가되었습니다.', NULL, '2025-07-25 10:31:35'),
	(333, 6, 3, '{"minimumPasswordLength": "14"}', 1, '암호 길이가 14자로 더욱 강화되어 최고 수준의 보안을 제공합니다.', NULL, '2025-07-25 10:32:15'),
	(334, 6, 4, '{"passwordComplexity": 1, "specialCharacters": 3, "upperCase": 2, "lowerCase": 2, "numbers": 2}', 1, '암호 복잡도가 특수문자 3개, 대소문자 각 2개, 숫자 2개 이상 포함하도록 최고 수준으로 강화되었습니다.', NULL, '2025-07-25 10:33:45'),
	(335, 6, 5, '{"maximumPasswordAge": "30"}', 1, '암호 변경 주기가 30일로 최대한 강화되어 최고 수준의 보안을 제공합니다.', NULL, '2025-07-25 10:34:20'),
	(336, 6, 6, '{"passwordHistorySize": "15"}', 1, '암호 이력 관리가 15개로 최대한 강화되어 과거 암호 재사용을 철저히 방지합니다.', NULL, '2025-07-25 10:35:30'),
	(337, 6, 7, '{"folders": ["IPC$"]}', 1, '불필요한 공유 폴더가 완전히 정리되어 최적의 보안 상태를 유지하고 있습니다.', NULL, '2025-07-25 10:36:45'),
	(338, 6, 8, '{"fDenyTSConnections": 1, "NetworkLevelAuthentication": "true", "AllowedUsers": "AdminOnly"}', 1, '원격 데스크톱이 네트워크 수준 인증과 관리자 전용 접속으로 최고 수준으로 제한되었습니다.', NULL, '2025-07-25 10:37:20'),
	(339, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "300", "screenSaverSecure": "1", "biometricLock": "true"}', 1, '생체인식 기능이 포함된 화면 보호기가 정상 작동하고 있습니다.', NULL, '2025-07-26 14:20:30'),
	(340, 6, 2, '{"DisplayName": "Bitdefender Total Security", "RealTimeProtection": 1, "UpToDate": 1, "ScanResults": "Clean"}', 1, 'Bitdefender Total Security가 시스템 전체 검사를 완료했으며 위협이 발견되지 않았습니다.', NULL, '2025-07-26 14:21:45'),
	(341, 6, 3, '{"minimumPasswordLength": "14"}', 1, '암호 길이가 최고 수준으로 설정되어 있습니다.', NULL, '2025-07-26 14:22:20'),
	(342, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 최고 수준으로 설정되어 있습니다.', NULL, '2025-07-26 14:23:10'),
	(343, 6, 5, '{"maximumPasswordAge": "30"}', 1, '암호 변경 주기가 최고 수준으로 설정되어 있습니다.', NULL, '2025-07-26 14:24:05'),
	(344, 6, 6, '{"passwordHistorySize": "15"}', 1, '암호 이력 관리가 최고 수준으로 설정되어 있습니다.', NULL, '2025-07-26 14:25:15'),
	(345, 6, 7, '{"folders": ["IPC$"]}', 1, '불필요한 공유 폴더가 없습니다.', NULL, '2025-07-26 14:26:30'),
	(346, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 최고 수준으로 제한되어 있습니다.', NULL, '2025-07-26 14:27:45'),
	(347, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "300", "screenSaverSecure": "1", "biometricLock": "true"}', 1, '화면 보호기가 최고 수준의 보안 설정으로 정상 작동하고 있습니다.', NULL, '2025-07-27 11:40:30'),
	(348, 6, 2, '{"DisplayName": "Bitdefender Total Security", "RealTimeProtection": 1, "UpToDate": 1}', 1, 'Bitdefender Total Security가 정상적으로 설치되어 있으며, 실시간 보호 및 최신 업데이트가 적용되어 있습니다.', NULL, '2025-07-27 11:41:45'),
	(349, 6, 3, '{"minimumPasswordLength": "14"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-07-27 11:42:20'),
	(350, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-27 11:43:10'),
	(351, 6, 5, '{"maximumPasswordAge": "30"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-27 11:44:05'),
	(352, 6, 6, '{"passwordHistorySize": "15"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-27 11:45:15'),
	(353, 6, 7, '{"folders": ["IPC$", "연구개발자료"]}', 0, '연구개발팀 전용 자료 공유 폴더가 발견되었으나 업무상 필요하여 제외 처리합니다.', '연구개발 업무용', '2025-07-27 11:46:30'),
	(354, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-27 11:47:45'),
	(355, 6, 1, '{"maintenance": "weekend_check"}', NULL, '주말 정기 점검으로 인해 화면 보호기 설정 확인이 지연되고 있습니다.', NULL, '2025-07-28 19:00:00'),
	(356, 6, 2, '{"DisplayName": "Bitdefender Total Security", "RealTimeProtection": 1, "UpToDate": 1, "WeekendScan": "InProgress"}', 1, 'Bitdefender Total Security가 주말 정기 전체 스캔을 진행 중이며 실시간 보호는 정상 작동하고 있습니다.', NULL, '2025-07-28 19:15:35'),
	(357, 6, 3, '{"validating": "weekend_policy_check"}', NULL, '주말 정기 정책 검증으로 인해 암호 설정 확인이 지연되고 있습니다.', NULL, '2025-07-28 19:30:20'),
	(358, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-28 19:45:10'),
	(359, 6, 5, '{"maximumPasswordAge": "30"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-28 20:00:05'),
	(360, 6, 6, '{"passwordHistorySize": "15"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-28 20:15:15'),
	(361, 6, 7, '{"folders": ["IPC$"]}', 1, '연구개발 자료 공유 폴더가 정리되었습니다.', NULL, '2025-07-28 20:30:30'),
	(362, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-28 20:45:45'),
	(363, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "300", "screenSaverSecure": "1", "biometricLock": "true"}', 1, '주말 점검 완료 후 화면 보호기가 정상 작동하고 있습니다.', NULL, '2025-07-29 08:50:30'),
	(364, 6, 2, '{"DisplayName": "Bitdefender Total Security", "RealTimeProtection": 1, "UpToDate": 1, "WeekendScanResult": "Clean", "ThreatsBlocked": 0}', 1, 'Bitdefender Total Security 주말 전체 스캔이 완료되었으며 위협이 발견되지 않았습니다.', NULL, '2025-07-29 08:51:45'),
	(365, 6, 3, '{"minimumPasswordLength": "14"}', 1, '주말 정책 검증이 완료되어 암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-07-29 08:52:20'),
	(366, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-29 08:53:10'),
	(367, 6, 5, '{"maximumPasswordAge": "30"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-29 08:54:05'),
	(368, 6, 6, '{"passwordHistorySize": "15"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-29 08:55:15'),
	(369, 6, 7, '{"folders": ["IPC$"]}', 1, '불필요한 공유 폴더가 없습니다.', NULL, '2025-07-29 08:56:30'),
	(370, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-29 08:57:45'),
	(371, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "300", "screenSaverSecure": "1", "biometricLock": "true"}', 1, '화면 보호기가 최고 수준의 보안 설정으로 정상 작동하고 있습니다.', NULL, '2025-07-30 12:35:30'),
	(372, 6, 2, '{"DisplayName": "Bitdefender Total Security", "RealTimeProtection": 1, "UpToDate": 1}', 1, 'Bitdefender Total Security가 정상적으로 설치되어 있으며, 실시간 보호 및 최신 업데이트가 적용되어 있습니다.', NULL, '2025-07-30 12:36:45'),
	(373, 6, 3, '{"minimumPasswordLength": "14"}', 1, '암호 길이가 정책에 맞게 설정되어 있습니다.', NULL, '2025-07-30 12:37:20'),
	(374, 6, 4, '{"passwordComplexity": 1}', 1, '암호 복잡도가 적절하게 설정되어 있습니다.', NULL, '2025-07-30 12:38:10'),
	(375, 6, 5, '{"maximumPasswordAge": "30"}', 1, '암호 변경 주기가 적절하게 설정되어 있습니다.', NULL, '2025-07-30 12:39:05'),
	(376, 6, 6, '{"passwordHistorySize": "15"}', 1, '동일 암호 사용 제한이 적절하게 설정되어 있습니다.', NULL, '2025-07-30 12:40:15'),
	(377, 6, 7, '{"folders": ["IPC$", "월말정산자료"]}', 0, '월말 정산 업무를 위한 임시 공유 폴더가 생성되었으나 업무상 필요하여 제외 처리합니다.', '월말정산 업무용', '2025-07-30 12:41:30'),
	(378, 6, 8, '{"fDenyTSConnections": 1}', 1, '원격 데스크톱이 적절하게 제한되어 있습니다.', NULL, '2025-07-30 12:42:45'),
	(379, 6, 1, '{"screenSaverEnabled": "1", "screenSaverTime": "300", "screenSaverSecure": "1", "biometricLock": "true", "monthlyReport": "Excellent"}', 1, '7월 한달간 화면 보호기가 최고 수준의 보안 설정으로 완벽하게 운영되었습니다.', NULL, '2025-07-31 17:45:30'),
	(380, 6, 2, '{"DisplayName": "Bitdefender Total Security", "RealTimeProtection": 1, "UpToDate": 1, "MonthlyStats": {"TotalScans": 31, "ThreatsBlocked": 15, "SystemHealth": "Excellent"}}', 1, 'Bitdefender Total Security가 7월 한달간 31회 스캔을 실행하고 15개의 위협을 차단하여 시스템을 완벽하게 보호했습니다.', NULL, '2025-07-31 17:46:45'),
	(381, 6, 3, '{"minimumPasswordLength": "14", "monthlyCompliance": "100%"}', 1, '7월 한달간 암호 길이 정책 준수율이 100%로 완벽하게 관리되었습니다.', NULL, '2025-07-31 17:47:20'),
	(382, 6, 4, '{"passwordComplexity": 1, "monthlyCompliance": "100%"}', 1, '7월 한달간 암호 복잡도 정책 준수율이 100%로 완벽하게 관리되었습니다.', NULL, '2025-07-31 17:48:10'),
	(383, 6, 5, '{"maximumPasswordAge": "30", "monthlyCompliance": "100%"}', 1, '7월 한달간 암호 변경 주기 정책 준수율이 100%로 완벽하게 관리되었습니다.', NULL, '2025-07-31 17:49:05'),
	(384, 6, 6, '{"passwordHistorySize": "15", "monthlyCompliance": "100%"}', 1, '7월 한달간 암호 이력 관리 정책 준수율이 100%로 완벽하게 관리되었습니다.', NULL, '2025-07-31 17:50:15'),
	(385, 6, 7, '{"folders": ["IPC$"], "monthlyReport": "CleanupCompleted"}', 1, '7월 한달간 불필요한 공유 폴더 정리가 완료되어 최적의 보안 상태를 유지했습니다.', NULL, '2025-07-31 17:51:30'),
	(386, 6, 8, '{"fDenyTSConnections": 1, "monthlyCompliance": "100%"}', 1, '7월 한달간 원격 데스크톱 제한 정책 준수율이 100%로 완벽하게 관리되었습니다.', NULL, '2025-07-31 17:52:45'),
	(419, 6, 1, '{"status": "pending", "message": "검사 대기 중"}', 1, 'pending 상태 자동 통과 처리', NULL, '2025-09-23 06:46:30'),
	(420, 6, 2, '{"status": "pending", "message": "검사 대기 중"}', 1, 'pending 상태 자동 통과 처리', NULL, '2025-09-23 06:46:30'),
	(421, 6, 3, '{"status": "pending", "message": "검사 대기 중"}', 1, 'pending 상태 자동 통과 처리', NULL, '2025-09-23 06:46:30'),
	(422, 6, 4, '{"status": "pending", "message": "검사 대기 중"}', 1, 'pending 상태 자동 통과 처리', NULL, '2025-09-23 06:46:30'),
	(423, 6, 5, '{"status": "pending", "message": "검사 대기 중"}', 1, 'pending 상태 자동 통과 처리', NULL, '2025-09-23 06:46:30'),
	(424, 6, 6, '{"status": "pending", "message": "검사 대기 중"}', 1, 'pending 상태 자동 통과 처리', NULL, '2025-09-23 06:46:30'),
	(425, 6, 7, '{"status": "pending", "message": "검사 대기 중"}', 1, 'pending 상태 자동 통과 처리', NULL, '2025-09-23 06:46:30'),
	(426, 6, 8, '{"status": "pending", "message": "검사 대기 중"}', 1, 'pending 상태 자동 통과 처리', NULL, '2025-09-23 06:46:30');

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

DELETE FROM `checklist_items`;
INSERT INTO `checklist_items` (`item_id`, `item_name`, `category`, `description`, `check_type`, `check_frequency`, `penalty_weight`, `created_at`, `updated_at`) VALUES
	(1, '화면보호기 사용', '접근통제', '화면보호기 설정 및 시간 확인', 'daily', 'daily', 0.5, '2025-06-03 03:44:38', '2025-06-03 03:44:38'),
	(2, '백신 상태 확인', '악성코드', '백신 설치 및 업데이트 상태 확인', 'daily', 'daily', 0.5, '2025-06-03 03:44:38', '2025-06-03 04:16:36'),
	(3, '패스워드 길이의 적정성', '접근통제', '최소 패스워드 길이 정책 확인', 'daily', 'daily', 0.5, '2025-06-03 03:44:38', '2025-06-03 04:16:43'),
	(4, '패스워드 복잡도 설정', '접근통제', '패스워드 복잡도 정책 확인', 'daily', 'daily', 0.5, '2025-06-03 03:44:38', '2025-06-03 04:16:47'),
	(5, '패스워드 주기적 변경', '접근통제', '패스워드 주기적 변경 정책 확인', 'daily', 'daily', 0.5, '2025-06-03 03:44:38', '2025-06-03 04:16:51'),
	(6, '동일 패스워드 설정 제한', '접근통제', '동일 패스워드 설정 정책 확인', 'daily', 'daily', 0.5, '2025-06-03 03:44:38', '2025-06-03 04:16:53'),
	(7, '공유폴더 확인', '접근통제', '공유폴더 설정 확인', 'daily', 'daily', 0.5, '2025-06-03 03:44:38', '2025-06-03 04:16:59'),
	(8, '원격데스크톱 제한', '접근통제', '원격 데스크톱 연결 제한 설정', 'daily', 'daily', 0.5, '2025-06-03 03:44:38', '2025-06-03 04:17:02');

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

DELETE FROM `department_exceptions`;

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

DELETE FROM `department_extended_exceptions`;

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

DELETE FROM `department_item_exceptions`;

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

DELETE FROM `manual_check_items`;
INSERT INTO `manual_check_items` (`item_id`, `item_code`, `item_name`, `item_category`, `description`, `penalty_weight`, `is_active`, `created_at`) VALUES
	(9, 'seal_check', 'PC 봉인씰 확인', '물리보안', 'PC 봉인씰 상태 점검', 0.5, 1, '2025-06-10 15:33:57'),
	(10, 'malware_scan', '악성코드 전체 검사', '악성코드', '전체 시스템 악성코드 검사', 0.5, 1, '2025-06-10 15:33:57'),
	(11, 'file_encryption', '개인정보 파일 암호화', '개인정보보호', '개인정보 파일 암호화 적용 여부', 0.5, 1, '2025-06-10 15:33:57');

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

DELETE FROM `manual_check_periods`;

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

DELETE FROM `manual_check_results`;

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
) ENGINE=InnoDB AUTO_INCREMENT=104 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='피싱 훈련 이력 (엑셀 업로드 매핑)';

DELETE FROM `phishing_training`;
INSERT INTO `phishing_training` (`training_id`, `user_id`, `period_id`, `training_year`, `email_sent_time`, `action_time`, `log_type`, `mail_type`, `target_email`, `training_result`, `response_time_minutes`, `notes`, `exclude_from_scoring`, `exclude_reason`, `created_at`, `updated_at`) VALUES
	(102, 6, 8, 2025, '2025-09-18 03:57:08', NULL, '자동 완료', '자동 통과', 'admin@test.com', 'success', NULL, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-09-18 03:57:08', '2025-09-18 03:57:08'),
	(103, 7, 8, 2025, '2025-09-18 03:57:08', NULL, '자동 완료', '자동 통과', 'dududu@nice.com', 'success', NULL, '기간 완료로 인한 자동 통과 처리', 0, NULL, '2025-09-18 03:57:08', '2025-09-18 03:57:08');

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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='피싱 훈련 기간 설정';

DELETE FROM `phishing_training_periods`;
INSERT INTO `phishing_training_periods` (`period_id`, `training_year`, `period_name`, `training_type`, `start_date`, `end_date`, `is_completed`, `completed_at`, `completed_by`, `description`, `auto_pass_setting`, `created_by`, `created_at`, `updated_at`) VALUES
	(8, 2025, '11c', '이메일 피싱', '2025-09-02', '2025-09-08', 1, '2025-09-18 03:57:08', 'admin', '', 1, 'admin', '2025-09-15 03:53:42', '2025-09-18 03:57:08');

DROP VIEW IF EXISTS `phishing_training_stats`;
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
);

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
) ENGINE=InnoDB AUTO_INCREMENT=564 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='정보보호 교육 이력 (CSV 매핑 개선 버전)';

DELETE FROM `security_education`;
INSERT INTO `security_education` (`education_id`, `user_id`, `education_year`, `course_name`, `completed_count`, `incomplete_count`, `education_type`, `education_date`, `notes`, `period_id`, `exclude_from_scoring`, `exclude_reason`, `created_at`, `updated_at`) VALUES
	(563, 6, 2025, '2025년 오프라인 교육', 2, 2, '오프라인', NULL, 'CSV 업로드 - admin', 31, 0, '', '2025-09-18 03:58:16', '2025-10-15 08:04:02');

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
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='정보보호 교육 기간 설정';

DELETE FROM `security_education_periods`;
INSERT INTO `security_education_periods` (`period_id`, `education_year`, `period_name`, `education_type`, `start_date`, `end_date`, `is_completed`, `completed_at`, `completed_by`, `description`, `auto_pass_setting`, `created_by`, `created_at`, `updated_at`) VALUES
	(29, 2025, '2025년 온라인 교육', '온라인', '2025-01-01', '2025-10-30', 1, '2025-10-15 08:04:30', 'admin', '', 0, 'admin', '2025-08-13 03:37:00', '2025-10-15 08:04:30'),
	(31, 2025, '2025년 오프라인 교육', '오프라인', '2025-03-20', '2025-10-20', 1, '2025-10-15 08:04:19', 'admin', '', 0, 'admin', '2025-09-12 08:07:09', '2025-10-15 08:04:19');

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
) ENGINE=InnoDB AUTO_INCREMENT=203 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='KPI 보안 점수 요약 (교육 기간별 감점 기준)';

DELETE FROM `security_score_summary`;
INSERT INTO `security_score_summary` (`summary_id`, `user_id`, `evaluation_year`, `audit_penalty`, `education_penalty`, `training_penalty`, `total_penalty`, `audit_failed_count`, `education_incomplete_count`, `training_failed_count`, `last_calculated`, `created_at`) VALUES
	(201, 6, 2025, 4.00, 0.50, 0.00, 4.50, 24, 1, 0, '2025-10-15 07:11:22', '2025-09-15 03:52:32'),
	(202, 7, 2025, 0.00, 0.00, 0.00, 0.00, 0, 0, 0, '2025-09-15 03:52:32', '2025-09-15 03:52:32');

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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 정보';

DELETE FROM `users`;
INSERT INTO `users` (`uid`, `user_id`, `username`, `mail`, `department`, `created_at`, `updated_at`, `last_updated`, `ip`, `mac`, `role`) VALUES
	(6, 'admin', '관리자', 'admin@test.com', 'ADMIN', '2025-08-13 00:41:10', '2025-08-13 00:41:10', '2025-08-13 00:41:10', '127.0.0.1', NULL, 'admin'),
	(7, 'dududu', '김은제', 'dududu@nice.com', '운영실', '2025-08-21 05:26:12', '2025-08-21 05:26:12', '2025-08-21 05:26:12', '10.106.15.129', NULL, 'user');

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

DELETE FROM `user_exceptions`;

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

DELETE FROM `user_extended_exceptions`;

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

DELETE FROM `user_item_exceptions`;

DROP VIEW IF EXISTS `user_phishing_summary`;
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
);

DROP TABLE IF EXISTS `phishing_training_stats`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `phishing_training_stats` AS select `pt`.`training_year` AS `training_year`,`pt`.`period_id` AS `period_id`,`ptp`.`period_name` AS `period_name`,`ptp`.`training_type` AS `training_type`,count(0) AS `total_targets`,count(case when `pt`.`training_result` = 'success' then 1 end) AS `success_count`,count(case when `pt`.`training_result` = 'fail' then 1 end) AS `fail_count`,count(case when `pt`.`training_result` = 'no_response' then 1 end) AS `no_response_count`,round(count(case when `pt`.`training_result` = 'success' then 1 end) / count(0) * 100,2) AS `success_rate`,round(count(case when `pt`.`training_result` = 'fail' then 1 end) / count(0) * 100,2) AS `fail_rate` from (`phishing_training` `pt` join `phishing_training_periods` `ptp` on(`pt`.`period_id` = `ptp`.`period_id`)) where `pt`.`exclude_from_scoring` = 0 group by `pt`.`training_year`,`pt`.`period_id`,`ptp`.`period_name`,`ptp`.`training_type` 
;

DROP TABLE IF EXISTS `user_phishing_summary`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `user_phishing_summary` AS select `u`.`uid` AS `user_id`,`u`.`user_id` AS `username`,`u`.`department` AS `department`,`u`.`mail` AS `email`,`pt`.`training_year` AS `training_year`,count(0) AS `total_trainings`,count(case when `pt`.`training_result` = 'success' then 1 end) AS `success_count`,count(case when `pt`.`training_result` = 'fail' then 1 end) AS `fail_count`,count(case when `pt`.`training_result` = 'no_response' then 1 end) AS `no_response_count`,round(count(case when `pt`.`training_result` = 'success' then 1 end) / count(0) * 100,2) AS `success_rate`,count(case when `pt`.`training_result` = 'fail' then 1 end) * 0.5 AS `penalty_score` from (`users` `u` left join `phishing_training` `pt` on(`u`.`uid` = `pt`.`user_id` and `pt`.`exclude_from_scoring` = 0)) group by `u`.`uid`,`u`.`user_id`,`u`.`department`,`u`.`mail`,`pt`.`training_year` 
;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
