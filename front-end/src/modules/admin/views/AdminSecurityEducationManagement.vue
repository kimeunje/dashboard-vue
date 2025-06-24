<template>
  <div class="admin-training">
    <div class="admin-header">
      <h1>정보보호 교육 관리</h1>
      <div class="admin-nav">
        <RouterLink to="/admin/training" class="nav-item">모의훈련 관리</RouterLink>
        <RouterLink to="/admin/education" class="nav-item active">교육 관리</RouterLink>
        <RouterLink to="/admin/manual-check" class="nav-item">수시 점검 관리</RouterLink>
        <RouterLink to="/admin/exceptions" class="nav-item">제외 설정</RouterLink>
      </div>
    </div>

    <div class="management-content">
      <!-- 필터 및 검색 -->
      <div class="filter-section">
        <div class="filter-group">
          <label>연도:</label>
          <select v-model="selectedYear" @change="loadEducationData">
            <option v-for="year in availableYears" :key="year" :value="year">{{ year }}년</option>
          </select>
        </div>

        <div class="filter-group">
          <label>교육유형:</label>
          <select v-model="selectedEducationType" @change="loadEducationData">
            <option value="">전체</option>
            <option value="오프라인">오프라인</option>
            <option value="온라인">온라인</option>
            <option value="신입교육">신입교육</option>
            <option value="심화교육">심화교육</option>
          </select>
        </div>

        <div class="filter-group">
          <label>상태:</label>
          <select v-model="selectedStatus" @change="loadEducationData">
            <option value="">전체</option>
            <option value="1">수료</option>
            <option value="0">미수료</option>
          </select>
        </div>

        <div class="search-group">
          <input
            type="text"
            v-model="searchQuery"
            @input="searchEducationData"
            placeholder="사용자명 또는 부서 검색..."
            class="search-input"
          />
        </div>
      </div>

      <!-- 교육 기간 관리 섹션 -->
      <div class="period-management-section">
        <div class="section-header">
          <h3>🗓️ 교육 기간 관리</h3>
          <button @click="openPeriodModal" class="primary-button">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"
              />
            </svg>
            기간 추가
          </button>
        </div>

        <!-- 교육 기간 카드들 -->
        <div
          class="period-cards"
          v-if="
            periodStatus.education_types && Object.keys(periodStatus.education_types).length > 0
          "
        >
          <!-- 교육 유형별로 그룹화해서 표시 -->
          <div
            v-for="(typeData, educationType) in periodStatus.education_types"
            :key="educationType"
            class="education-type-group"
          >
            <h4 class="type-header">{{ educationType }} 교육</h4>
            <div class="type-periods">
              <div
                v-for="period in typeData.periods"
                :key="period.period_id"
                class="period-card"
                :class="[`status-${period.status}`, { completed: period.is_completed }]"
              >
                <div class="card-header">
                  <h5>{{ period.period_name }}</h5>
                  <div class="period-type">{{ period.education_type }}</div>
                  <div class="status-badge" :class="period.status">
                    {{ getStatusText(period.status, period.is_completed) }}
                  </div>
                </div>
                <div class="card-body">
                  <div class="period-info">
                    <span class="info-item">
                      📅 {{ formatDate(period.start_date) }} ~ {{ formatDate(period.end_date) }}
                    </span>
                    <span class="info-item" v-if="period.completed_participants !== undefined">
                      👥 {{ period.completed_participants || 0 }}명 수료
                    </span>
                  </div>
                  <div class="card-actions">
                    <button @click="editPeriod(period)" class="edit-button" title="수정">✏️</button>
                    <button
                      v-if="!period.is_completed"
                      @click="completePeriod(period)"
                      class="complete-button"
                      title="완료 처리"
                    >
                      ✅
                    </button>
                    <button v-else @click="reopenPeriod(period)" class="reopen-button" title="재개">
                      🔄
                    </button>
                    <button @click="deletePeriod(period)" class="delete-button" title="삭제">
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 기간이 없을 때 -->
        <div v-else class="no-periods">
          <p>등록된 교육 기간이 없습니다.</p>
          <p class="text-muted">위의 "기간 추가" 버튼을 클릭하여 새로운 교육 기간을 등록하세요.</p>
        </div>
      </div>

      <!-- 액션 버튼 -->
      <div class="action-section">
        <button @click="showBulkUploadModal = true" class="primary-button">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path
              d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
            />
            <path
              d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"
            />
          </svg>
          일괄 등록
        </button>

        <button @click="exportEducationData" class="secondary-button">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path
              d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
            />
            <path
              d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"
            />
          </svg>
          내보내기
        </button>

        <button @click="downloadTemplate" class="outline-button">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path
              d="M14 14V4.5L9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2zM9.5 3A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h5.5v2z"
            />
          </svg>
          템플릿 다운로드
        </button>

        <RouterLink to="/admin/exceptions" class="outline-button">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path
              d="M2.5 1a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1H3v9a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V4h.5a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H10a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1H2.5zm3 4a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5zM8 5a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7A.5.5 0 0 1 8 5zm3 .5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 1 0z"
            />
          </svg>
          제외 설정
        </RouterLink>
      </div>

      <!-- 교육 기록 테이블 -->
      <div class="table-section">
        <div class="table-header">
          <h3>교육 기록 ({{ filteredRecords.length }}건)</h3>
          <div class="bulk-actions">
            <label class="select-all">
              <input
                type="checkbox"
                v-model="selectAll"
                @change="toggleSelectAll"
                :indeterminate="
                  selectedRecords.length > 0 && selectedRecords.length < paginatedRecords.length
                "
              />
              전체 선택
            </label>
            <button
              @click="bulkToggleException"
              :disabled="selectedRecords.length === 0"
              class="bulk-action-button"
            >
              선택 항목 제외/포함 토글
            </button>
          </div>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th style="width: 40px">
                  <input
                    type="checkbox"
                    v-model="selectAll"
                    @change="toggleSelectAll"
                    :indeterminate="
                      selectedRecords.length > 0 && selectedRecords.length < paginatedRecords.length
                    "
                  />
                </th>
                <th>사용자</th>
                <th>부서</th>
                <!-- ✅ 새로운 컬럼: 과정명 (기존 교육유형 대체) -->
                <th>과정명</th>
                <th>교육유형</th>
                <!-- ✅ 새로운 컬럼들 -->
                <th>수료횟수</th>
                <th>미수료횟수</th>
                <th>수료율</th>
                <!-- 기존 컬럼들 -->
                <th>상태</th>
                <th>교육일</th>
                <th>기간</th>
                <th>감점</th>
                <th>제외</th>
                <th>작업</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="record in paginatedRecords"
                :key="record.education_id"
                :class="{
                  selected: selectedRecords.includes(record),
                  excluded: record.exclude_from_scoring,
                  'data-legacy': record.data_mode === 'legacy',
                }"
              >
                <!-- 체크박스 -->
                <td class="checkbox-col">
                  <input
                    type="checkbox"
                    :value="record"
                    v-model="selectedRecords"
                    @change="updateSelectAll"
                  />
                </td>

                <!-- 사용자 정보 -->
                <td class="user-info">
                  <div class="user-name">{{ record.username }}</div>
                  <div class="user-id">{{ record.user_id }}</div>
                </td>

                <!-- 부서 -->
                <td class="department">{{ record.department }}</td>

                <!-- ✅ 과정명 (새로운 정보 우선 표시) -->
                <td class="course-name">
                  <div class="course-main">{{ record.course_name || record.education_type }}</div>
                  <!-- ✅ 새로운 스키마인 경우 총 과정 수 표시 -->
                  <div v-if="record.total_courses > 1" class="course-meta">
                    총 {{ record.total_courses }}과정
                  </div>
                </td>

                <!-- 교육유형 -->
                <td class="education-type">
                  <span class="type-badge" :class="getTypeClass(record.education_type)">
                    {{ record.education_type }}
                  </span>
                </td>

                <!-- ✅ 수료횟수 -->
                <td class="completed-count">
                  <span class="count-value success">{{ record.completed_count || 0 }}</span>
                </td>

                <!-- ✅ 미수료횟수 -->
                <td class="incomplete-count">
                  <span class="count-value danger">{{ record.incomplete_count || 0 }}</span>
                </td>

                <!-- ✅ 수료율 -->
                <td class="completion-rate">
                  <div class="rate-container">
                    <div class="rate-bar">
                      <div
                        class="rate-fill"
                        :style="{ width: `${record.completion_rate || 0}%` }"
                        :class="getRateClass(record.completion_rate)"
                      ></div>
                    </div>
                    <span class="rate-text" :class="getRateTextClass(record.completion_rate)">
                      {{ (record.completion_rate || 0).toFixed(0) }}%
                    </span>
                  </div>
                </td>

                <!-- 상태 (향상된 표시) -->
                <td class="status">
                  <span class="status-badge" :class="getStatusClass(record)">
                    {{ record.status_text || getStatusText(record) }}
                  </span>
                  <!-- ✅ 레거시 데이터 표시 -->
                  <div v-if="record.data_mode === 'legacy'" class="legacy-indicator">레거시</div>
                </td>

                <!-- 교육일 -->
                <td class="education-date">
                  {{ formatDate(record.education_date) }}
                </td>

                <!-- ✅ 기간 정보 (향상된 표시) -->
                <td class="period-info">
                  <div v-if="record.period_name" class="period-name">
                    {{ record.period_name }}
                  </div>
                  <div
                    v-if="record.period_start_date && record.period_end_date"
                    class="period-dates"
                  >
                    {{ formatDateShort(record.period_start_date) }} ~
                    {{ formatDateShort(record.period_end_date) }}
                  </div>
                  <div v-if="record.period_completed" class="period-status completed">완료됨</div>
                </td>

                <!-- ✅ 감점 (정확한 계산) -->
                <td class="penalty">
                  <span v-if="record.exclude_from_scoring" class="penalty-excluded"> 제외 </span>
                  <span
                    v-else
                    class="penalty-value"
                    :class="{ 'penalty-active': record.penalty_applied > 0 }"
                  >
                    -{{ (record.penalty_applied || 0).toFixed(1) }}점
                  </span>
                </td>

                <!-- 제외 상태 -->
                <td class="exclude-status">
                  <button
                    @click="toggleExceptionStatus(record)"
                    class="exclude-toggle"
                    :class="{ active: record.exclude_from_scoring }"
                    :title="record.exclude_from_scoring ? '제외 해제' : '점수 제외'"
                  >
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                      <path
                        v-if="record.exclude_from_scoring"
                        d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"
                      />
                      <path
                        v-else
                        d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.061L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"
                      />
                    </svg>
                  </button>

                  <!-- ✅ 제외 사유 표시 -->
                  <div
                    v-if="record.exclude_from_scoring && record.exclude_reason"
                    class="exclude-reason"
                  >
                    {{ record.exclude_reason }}
                  </div>
                </td>

                <!-- 작업 버튼 -->
                <td class="actions">
                  <div class="action-buttons">
                    <button @click="editRecord(record)" class="action-btn edit" title="수정">
                      <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                        <path
                          d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"
                        />
                        <path
                          fill-rule="evenodd"
                          d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z"
                        />
                      </svg>
                    </button>

                    <button @click="deleteRecord(record)" class="action-btn delete" title="삭제">
                      <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                        <path
                          d="M2.5 1a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1H3v9a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V4h.5a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H10a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1H2.5zm3 4a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5zM8 5a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7A.5.5 0 0 1 8 5zm3 .5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 1 0z"
                        />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- 페이지네이션 -->
          <div class="pagination">
            <button @click="currentPage--" :disabled="currentPage <= 1" class="pagination-button">
              이전
            </button>

            <span class="pagination-info">
              {{ currentPage }} / {{ totalPages }} 페이지 (총 {{ filteredRecords.length }}건)
            </span>

            <button
              @click="currentPage++"
              :disabled="currentPage >= totalPages"
              class="pagination-button"
            >
              다음
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 기간 설정 모달 -->
    <div v-if="showPeriodModal" class="modal-overlay" @click="closePeriodModal">
      <div class="modal-content period-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ editingPeriod ? '기간 수정' : '기간 추가' }}</h3>
          <button @click="closePeriodModal" class="close-button">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>연도:</label>
            <input
              type="number"
              v-model="periodForm.education_year"
              :min="2020"
              :max="2030"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>기간명:</label>
            <input
              type="text"
              v-model="periodForm.period_name"
              placeholder="예: 1차 오프라인 교육, 신입사원 교육"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>교육유형:</label>
            <select v-model="periodForm.education_type" class="form-input">
              <option value="오프라인">오프라인</option>
              <option value="온라인">온라인</option>
              <option value="신입교육">신입교육</option>
              <option value="심화교육">심화교육</option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>시작일:</label>
              <input type="date" v-model="periodForm.start_date" class="form-input" />
            </div>
            <div class="form-group">
              <label>종료일:</label>
              <input type="date" v-model="periodForm.end_date" class="form-input" />
            </div>
          </div>
          <div class="form-group">
            <label>설명:</label>
            <textarea
              v-model="periodForm.description"
              rows="3"
              placeholder="교육에 대한 설명을 입력하세요"
              class="form-input"
            ></textarea>
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="periodForm.auto_pass_setting" />
              완료 시 자동 통과 처리
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closePeriodModal" class="cancel-button">취소</button>
          <button @click="savePeriod" class="save-button" :disabled="!isValidPeriodForm">
            {{ editingPeriod ? '수정' : '추가' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 기존 일괄 업로드 모달 수정 -->
    <div v-if="showBulkUploadModal" class="modal-overlay" @click="closeBulkUploadModal">
      <div class="modal-content bulk-upload-modal" @click.stop>
        <div class="modal-header">
          <h3>교육 결과 일괄 업로드</h3>
          <button @click="closeBulkUploadModal" class="close-button">&times;</button>
        </div>

        <div class="modal-body">
          <!-- ✅ 개선: 교육 기간 선택 필수 안내 -->
          <div class="upload-step">
            <h4>1단계: 교육 기간 선택 (필수)</h4>
            <div class="period-selection">
              <select v-model="selectedUploadPeriod" @change="onPeriodChange" class="period-select">
                <option value="">교육 기간을 선택하세요</option>
                <optgroup
                  v-for="(typeData, eduType) in availablePeriodsForUpload"
                  :key="eduType"
                  :label="`${eduType} 교육`"
                >
                  <option
                    v-for="period in typeData.periods"
                    :key="period.period_id"
                    :value="period.period_id"
                  >
                    {{ period.period_name }} ({{
                      formatDateRange(period.start_date, period.end_date)
                    }}) - {{ getPeriodStatusText(period) }}
                  </option>
                </optgroup>
              </select>
            </div>

            <!-- ✅ 새로운 기능: 선택된 기간 정보 표시 -->
            <div v-if="selectedPeriodInfo" class="selected-period-info">
              <div class="info-card">
                <h5>선택된 교육 기간</h5>
                <p><strong>기간명:</strong> {{ selectedPeriodInfo.period_name }}</p>
                <p><strong>교육유형:</strong> {{ selectedPeriodInfo.education_type }}</p>
                <p>
                  <strong>기간:</strong>
                  {{ formatDateRange(selectedPeriodInfo.start_date, selectedPeriodInfo.end_date) }}
                </p>
                <p>
                  <strong>상태:</strong>
                  <span :class="getPeriodStatusClass(selectedPeriodInfo)">
                    {{ getPeriodStatusText(selectedPeriodInfo) }}
                  </span>
                </p>
              </div>
            </div>
          </div>

          <!-- ✅ 수정: 파일 업로드 섹션 - 기간 선택 후에만 활성화 -->
          <div class="upload-step" :class="{ disabled: !selectedUploadPeriod }">
            <h4>2단계: CSV/Excel 파일 업로드</h4>

            <!-- 기간 미선택 시 안내 메시지 -->
            <div v-if="!selectedUploadPeriod" class="warning-message">
              <p>⚠️ 먼저 교육 기간을 선택해주세요.</p>
            </div>

            <div v-else class="file-upload-area">
              <div
                class="dropzone"
                :class="{ active: isDragOver }"
                @dragover.prevent="isDragOver = true"
                @dragleave="isDragOver = false"
                @drop.prevent="handleFileDrop"
                @click="triggerFileSelect"
              >
                <div v-if="!selectedFile" class="upload-placeholder">
                  <div class="upload-icon">📁</div>
                  <p>CSV 또는 Excel 파일을 드래그하거나 클릭하여 선택하세요</p>
                  <small>지원 형식: .csv, .xlsx, .xls</small>
                </div>

                <div v-else class="file-info">
                  <div class="file-icon">📄</div>
                  <div class="file-details">
                    <p>
                      <strong>{{ selectedFile.name }}</strong>
                    </p>
                    <small>{{ formatFileSize(selectedFile.size) }}</small>
                  </div>
                  <button @click.stop="removeSelectedFile" class="remove-file-btn">✕</button>
                </div>
              </div>

              <input
                ref="fileInput"
                type="file"
                accept=".csv,.xlsx,.xls"
                @change="handleFileSelect"
                style="display: none"
              />

              <!-- ✅ 개선: 템플릿 다운로드 링크를 더 눈에 띄게 -->
              <div class="template-section">
                <button @click="downloadTemplate" class="template-btn">
                  📥 업로드 템플릿 다운로드
                </button>
                <small>템플릿을 다운로드하여 올바른 형식으로 데이터를 준비하세요</small>
              </div>
            </div>
          </div>

          <!-- ✅ 개선: 파일 미리보기 - 백엔드 검증 결과 반영 -->
          <div v-if="uploadPreview.length > 0" class="upload-step">
            <h4>3단계: 데이터 미리보기 및 검증</h4>

            <!-- 검증 결과 요약 -->
            <div class="validation-summary">
              <div class="summary-stats">
                <div class="stat-item">
                  <span class="stat-label">총 레코드:</span>
                  <span class="stat-value">{{ uploadPreview.length }}건</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">예상 수료:</span>
                  <span class="stat-value success">{{ getTotalCompletedCount() }}건</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">예상 미수료:</span>
                  <span class="stat-value warning">{{ getTotalIncompleteCount() }}건</span>
                </div>
              </div>
            </div>

            <!-- ✅ 새로운 기능: 데이터 검증 경고 -->
            <div v-if="validationWarnings.length > 0" class="validation-warnings">
              <h5>⚠️ 검증 경고사항</h5>
              <ul>
                <li v-for="warning in validationWarnings" :key="warning">{{ warning }}</li>
              </ul>
            </div>

            <!-- 데이터 테이블 미리보기 -->
            <div class="preview-table-container">
              <table class="preview-table">
                <thead>
                  <tr>
                    <!-- ✅ 새로운 컬럼 구조로 변경 -->
                    <th>이름</th>
                    <th>부서</th>
                    <th>수강과정</th>
                    <th>수료횟수</th>
                    <th>미수료횟수</th>
                    <th>전체</th>
                    <th>수료율</th>
                    <th>상태</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(record, index) in uploadPreview.slice(0, 10)" :key="index">
                    <td>{{ record.username }}</td>
                    <td>{{ record.department }}</td>
                    <td>{{ record.education_type }}</td>
                    <!-- ✅ 새로운 필드들 표시 -->
                    <td class="number-cell">{{ record.completed_count }}</td>
                    <td class="number-cell">{{ record.incomplete_count }}</td>
                    <td class="number-cell">
                      {{ record.completed_count + record.incomplete_count }}
                    </td>
                    <td class="percentage-cell">
                      {{
                        record.completed_count + record.incomplete_count > 0
                          ? Math.round(
                              (record.completed_count /
                                (record.completed_count + record.incomplete_count)) *
                                100,
                            )
                          : 0
                      }}%
                    </td>
                    <td>
                      <!-- ✅ 수료율에 따른 상태 표시 -->
                      <span
                        :class="{
                          'status-excellent':
                            record.completed_count + record.incomplete_count > 0 &&
                            record.completed_count /
                              (record.completed_count + record.incomplete_count) >=
                              0.8,
                          'status-good':
                            record.completed_count + record.incomplete_count > 0 &&
                            record.completed_count /
                              (record.completed_count + record.incomplete_count) >=
                              0.6 &&
                            record.completed_count /
                              (record.completed_count + record.incomplete_count) <
                              0.8,
                          'status-poor':
                            record.completed_count + record.incomplete_count > 0 &&
                            record.completed_count /
                              (record.completed_count + record.incomplete_count) <
                              0.6,
                          'status-none': record.completed_count + record.incomplete_count === 0,
                        }"
                      >
                        {{
                          record.completed_count + record.incomplete_count === 0
                            ? '데이터없음'
                            : record.completed_count /
                                  (record.completed_count + record.incomplete_count) >=
                                0.8
                              ? '우수'
                              : record.completed_count /
                                    (record.completed_count + record.incomplete_count) >=
                                  0.6
                                ? '양호'
                                : '미흡'
                        }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>

              <!-- 데이터가 없는 경우 -->
              <div v-if="filteredRecords.length === 0" class="no-data">
                <div class="no-data-icon">📚</div>
                <h3>교육 기록이 없습니다</h3>
                <p>필터 조건을 변경하거나 새로운 교육 데이터를 업로드해보세요.</p>
              </div>

              <!-- 더 많은 데이터가 있는 경우 안내 (기존 유지) -->
              <p v-if="uploadPreview.length > 10" class="preview-note">
                총 {{ uploadPreview.length }}건 중 10건만 미리보기로 표시됩니다.
              </p>
            </div>
          </div>
        </div>

        <!-- ✅ 수정: 업로드 버튼 - 더 명확한 검증 메시지 -->
        <div class="modal-footer">
          <button @click="closeBulkUploadModal" class="cancel-button">취소</button>
          <button
            @click="executeUpload"
            :disabled="!canUpload"
            class="upload-button"
            :class="{ loading: uploading }"
          >
            <span v-if="uploading" class="loading-spinner"></span>
            <span v-if="uploading"> {{ selectedPeriodInfo?.period_name }}에 업로드 중... </span>
            <span v-else-if="!selectedUploadPeriod"> 교육 기간을 선택하세요 </span>
            <span v-else-if="uploadPreview.length === 0"> 파일을 선택하세요 </span>
            <span v-else>
              {{ selectedPeriodInfo?.period_name }}에 {{ uploadPreview.length }}건 업로드
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- 토스트 메시지 -->
    <div v-if="showToast" class="toast" :class="toastType">
      {{ toastMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { RouterLink } from 'vue-router'

// 반응형 데이터
const loading = ref(false)
const selectedYear = ref(new Date().getFullYear())
const selectedEducationType = ref('')
const selectedStatus = ref('')
const searchQuery = ref('')

// 교육 기간 관리
const periodStatus = ref({ periods: [] })
const showPeriodModal = ref(false)
const editingPeriod = ref(null)
const periodForm = ref({
  education_year: new Date().getFullYear(),
  period_name: '',
  education_type: '오프라인',
  start_date: '',
  end_date: '',
  description: '',
  auto_pass_setting: true,
})

// 교육 데이터
const educationData = ref([])
const filteredRecords = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const selectedRecords = ref([])
const selectAll = ref(false)

// 업로드 관련
const showBulkUploadModal = ref(false)
const selectedFile = ref(null)
const uploadPreview = ref([])
const uploading = ref(false)
const isDragging = ref(false)

// ✅ 새로 추가된 변수들
const selectedUploadPeriod = ref('') // 선택된 교육 기간 ID
const availablePeriodsForUpload = ref({}) // 업로드 가능한 교육 기간들

// ✅ 새로운 상태: 데이터 검증 관련
const validationWarnings = ref([])

// 편집 관련
const showEditModal = ref(false)
const editingRecord = ref({})

// 토스트
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

// 계산된 속성
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return [currentYear - 1, currentYear, currentYear + 1]
})

const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRecords.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredRecords.value.length / pageSize.value)
})

const isValidPeriodForm = computed(() => {
  return (
    periodForm.value.period_name &&
    periodForm.value.education_type &&
    periodForm.value.start_date &&
    periodForm.value.end_date
  )
})

// 라이프사이클
onMounted(() => {
  loadPeriodStatus()
  loadEducationData()
  loadAvailablePeriodsForUpload()
})

// 메서드들
const loadPeriodStatus = async () => {
  try {
    console.log('[DEBUG] 기간 현황 조회 시작:', selectedYear.value)

    const response = await fetch(
      `/api/security-education/periods/status?year=${selectedYear.value}`,
      {
        credentials: 'include',
      },
    )

    if (!response.ok) {
      throw new Error('기간 현황 조회 실패')
    }

    const data = await response.json()
    console.log('[DEBUG] 서버 응답 데이터:', data)

    periodStatus.value = data

    // 기간 개수 로그
    if (data.education_types) {
      let totalPeriods = 0
      Object.values(data.education_types).forEach((typeData) => {
        totalPeriods += typeData.periods ? typeData.periods.length : 0
      })
      console.log('[DEBUG] 총 기간 개수:', totalPeriods)
    }
  } catch (err) {
    console.error('기간 현황 조회 오류:', err)
    displayToast('기간 현황을 불러오는데 실패했습니다.', 'error')
  }
}

const loadEducationData = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      year: selectedYear.value,
      education_type: selectedEducationType.value,
      status: selectedStatus.value,
    })

    const response = await fetch(`/api/security-education/records?${params}`, {
      credentials: 'include',
    })

    if (!response.ok) {
      throw new Error('교육 데이터 조회 실패')
    }

    educationData.value = await response.json()
    applyFilters()
  } catch (err) {
    console.error('교육 데이터 조회 오류:', err)
    displayToast('교육 데이터를 불러오는데 실패했습니다.', 'error')
  } finally {
    loading.value = false
  }
}

const searchEducationData = () => {
  applyFilters()
}

// ✅ 필터링 로직 개선 (기존 applyFilters 함수 수정)
const applyFilters = () => {
  let filtered = [...educationData.value]

  // 검색어 필터
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter((record) => {
      return (
        record.username?.toLowerCase().includes(query) ||
        record.department?.toLowerCase().includes(query) ||
        record.course_name?.toLowerCase().includes(query) || // ✅ 과정명 검색 추가
        record.education_type?.toLowerCase().includes(query)
      )
    })
  }

  filteredRecords.value = filtered
  currentPage.value = 1
}

// 기간 관리 메서드
const openPeriodModal = () => {
  editingPeriod.value = null
  periodForm.value = {
    education_year: selectedYear.value,
    period_name: '',
    education_type: '오프라인',
    start_date: '',
    end_date: '',
    description: '',
    auto_pass_setting: true,
  }
  showPeriodModal.value = true
}

const editPeriod = (period) => {
  editingPeriod.value = period
  periodForm.value = {
    education_year: period.education_year,
    period_name: period.period_name,
    education_type: period.education_type,
    start_date: period.start_date,
    end_date: period.end_date,
    description: period.description || '',
    auto_pass_setting: period.auto_pass_setting !== undefined ? period.auto_pass_setting : true,
  }
  showPeriodModal.value = true
}
const savePeriod = async () => {
  if (!isValidPeriodForm.value) {
    displayToast('필수 필드를 모두 입력해주세요.', 'error')
    return
  }

  // 날짜 유효성 검사
  if (new Date(periodForm.value.start_date) >= new Date(periodForm.value.end_date)) {
    displayToast('종료일은 시작일보다 늦어야 합니다.', 'error')
    return
  }

  try {
    console.log('[DEBUG] 기간 저장 요청:', periodForm.value)

    const method = editingPeriod.value ? 'PUT' : 'POST'
    const url = editingPeriod.value
      ? `/api/security-education/periods/${editingPeriod.value.period_id}`
      : '/api/security-education/periods'

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(periodForm.value),
    })

    const result = await response.json()
    console.log('[DEBUG] 서버 응답:', result)

    if (!response.ok) {
      // 더 구체적인 에러 메시지 표시
      let errorMessage = result.error || '기간 저장 실패'

      // 겹치는 기간이 있는 경우 상세 정보 표시
      if (result.overlapping_periods && result.overlapping_periods.length > 0) {
        const overlapDetails = result.overlapping_periods
          .map((p) => `${p.year}년 ${p.period_name} (${p.start_date} ~ ${p.end_date})`)
          .join(', ')
        errorMessage += `\n\n겹치는 기간: ${overlapDetails}`
      }

      throw new Error(errorMessage)
    }

    displayToast(result.message || '기간이 저장되었습니다.', 'success')
    closePeriodModal()
    await loadPeriodStatus()
  } catch (err) {
    console.error('기간 저장 오류:', err)
    // 여러 줄 메시지 처리
    const message = err.message.split('\n')[0] // 첫 번째 줄만 토스트에 표시
    displayToast(message, 'error')

    // 전체 에러 메시지는 콘솔에 출력
    if (err.message.includes('\n')) {
      console.warn('전체 에러 메시지:', err.message)
    }
  }
}

const completePeriod = async (period) => {
  if (!confirm(`${period.period_name} 기간을 완료 처리하시겠습니까?`)) return

  try {
    const response = await fetch(`/api/security-education/periods/${period.period_id}/complete`, {
      method: 'POST',
      credentials: 'include',
    })

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.error || '완료 처리 실패')
    }

    displayToast(result.message, 'success')
    await loadPeriodStatus()
    await loadEducationData()
  } catch (err) {
    console.error('완료 처리 오류:', err)
    displayToast(err.message, 'error')
  }
}

const reopenPeriod = async (period) => {
  if (!confirm(`${period.period_name} 기간을 재개하시겠습니까?`)) return

  try {
    const response = await fetch(`/api/security-education/periods/${period.period_id}/reopen`, {
      method: 'POST',
      credentials: 'include',
    })

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.error || '재개 처리 실패')
    }

    displayToast(result.message, 'success')
    await loadPeriodStatus()
    await loadEducationData()
  } catch (err) {
    console.error('재개 처리 오류:', err)
    displayToast(err.message, 'error')
  }
}

const deletePeriod = async (period) => {
  if (!confirm(`${period.period_name} 기간을 삭제하시겠습니까?`)) return

  try {
    const response = await fetch(`/api/security-education/periods/${period.period_id}`, {
      method: 'DELETE',
      credentials: 'include',
    })

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.error || '삭제 실패')
    }

    displayToast(result.message, 'success')
    await loadPeriodStatus()
  } catch (err) {
    console.error('기간 삭제 오류:', err)
    displayToast(err.message, 'error')
  }
}

const closePeriodModal = () => {
  showPeriodModal.value = false
  editingPeriod.value = null
  periodForm.value = {
    education_year: selectedYear.value,
    period_name: '',
    education_type: '오프라인',
    start_date: '',
    end_date: '',
    description: '',
    auto_pass_setting: true,
  }
}

// 파일 업로드 메서드
const handleFileSelect = (event) => {
  if (!selectedUploadPeriod.value) {
    displayToast('먼저 교육 기간을 선택해주세요.', 'warning')
    return
  }

  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    parseFile(file)
  }
}

const handleFileDrop = (event) => {
  event.preventDefault()
  isDragging.value = false

  if (!selectedUploadPeriod.value) {
    displayToast('먼저 교육 기간을 선택해주세요.', 'warning')
    return
  }

  const file = event.dataTransfer.files[0]
  if (file) {
    selectedFile.value = file
    parseFile(file)
  }
}

const removeSelectedFile = () => {
  selectedFile.value = null
  uploadPreview.value = []
}

// ✅ 새로운 메서드: 교육 기간 변경 처리
const onPeriodChange = () => {
  if (selectedFile.value) {
    // 기간 변경 시 파일 초기화하고 재검증 필요 알림
    selectedFile.value = null
    uploadPreview.value = []
    validationWarnings.value = []
    displayToast('교육 기간이 변경되어 파일을 다시 선택해주세요.', 'info')
  }
}

// ✅ 개선된 파일 처리: 단순 파싱만 수행 (비즈니스 로직 제거)
const parseFile = async (file) => {
  try {
    const fileName = file.name.toLowerCase()
    let records = []

    if (fileName.endsWith('.csv')) {
      // CSV 파일 처리
      const text = await file.text()
      const lines = text.split('\n')
      const headers = lines[0].split(',').map((h) => h.trim().replace(/"/g, ''))

      for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim()) {
          const values = lines[i].split(',').map((v) => v.trim().replace(/"/g, ''))
          const record = {}
          headers.forEach((header, index) => {
            record[header] = values[index] || ''
          })
          records.push(record)
        }
      }
    } else if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
      // Excel 파일 처리
      const arrayBuffer = await file.arrayBuffer()
      const XLSX = window.XLSX || (await import('xlsx'))

      const workbook = XLSX.read(arrayBuffer, { type: 'array' })
      const sheetName = workbook.SheetNames[0]
      const worksheet = workbook.Sheets[sheetName]

      records = XLSX.utils.sheet_to_json(worksheet, {
        raw: false,
        dateNF: 'yyyy-mm-dd hh:mm:ss',
      })
    } else {
      throw new Error('지원하지 않는 파일 형식입니다. CSV 또는 Excel 파일을 선택해주세요.')
    }

    // ✅ 개선: 단순 필드 매핑만 수행 (백엔드가 비즈니스 로직 처리)
    const processedRecords = normalizeFieldNames(records)

    // ✅ 새로운 기능: 클라이언트 사이드 기본 검증
    const validation = validateUploadData(processedRecords)

    uploadPreview.value = processedRecords
    validationWarnings.value = validation.warnings

    if (validation.errors.length > 0) {
      displayToast(`파일 검증 실패: ${validation.errors[0]}`, 'error')
      uploadPreview.value = []
      return
    }

    displayToast(`${processedRecords.length}개의 레코드가 준비되었습니다.`, 'success')
  } catch (err) {
    console.error('파일 파싱 실패:', err)
    displayToast(`파일 파싱에 실패했습니다: ${err.message}`, 'error')
    uploadPreview.value = []
    validationWarnings.value = []
  }
}

// ✅ 수정: 새로운 CSV 형식에 맞는 필드 매핑
const normalizeFieldNames = (records) => {
  const fieldMapping = {
    // ✅ 새로운 CSV 형식 필드 매핑
    이름: 'username',
    사용자명: 'username',
    사용자이름: 'username',
    부서: 'department',
    소속: 'department',
    소속부서: 'department',
    수강과정: 'education_type',
    교육과정: 'education_type',
    과정명: 'education_type',
    과정: 'education_type',
    수료: 'completed_count',
    수료횟수: 'completed_count',
    완료: 'completed_count',
    완료횟수: 'completed_count',
    미수료: 'incomplete_count',
    미완료: 'incomplete_count',
    미이수: 'incomplete_count',
    실패: 'incomplete_count',
    실패횟수: 'incomplete_count',

    // 영문 헤더도 지원 (기존 유지)
    username: 'username',
    department: 'department',
    education_type: 'education_type',
    completed_count: 'completed_count',
    incomplete_count: 'incomplete_count',
  }

  return records
    .map((record) => {
      const processedRecord = {}

      // 필드명 매핑
      Object.keys(record).forEach((key) => {
        const normalizedKey = key.trim().replace(/\s+/g, '')
        const mappedKey = fieldMapping[normalizedKey] || fieldMapping[key] || key
        processedRecord[mappedKey] = record[key]
      })

      // ✅ 중요: 타입 변환 및 기본값 설정
      processedRecord.completed_count = Math.max(0, parseInt(processedRecord.completed_count) || 0)
      processedRecord.incomplete_count = Math.max(
        0,
        parseInt(processedRecord.incomplete_count) || 0,
      )

      // 문자열 필드 정리
      if (processedRecord.username)
        processedRecord.username = processedRecord.username.toString().trim()
      if (processedRecord.department)
        processedRecord.department = processedRecord.department.toString().trim()
      if (processedRecord.education_type)
        processedRecord.education_type = processedRecord.education_type.toString().trim()

      return processedRecord
    })
    .filter((record) => record.username && record.department && record.education_type)
}

// ✅ 기존 업로드 메서드는 대부분 유지 (API 호출 부분만 약간 수정)
const executeUpload = async () => {
  if (!selectedUploadPeriod.value) {
    displayToast('교육 기간을 선택해주세요.', 'warning')
    return
  }

  if (uploadPreview.value.length === 0) {
    displayToast('업로드할 파일을 선택해주세요.', 'warning')
    return
  }

  uploading.value = true

  try {
    // ✅ 핵심 수정: 새로운 필드명으로 데이터 전송
    const uploadData = {
      period_id: selectedUploadPeriod.value,
      records: uploadPreview.value.map((record) => ({
        // ✅ 새로운 API가 기대하는 필드명으로 매핑
        이름: record.username,
        부서: record.department,
        수강과정: record.education_type,
        수료: record.completed_count,
        미수료: record.incomplete_count,
      })),
    }

    console.log('[DEBUG] 업로드 데이터 전송:', {
      period_id: uploadData.period_id,
      record_count: uploadData.records.length,
      sample_record: uploadData.records[0],
    })

    // 기존 API 호출 코드 유지
    const response = await fetch('/api/security-education/bulk-upload', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(uploadData),
    })

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.error || '업로드 실패')
    }

    // 기존 성공 처리 로직 유지
    const successMsg =
      `${selectedPeriodInfo.value.period_name}에 업로드 완료!\n` +
      `✅ 성공: ${result.success_count}건\n` +
      (result.update_count > 0 ? `🔄 업데이트: ${result.update_count}건\n` : '') +
      (result.error_count > 0 ? `❌ 오류: ${result.error_count}건` : '')

    displayToast(successMsg, 'success')

    // 오류 상세 정보 표시 (기존 유지)
    if (result.error_count > 0 && result.errors) {
      console.warn('업로드 오류 상세:', result.errors)
      setTimeout(() => {
        displayToast(`오류 상세: ${result.errors.slice(0, 3).join(', ')}`, 'warning')
      }, 2000)
    }

    closeBulkUploadModal()
    await loadEducationData()
  } catch (err) {
    console.error('업로드 오류:', err)
    displayToast(`업로드 실패: ${err.message}`, 'error')
  } finally {
    uploading.value = false
  }
}

// ✅ 수정: 새로운 CSV 형식 검증
const validateUploadData = (records) => {
  const warnings = []
  const errors = []

  if (records.length === 0) {
    errors.push('유효한 데이터가 없습니다.')
    return { warnings, errors }
  }

  // ✅ 새로운 필수 필드 검증 (기존과 다름)
  const requiredFields = [
    'username',
    'department',
    'education_type',
    'completed_count',
    'incomplete_count',
  ]

  for (let i = 0; i < records.length; i++) {
    const record = records[i]
    const missingFields = requiredFields.filter((field) => !record[field] && record[field] !== 0)

    if (missingFields.length > 0) {
      errors.push(`행 ${i + 1}: 필수 필드 누락 (${missingFields.join(', ')})`)
      continue
    }

    // ✅ 새로운 검증: 수료/미수료 횟수 유효성
    const completed = parseInt(record.completed_count) || 0
    const incomplete = parseInt(record.incomplete_count) || 0

    if (completed < 0 || incomplete < 0) {
      errors.push(`행 ${i + 1}: 수료/미수료 횟수는 0 이상이어야 합니다`)
    }

    if (completed + incomplete === 0) {
      warnings.push(`행 ${i + 1} (${record.username}): 수료와 미수료가 모두 0입니다`)
    }

    // 기존 검증도 유지
    if (!record.username?.trim()) {
      errors.push(`행 ${i + 1}: 사용자명이 비어있습니다`)
    }

    if (!record.department?.trim()) {
      errors.push(`행 ${i + 1}: 부서명이 비어있습니다`)
    }

    if (!record.education_type?.trim()) {
      errors.push(`행 ${i + 1}: 수강과정이 비어있습니다`)
    }
  }

  return { warnings, errors }
}

// 디버깅을 위한 reactive 데이터 추가
const debugInfo = ref({
  loadingPeriods: false,
  periodsError: null,
  apiResponse: null,
})

// ✅ 개선된 모달 관리
const openBulkUploadModal = async () => {
  console.log('[DEBUG] 업로드 모달 열기')

  // 활성 기간 목록 로드
  await loadAvailablePeriodsForUpload()

  showBulkUploadModal.value = true
  selectedFile.value = null
  uploadPreview.value = []
  selectedUploadPeriod.value = ''
  validationWarnings.value = []
}

// ✅ 새로운 computed: 선택된 기간 정보
const selectedPeriodInfo = computed(() => {
  if (!selectedUploadPeriod.value) return null

  for (const typeData of Object.values(availablePeriodsForUpload.value)) {
    const period = typeData.periods.find((p) => p.period_id == selectedUploadPeriod.value)
    if (period) return period
  }
  return null
})

// ✅ 새로운 computed: 업로드 가능 여부 검증
const canUpload = computed(() => {
  return (
    selectedUploadPeriod.value &&
    uploadPreview.value.length > 0 &&
    !uploading.value &&
    validationWarnings.value.filter((w) => w.includes('오류')).length === 0
  )
})

// ✅ 새로운 computed: 총 수료/미수료 횟수 계산
const getTotalCompletedCount = () => {
  return uploadPreview.value.reduce(
    (sum, record) => sum + (parseInt(record.completed_count) || 0),
    0,
  )
}

const getTotalIncompleteCount = () => {
  return uploadPreview.value.reduce(
    (sum, record) => sum + (parseInt(record.incomplete_count) || 0),
    0,
  )
}

// ✅ 교육 기간 선택 변경 시 파일 초기화
watch(selectedUploadPeriod, (newValue, oldValue) => {
  if (newValue !== oldValue && selectedFile.value) {
    // 기간이 변경되면 파일 선택 초기화
    selectedFile.value = null
    uploadPreview.value = []
    displayToast('교육 기간이 변경되어 파일 선택을 초기화했습니다.', 'info')
  }
})

// ✅ 업로드 가능한 교육 기간 목록 로드
const loadAvailablePeriodsForUpload = async () => {
  try {
    const response = await fetch('/api/security-education/periods/status', {
      credentials: 'include',
    })

    if (!response.ok) {
      throw new Error('교육 기간 목록 로드 실패')
    }

    const result = await response.json()
    availablePeriodsForUpload.value = result.education_types || {}

    console.log('[DEBUG] 업로드 가능한 교육 기간:', availablePeriodsForUpload.value)
  } catch (err) {
    console.error('교육 기간 로드 오류:', err)
    displayToast('교육 기간 목록을 불러오는데 실패했습니다.', 'error')
  }
}

// ✅ 기간 상태 텍스트 반환
const getPeriodStatusText = (period) => {
  if (period.is_completed) return '완료됨'

  const now = new Date()
  const startDate = new Date(period.start_date)
  const endDate = new Date(period.end_date)

  if (now < startDate) return '예정'
  if (now > endDate) return '종료됨'
  return '진행중'
}

// ✅ 기간 상태 CSS 클래스 반환
const getPeriodStatusClass = (period) => {
  if (period.is_completed) return 'status-completed'

  const now = new Date()
  const startDate = new Date(period.start_date)
  const endDate = new Date(period.end_date)

  if (now < startDate) return 'status-upcoming'
  if (now > endDate) return 'status-ended'
  return 'status-active'
}

// ✅ 날짜 범위 포맷팅
const formatDateRange = (startDate, endDate) => {
  const start = new Date(startDate).toLocaleDateString('ko-KR')
  const end = new Date(endDate).toLocaleDateString('ko-KR')
  return `${start} ~ ${end}`
}

// 디버깅용 메서드 추가
const testPeriodsAPI = async () => {
  console.log('[DEBUG] 수동 API 테스트 시작')
  try {
    // 1. 전체 기간 조회 테스트
    const allPeriodsResponse = await fetch('/api/security-education/periods', {
      credentials: 'include',
    })
    const allPeriodsResult = await allPeriodsResponse.json()
    console.log('[DEBUG] 전체 기간 조회 결과:', allPeriodsResult)

    // 2. 활성 기간 조회 테스트
    const activePeriodsResponse = await fetch(
      `/api/security-education/periods/active?year=${selectedYear.value}`,
      {
        credentials: 'include',
      },
    )
    const activePeriodsResult = await activePeriodsResponse.json()
    console.log('[DEBUG] 활성 기간 조회 결과:', activePeriodsResult)
  } catch (err) {
    console.error('[DEBUG] API 테스트 오류:', err)
  }
}

// ✅ 개선된 업로드 처리: 백엔드에서 모든 비즈니스 로직 처리
const processBulkUpload = async () => {
  if (!canUpload.value) {
    if (!selectedUploadPeriod.value) {
      displayToast('교육 기간을 선택해주세요.', 'warning')
      return
    }
    if (uploadPreview.value.length === 0) {
      displayToast('업로드할 파일을 선택해주세요.', 'warning')
      return
    }
    return
  }

  uploading.value = true

  try {
    // ✅ 핵심 개선: 원시 데이터만 전송, 백엔드에서 수료/미수료 결정
    const uploadData = {
      period_id: selectedUploadPeriod.value,
      records: uploadPreview.value, // 단순 정규화된 데이터만 전송
    }

    console.log('[DEBUG] 업로드 데이터 전송:', {
      period_id: uploadData.period_id,
      record_count: uploadData.records.length,
      sample_record: uploadData.records[0],
    })

    const response = await fetch('/api/security-education/bulk-upload', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(uploadData),
    })

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.error || '업로드 실패')
    }

    // ✅ 개선: 백엔드 처리 결과를 명확하게 표시
    const successMsg =
      `${selectedPeriodInfo.value.period_name}에 업로드 완료!\n` +
      `✅ 성공: ${result.success_count}건\n` +
      (result.update_count > 0 ? `🔄 업데이트: ${result.update_count}건\n` : '') +
      (result.error_count > 0 ? `❌ 오류: ${result.error_count}건` : '')

    displayToast(successMsg, 'success')

    // 오류가 있는 경우 상세 정보 표시
    if (result.error_count > 0 && result.errors) {
      console.warn('업로드 오류 상세:', result.errors)
      setTimeout(() => {
        displayToast(`오류 상세: ${result.errors.slice(0, 3).join(', ')}`, 'warning')
      }, 2000)
    }

    closeBulkUploadModal()
    await loadEducationData()
  } catch (err) {
    console.error('업로드 오류:', err)
    displayToast(`업로드 실패: ${err.message}`, 'error')
  } finally {
    uploading.value = false
  }
}

// ✅ 모달 닫기 함수 수정
const closeBulkUploadModal = () => {
  showBulkUploadModal.value = false
  selectedFile.value = null
  uploadPreview.value = []
  selectedUploadPeriod.value = ''
  validationWarnings.value = []
}
// ✅ 편집 레코드 함수 개선 (기존 editRecord 함수 수정)
const editRecord = (record) => {
  // 새로운 스키마 데이터를 기존 형식으로 변환
  editingRecord.value = {
    education_id: record.education_id,
    user_id: record.user_id,
    username: record.username,
    department: record.department,
    education_year: record.education_year,
    education_period: record.education_period,
    education_type: record.education_type,
    education_date: record.education_date,
    // ✅ 새로운 필드들
    course_name: record.course_name,
    completed_count: record.completed_count || 0,
    incomplete_count: record.incomplete_count || 0,
    total_courses: record.total_courses || 1,
    completion_rate: record.completion_rate || 0,
    // 기존 필드들
    completion_status: record.completion_status,
    exclude_from_scoring: record.exclude_from_scoring,
    exclude_reason: record.exclude_reason,
    notes: record.notes,
    period_id: record.period_id,
  }
  showEditModal.value = true
}

// ✅ 상태 통계 계산 함수 (템플릿에서 사용)
const getRecordsSummary = () => {
  if (!filteredRecords.value.length) return null

  const total = filteredRecords.value.length
  const completed = filteredRecords.value.filter((r) => {
    if (r.completion_rate !== undefined) {
      return r.completion_rate >= 80
    }
    return r.completion_status === 1
  }).length

  const excluded = filteredRecords.value.filter((r) => r.exclude_from_scoring).length

  return {
    total,
    completed,
    incomplete: total - completed,
    excluded,
    completionRate: total > 0 ? Math.round((completed / total) * 100) : 0,
  }
}

// ✅ 새로운 스키마 데이터 감지 함수
const hasEnhancedData = computed(() => {
  return educationData.value.some(
    (record) => record.course_name && record.completion_rate !== undefined,
  )
})

const deleteRecord = async (record) => {
  if (!confirm('이 교육 기록을 삭제하시겠습니까?')) return

  try {
    const response = await fetch('/api/security-education/delete', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        user_id: record.user_id,
        period_id: record.period_id,
        education_type: record.education_type,
      }),
    })

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.error || '삭제 실패')
    }

    displayToast(result.message, 'success')
    await loadEducationData()
  } catch (err) {
    console.error('기록 삭제 오류:', err)
    displayToast(err.message, 'error')
  }
}

const closeEditModal = () => {
  showEditModal.value = false
  editingRecord.value = {}
}

// 선택 관리
const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedRecords.value = [...paginatedRecords.value]
  } else {
    selectedRecords.value = []
  }
}

const updateSelectAll = () => {
  selectAll.value =
    paginatedRecords.value.length > 0 &&
    selectedRecords.value.length === paginatedRecords.value.length
}

// 예외처리
const toggleExceptionStatus = async (record) => {
  if (!confirm(`${record.username}의 교육 제외 상태를 변경하시겠습니까?`)) return

  try {
    const newExcludeStatus = !record.exclude_from_scoring

    const response = await fetch('/api/security-education/toggle-exception', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        user_id: record.user_id,
        period_id: record.period_id,
        education_type: record.education_type,
        exclude: newExcludeStatus,
        exclude_reason: newExcludeStatus ? '관리자 설정' : '',
      }),
    })

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.error || '제외 상태 변경 실패')
    }

    record.exclude_from_scoring = newExcludeStatus
    record.exclude_reason = newExcludeStatus ? '관리자 설정' : ''

    displayToast(result.message || '제외 상태가 변경되었습니다.', 'success')
    await loadEducationData()
  } catch (err) {
    console.error('제외 상태 변경 오류:', err)
    displayToast(err.message, 'error')
  }
}

const bulkToggleException = async () => {
  if (selectedRecords.value.length === 0) return

  try {
    const response = await fetch('/api/security-education/bulk-toggle-exception', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        records: selectedRecords.value.map((r) => ({
          user_id: r.user_id,
          period_id: r.period_id,
          education_type: r.education_type,
        })),
      }),
    })

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.error || '일괄 제외 상태 변경 실패')
    }

    displayToast(result.message, 'success')
    selectedRecords.value = []
    await loadEducationData()
  } catch (err) {
    console.error('일괄 제외 상태 변경 오류:', err)
    displayToast(err.message, 'error')
  }
}

// 내보내기
const exportEducationData = async () => {
  try {
    const params = new URLSearchParams({
      year: selectedYear.value,
      format: 'csv',
    })

    const response = await fetch(`/api/security-education/export?${params}`, {
      method: 'GET',
      credentials: 'include',
      headers: { Accept: 'text/csv' },
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || '데이터 내보내기에 실패했습니다.')
    }

    const blob = await response.blob()
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `정보보호교육_데이터_${selectedYear.value}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    displayToast('데이터가 성공적으로 내보내졌습니다.', 'success')
  } catch (err) {
    console.error('내보내기 실패:', err)
    displayToast(err.message, 'error')
  }
}

const downloadTemplate = async () => {
  try {
    const response = await fetch('/api/security-education/template/download', {
      credentials: 'include',
    })

    if (!response.ok) throw new Error('템플릿 다운로드 실패')

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = '정보보호교육_업로드_템플릿.csv'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (err) {
    console.error('템플릿 다운로드 오류:', err)
    displayToast('템플릿 다운로드에 실패했습니다.', 'error')
  }
}

// ✅ 날짜 포맷 함수들
const formatDate = (dateString) => {
  if (!dateString) return '-'
  try {
    return new Date(dateString).toLocaleDateString('ko-KR')
  } catch {
    return dateString
  }
}

const formatDateShort = (dateString) => {
  if (!dateString) return '-'
  try {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      month: '2-digit',
      day: '2-digit',
    })
  } catch {
    return dateString
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const truncateText = (text, maxLength) => {
  if (!text) return '-'
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

// ✅ 새로운 헬퍼 함수들
const getTypeClass = (educationType) => {
  const typeMap = {
    온라인: 'type-online',
    오프라인: 'type-offline',
    신입교육: 'type-newbie',
    심화교육: 'type-advanced',
    기본교육: 'type-basic',
  }
  return typeMap[educationType] || 'type-default'
}

const getRateClass = (rate) => {
  if (rate >= 80) return 'rate-excellent'
  if (rate >= 60) return 'rate-good'
  if (rate >= 40) return 'rate-warning'
  return 'rate-poor'
}

const getRateTextClass = (rate) => {
  if (rate >= 80) return 'text-excellent'
  if (rate >= 60) return 'text-good'
  if (rate >= 40) return 'text-warning'
  return 'text-danger'
}

const getStatusClass = (record) => {
  if (record.exclude_from_scoring) return 'status-excluded'

  // 새로운 스키마 기반
  if (record.completion_rate !== undefined) {
    if (record.completion_rate >= 100) return 'status-completed'
    if (record.completion_rate >= 80) return 'status-passed'
    if (record.completion_rate > 0) return 'status-partial'
    return 'status-not-started'
  }

  // 레거시 스키마 기반
  if (record.completion_status === 1) return 'status-completed'
  return 'status-incomplete'
}

const getStatusText = (record) => {
  if (record.status_text) return record.status_text

  if (record.exclude_from_scoring) return '제외'

  // 새로운 스키마 기반
  if (record.completion_rate !== undefined) {
    if (record.completion_rate >= 100) return '완료'
    if (record.completion_rate >= 80) return '수료'
    if (record.completion_rate > 0) return `부분완료(${record.completion_rate.toFixed(0)}%)`
    return '미실시'
  }

  // 레거시 기반
  return record.completion_status === 1 ? '수료' : '미수료'
}

const displayToast = (message, type = 'success') => {
  toastMessage.value = message
  toastType.value = type
  showToast.value = true

  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

// 워처
watch(selectedYear, () => {
  loadPeriodStatus()
  loadEducationData()
})
</script>

<style scoped>
@import '../styles/AdminSecurityEducationManagement.css';
</style>
