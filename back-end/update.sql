-- 1. checklist_items 테이블에 새로운 컬럼 추가
ALTER TABLE checklist_items ADD COLUMN check_type ENUM('daily', 'manual') DEFAULT 'daily' COMMENT '점검 유형 (정기/수시)';
ALTER TABLE checklist_items ADD COLUMN check_frequency VARCHAR(100) DEFAULT '매일' COMMENT '점검 주기';

-- 2. 기존 8개 항목을 정기 점검으로 설정
UPDATE checklist_items SET check_type = 'daily', check_frequency = '매일' WHERE item_id <= 8;

-- 3. 새로운 수시 점검 항목 추가
INSERT INTO checklist_items (category, item_name, description, check_type, check_frequency) VALUES
('물리적 보안', 'PC 봉인씰 상태 확인', 'PC 케이스의 봉인씰 훼손 여부를 육안으로 확인', 'manual', '수시'),
('악성코드 점검', '악성코드 탐지 이력 확인', '시스템에서 발견된 악성코드 탐지 이력 및 처리 현황 확인', 'manual', '수시'),
('정보보호', '개인정보 암호화 상태 확인', '개인정보가 포함된 파일의 암호화 적용 여부 확인', 'manual', '수시');

-- 4. audit_log 테이블에 점검 유형 구분을 위한 인덱스 추가 (선택사항)
-- ALTER TABLE audit_log ADD INDEX idx_item_type (item_id, checked_at);

-- 5. 추가된 항목 확인
SELECT 
    item_id,
    category,
    item_name,
    check_type,
    check_frequency,
    description
FROM checklist_items 
ORDER BY check_type, item_id;