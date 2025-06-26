<template>
  <div class="admin-training">
    <!-- ===== 관리 헤더 ===== -->
    <div class="admin-header">
      <h1>피싱 훈련 관리</h1>
      <div class="admin-nav">
        <RouterLink to="/admin/education" class="nav-item">교육 관리</RouterLink>
        <RouterLink to="/admin/phishing" class="nav-item active">피싱 훈련 관리</RouterLink>
        <RouterLink to="/admin/manual-check" class="nav-item">수시 점검 관리</RouterLink>
        <RouterLink to="/admin/exceptions" class="nav-item">제외 설정</RouterLink>
      </div>
    </div>

    <div class="management-content">
      <!-- ===== 훈련 기간 관리 섹션 ===== -->
      <div class="period-management-section">
        <div class="section-header">
          <h3>🗓️ 훈련 기간 관리</h3>
          <button @click="openPeriodModal" class="primary-button">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"
              />
            </svg>
            기간 추가
          </button>
        </div>

        <!-- 훈련 기간 카드들 -->
        <div
          class="period-cards"
          v-if="periodStatus.training_types && Object.keys(periodStatus.training_types).length > 0"
        >
          <div
            v-for="(typeData, trainingType) in periodStatus.training_types"
            :key="trainingType"
            class="education-type-group"
          >
            <!-- 훈련 유형 헤더 -->
            <div class="type-header-with-stats">
              <div class="type-title-section">
                <h4 class="type-header">{{ trainingType }} 훈련</h4>
                <div class="type-summary">
                  <span class="stat-item"> 참가자 {{ typeData.total_participants }}명 </span>
                  <span class="stat-item success"> 성공 {{ typeData.total_success }}명 </span>
                  <span class="stat-item failure"> 실패 {{ typeData.total_failure }}명 </span>
                  <span class="stat-item" :class="getRateClass(getTypeSuccessRate(typeData))">
                    성공률 {{ getTypeSuccessRate(typeData) }}%
                  </span>
                </div>
              </div>
            </div>

            <div class="type-periods">
              <div
                v-for="period in typeData.periods"
                :key="period.period_id"
                class="period-card"
                :class="[`status-${period.status}`, { completed: period.is_completed }]"
              >
                <!-- 카드 헤더 -->
                <div class="card-header">
                  <h5>{{ period.period_name }}</h5>
                  <div class="status-badge" :class="getCardHeaderStatusClass(period.status)">
                    {{ period.status }}
                  </div>
                </div>

                <!-- 카드 바디 -->
                <div class="card-body">
                  <div class="period-info">
                    <div class="info-item">
                      <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path
                          d="M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5zM1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4H1z"
                        />
                      </svg>
                      {{ formatDateRange(period.start_date, period.end_date) }}
                    </div>
                    <div class="info-item">
                      <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path
                          d="M15 14s1 0 1-1-1-4-5-4-5 3-5 4 1 1 1 1h8zm-7.978-1A.261.261 0 0 1 7 12.996c.001-.264.167-1.03.76-1.72C8.312 10.629 9.282 10 11 10c1.717 0 2.687.63 3.24 1.276.593.69.758 1.457.76 1.72l-.008.002a.274.274 0 0 1-.014.002H7.022zM11 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm3-2a3 3 0 1 1-6 0 3 3 0 0 1 6 0zM6.936 9.28a5.88 5.88 0 0 0-1.23-.247A7.35 7.35 0 0 0 5 9c-4 0-5 3-5 4 0 .667.333 1 1 1h4.216A2.238 2.238 0 0 1 5 13c0-1.01.377-2.042 1.09-2.904.243-.294.526-.569.846-.816zM4.92 10A5.493 5.493 0 0 0 4 13H1c0-.26.164-1.03.76-1.724.545-.636 1.492-1.256 3.16-1.275zM1.5 5.5a3 3 0 1 1 6 0 3 3 0 0 1-6 0zm3-2a2 2 0 1 0 0 4 2 2 0 0 0 0-4z"
                        />
                      </svg>
                      참가자 {{ period.participants }}명
                    </div>
                    <div class="info-item">
                      <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path
                          d="M10.067.87a2.89 2.89 0 0 0-4.134 0l-.622.638-.89-.011a2.89 2.89 0 0 0-2.924 2.924l.01.89-.636.622a2.89 2.89 0 0 0 0 4.134l.637.622-.011.89a2.89 2.89 0 0 0 2.924 2.924l.89-.01.622.636a2.89 2.89 0 0 0 4.134 0l.622-.637.89.011a2.89 2.89 0 0 0 2.924-2.924l-.01-.89.636-.622a2.89 2.89 0 0 0 0-4.134l-.637-.622.011-.89a2.89 2.89 0 0 0-2.924-2.924l-.89.01-.622-.636zm.287 5.984-3 3a.5.5 0 0 1-.708 0l-1.5-1.5a.5.5 0 1 1 .708-.708L7 8.793l2.646-2.647a.5.5 0 0 1 .708.708z"
                        />
                      </svg>
                      <span :class="getRateClass(period.success_rate)">
                        성공률 {{ period.success_rate }}%
                      </span>
                    </div>
                  </div>

                  <!-- 통계 정보 -->
                  <div class="period-stats">
                    <div class="stats-grid">
                      <div class="stat-item success">
                        <span class="stat-value">{{ period.success_count }}</span>
                        <span class="stat-label">성공</span>
                      </div>
                      <div class="stat-item failure">
                        <span class="stat-value">{{ period.failure_count }}</span>
                        <span class="stat-label">실패</span>
                      </div>
                    </div>
                  </div>

                  <!-- 설명 -->
                  <div v-if="period.description" class="period-description">
                    {{ period.description }}
                  </div>
                </div>

                <!-- 카드 액션 버튼들 -->
                <div class="card-actions">
                  <button
                    @click="editPeriod(period)"
                    class="edit-button"
                    :disabled="period.is_completed"
                    title="기간 수정"
                  >
                    <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                      <path
                        d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708L14.5 5.207l-3-3L12.146.146zM11.207 1.5 13.5 3.793 4.793 12.5H2.5v-2.293L11.207 1.5z"
                      />
                    </svg>
                    수정
                  </button>

                  <button
                    v-if="!period.is_completed"
                    @click="completePeriod(period)"
                    class="complete-button"
                    title="기간 완료"
                  >
                    <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                      <path
                        d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"
                      />
                    </svg>
                    완료
                  </button>

                  <button
                    v-else
                    @click="reopenPeriod(period)"
                    class="reopen-button"
                    title="기간 재개"
                  >
                    <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z" />
                      <path
                        d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"
                      />
                    </svg>
                    재개
                  </button>

                  <button
                    @click="deletePeriod(period)"
                    class="delete-button"
                    :disabled="period.participants > 0"
                    title="기간 삭제"
                  >
                    <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                      <path
                        d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"
                      />
                      <path
                        fill-rule="evenodd"
                        d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"
                      />
                    </svg>
                    삭제
                  </button>

                  <button @click="viewDetailStats(period)" class="stats-button" title="상세 통계">
                    <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                      <path
                        d="M4 11H2v3h2v-3zm5-4H7v7h2V7zm5-5v12h-2V2h2zm-2-1a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1h-2zM6 7a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7zm-5 4a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1v-3z"
                      />
                    </svg>
                    통계
                  </button>

                  <button
                    @click="openUploadModal(period)"
                    class="upload-button"
                    title="데이터 업로드"
                  >
                    <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                      <path
                        d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
                      />
                      <path
                        d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"
                      />
                    </svg>
                    업로드
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 비어있을 때 표시 -->
        <div v-else class="empty-state">
          <div class="empty-icon">
            <svg width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5zM1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4H1z"
              />
            </svg>
          </div>
          <h3>등록된 훈련 기간이 없습니다</h3>
          <p>새로운 피싱 훈련 기간을 추가해보세요.</p>
          <button @click="openPeriodModal" class="primary-button">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"
              />
            </svg>
            첫 번째 기간 추가
          </button>
        </div>
      </div>

      <!-- ===== 훈련 기록 관리 섹션 ===== -->
      <div class="table-section">
        <!-- 액션 버튼들 -->
        <div class="section-header">
          <h3>📋 훈련 기록 관리 ({{ filteredRecords.length }}건)</h3>
          <div class="section-actions">
            <button @click="downloadTemplate" class="outline-button">
              <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M14 14V4.5L9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2zM9.5 3A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h5.5v2z"
                />
              </svg>
              📄 템플릿 다운로드
            </button>
            <button @click="showBulkUploadModal = true" class="primary-button">
              <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
                />
                <path
                  d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"
                />
              </svg>
              📤 일괄 등록
            </button>
          </div>
        </div>

        <!-- 필터 섹션 -->
        <div class="filter-section">
          <div class="filter-group">
            <label>연도:</label>
            <select v-model="selectedYear" @change="loadTrainingData">
              <option v-for="year in availableYears" :key="year" :value="year">{{ year }}년</option>
            </select>
          </div>

          <div class="filter-group">
            <label>훈련유형:</label>
            <select v-model="selectedTrainingType" @change="loadTrainingData">
              <option value="">전체</option>
              <option value="이메일 피싱">이메일 피싱</option>
              <option value="SMS 피싱">SMS 피싱</option>
              <option value="전화 피싱">전화 피싱</option>
            </select>
          </div>

          <div class="filter-group">
            <label>결과:</label>
            <select v-model="selectedResult" @change="loadTrainingData">
              <option value="">전체</option>
              <option value="success">성공</option>
              <option value="fail">실패</option>
              <option value="no_response">무응답</option>
            </select>
          </div>

          <div class="search-group">
            <label>검색:</label>
            <input
              type="text"
              v-model="searchQuery"
              @input="searchTrainingData"
              placeholder="사용자명 또는 부서 검색..."
              class="search-input"
            />
          </div>
        </div>

        <!-- 기록 테이블은 다음 단계에서 구현 -->
        <div class="records-table-placeholder">
          <p>훈련 기록 테이블이 여기에 표시됩니다.</p>
        </div>
      </div>
    </div>

    <!-- 모달들은 다음 단계에서 구현 -->
    <!-- 기간 생성/수정 모달 -->
    <div v-if="showPeriodModal" class="modal-overlay" @click="closePeriodModal">
      <div class="modal-content period-modal" @click.stop>
        <div class="modal-header">
          <h3>
            {{ editingPeriod ? '훈련 기간 수정' : '새 훈련 기간 추가' }}
          </h3>
          <button @click="closePeriodModal" class="close-button">&times;</button>
        </div>

        <div class="modal-body">
          <form @submit.prevent="savePeriod">
            <!-- 기본 정보 섹션 -->
            <div class="form-section">
              <h4>기본 정보</h4>

              <div class="form-grid">
                <div class="form-group">
                  <label for="training-year">훈련 연도 *</label>
                  <select
                    id="training-year"
                    v-model="periodForm.training_year"
                    class="form-control"
                    required
                    :disabled="editingPeriod"
                  >
                    <option v-for="year in availableYears" :key="year" :value="year">
                      {{ year }}년
                    </option>
                  </select>
                  <small class="form-hint" v-if="editingPeriod">
                    기존 기간의 연도는 수정할 수 없습니다.
                  </small>
                </div>

                <div class="form-group">
                  <label for="training-type">훈련 유형 *</label>
                  <select
                    id="training-type"
                    v-model="periodForm.training_type"
                    class="form-control"
                    required
                  >
                    <option value="이메일 피싱">이메일 피싱</option>
                    <option value="SMS 피싱">SMS 피싱</option>
                    <option value="전화 피싱">전화 피싱</option>
                    <option value="웹사이트 피싱">웹사이트 피싱</option>
                    <option value="소셜 엔지니어링">소셜 엔지니어링</option>
                  </select>
                </div>
              </div>

              <div class="form-group">
                <label for="period-name">기간명 *</label>
                <input
                  id="period-name"
                  v-model="periodForm.period_name"
                  type="text"
                  class="form-control"
                  placeholder="예: 1차 이메일 피싱 훈련"
                  required
                  maxlength="50"
                />
                <small class="form-hint">
                  훈련 기간을 구분할 수 있는 명확한 이름을 입력하세요. (최대 50자)
                </small>
              </div>

              <div class="form-grid">
                <div class="form-group">
                  <label for="start-date">시작일 *</label>
                  <input
                    id="start-date"
                    v-model="periodForm.start_date"
                    type="date"
                    class="form-control"
                    required
                    :min="getMinDate()"
                  />
                </div>

                <div class="form-group">
                  <label for="end-date">종료일 *</label>
                  <input
                    id="end-date"
                    v-model="periodForm.end_date"
                    type="date"
                    class="form-control"
                    required
                    :min="periodForm.start_date || getMinDate()"
                  />
                </div>
              </div>

              <!-- 날짜 유효성 체크 메시지 -->
              <div v-if="dateValidationMessage" class="validation-message">
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"
                  />
                </svg>
                {{ dateValidationMessage }}
              </div>

              <div class="form-group">
                <label for="description">설명</label>
                <textarea
                  id="description"
                  v-model="periodForm.description"
                  class="form-control"
                  rows="3"
                  placeholder="훈련에 대한 간단한 설명을 입력하세요"
                  maxlength="500"
                ></textarea>
                <small class="form-hint">
                  {{ periodForm.description ? periodForm.description.length : 0 }}/500자
                </small>
              </div>
            </div>

            <!-- 훈련 설정 섹션 -->
            <div class="form-section">
              <h4>훈련 설정</h4>

              <div class="form-group">
                <div class="checkbox-group">
                  <input
                    id="auto-pass"
                    v-model="periodForm.auto_pass_setting"
                    type="checkbox"
                    class="form-checkbox"
                  />
                  <label for="auto-pass" class="checkbox-label">
                    자동 통과 처리 설정
                    <span class="tooltip-trigger">
                      <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path
                          d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"
                        />
                        <path
                          d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"
                        />
                      </svg>
                      <span class="tooltip-content">
                        기간 완료 시 무응답 사용자를 자동으로 성공 처리합니다.
                      </span>
                    </span>
                  </label>
                </div>
                <small class="form-hint">
                  체크하면 훈련 기간 완료 시 무응답한 사용자들을 자동으로 성공 처리합니다.
                </small>
              </div>
            </div>

            <!-- 중복 체크 안내 -->
            <div v-if="duplicateWarning" class="warning-section">
              <div class="warning-message">
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"
                  />
                </svg>
                {{ duplicateWarning }}
              </div>
            </div>

            <!-- 기존 기간 수정 시 추가 안내 -->
            <div v-if="editingPeriod && editingPeriod.is_completed" class="info-section">
              <div class="info-message">
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"
                  />
                  <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                </svg>
                완료된 훈련 기간입니다. 수정하려면 먼저 기간을 재개해야 합니다.
              </div>
            </div>

            <div class="modal-actions">
              <button type="button" @click="closePeriodModal" class="cancel-button">취소</button>
              <button type="submit" class="save-button" :disabled="!isValidPeriodForm || saving">
                <svg
                  v-if="saving"
                  width="16"
                  height="16"
                  fill="currentColor"
                  viewBox="0 0 16 16"
                  class="animate-spin"
                >
                  <path
                    d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"
                  />
                  <path
                    fill-rule="evenodd"
                    d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"
                  />
                </svg>
                <svg v-else width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M15.854 8.354a.5.5 0 0 0 0-.708L13.207 5a.5.5 0 0 0-.707.707L14.793 7.5H1a.5.5 0 0 0 0 1h13.793L12.5 10.793a.5.5 0 0 0 .707.707l2.647-2.646z"
                  />
                </svg>
                {{ saving ? '저장 중...' : editingPeriod ? '수정' : '생성' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    <!-- 피싱 훈련 업로드 모달 - AdminPhishingTrainingManagement.vue에 추가할 부분 -->

    <!-- 일괄 업로드 모달 -->
    <div v-if="showBulkUploadModal" class="modal-overlay" @click="closeBulkUploadModal">
      <div class="modal-content bulk-upload-modal" @click.stop>
        <div class="modal-header">
          <h3>피싱 훈련 결과 일괄 업로드</h3>
          <button @click="closeBulkUploadModal" class="close-button">&times;</button>
        </div>

        <div class="modal-body">
          <!-- 1단계: 훈련 기간 선택 -->
          <div class="upload-step" :class="{ disabled: !selectedUploadPeriod }">
            <h4>1단계: 훈련 기간 선택 (필수)</h4>
            <div class="period-selection">
              <select v-model="selectedUploadPeriod" @change="onPeriodChange" class="period-select">
                <option value="">훈련 기간을 선택하세요</option>
                <optgroup
                  v-for="(typeData, trainingType) in availablePeriodsForUpload"
                  :key="trainingType"
                  :label="`${trainingType} 훈련`"
                >
                  <option
                    v-for="period in typeData.periods"
                    :key="period.period_id"
                    :value="period.period_id"
                    :disabled="period.is_completed"
                  >
                    {{ period.period_name }} ({{
                      formatDateRange(period.start_date, period.end_date)
                    }}) - {{ getPeriodStatusText(period) }}
                  </option>
                </optgroup>
              </select>
            </div>

            <!-- 선택된 기간 정보 표시 -->
            <div v-if="selectedPeriodInfo" class="selected-period-info">
              <div class="info-card">
                <h5>선택된 훈련 기간</h5>
                <p><strong>기간명:</strong> {{ selectedPeriodInfo.period_name }}</p>
                <p><strong>훈련 유형:</strong> {{ selectedPeriodInfo.training_type }}</p>
                <p>
                  <strong>훈련 기간:</strong>
                  {{ formatDateRange(selectedPeriodInfo.start_date, selectedPeriodInfo.end_date) }}
                </p>
                <p><strong>상태:</strong> {{ getPeriodStatusText(selectedPeriodInfo) }}</p>
                <p v-if="selectedPeriodInfo.description">
                  <strong>설명:</strong> {{ selectedPeriodInfo.description }}
                </p>
              </div>
            </div>

            <!-- 기간 미선택 안내 -->
            <div v-if="!selectedUploadPeriod" class="warning-message">
              <p>⚠️ 먼저 훈련 기간을 선택해주세요</p>
            </div>
          </div>

          <!-- 2단계: 템플릿 다운로드 -->
          <div class="upload-step">
            <h4>2단계: 템플릿 다운로드</h4>
            <p>피싱 훈련 결과를 정확히 업로드하려면 아래 템플릿을 다운로드하여 사용하세요.</p>

            <div class="template-section">
              <button @click="downloadTemplate" class="template-btn">
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
                  />
                  <path
                    d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"
                  />
                </svg>
                엑셀 템플릿 다운로드
              </button>
            </div>

            <!-- 필수 컬럼 안내 -->
            <div class="column-guide">
              <h5>필수 컬럼 정보</h5>
              <div class="columns-list">
                <div class="column-item">
                  <span class="column-name">메일발송시각</span>
                  <span class="column-desc"
                    >피싱 메일을 발송한 날짜와 시간 (YYYY-MM-DD HH:MM:SS 형식)</span
                  >
                </div>
                <div class="column-item">
                  <span class="column-name">수행시각</span>
                  <span class="column-desc"
                    >사용자가 행동을 수행한 날짜와 시간 (빈 값이면 무응답 처리)</span
                  >
                </div>
                <div class="column-item">
                  <span class="column-name">로그유형</span>
                  <span class="column-desc"
                    >사용자 행동 유형 (예: 스크립트 첨부파일 열람, 이메일 열람2, 링크 클릭)</span
                  >
                </div>
                <div class="column-item">
                  <span class="column-name">메일유형</span>
                  <span class="column-desc"
                    >피싱 메일의 종류 (예: 퇴직연금 운용, 세금계산서, 카카오톡)</span
                  >
                </div>
                <div class="column-item">
                  <span class="column-name">이메일</span>
                  <span class="column-desc">대상 사용자의 이메일 주소</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 3단계: 파일 업로드 -->
          <div class="upload-step" :class="{ disabled: !selectedUploadPeriod }">
            <h4>3단계: 파일 업로드</h4>

            <div class="file-upload-area">
              <!-- 파일 드롭존 -->
              <div
                class="dropzone"
                :class="{ active: isDragOver }"
                @click="triggerFileSelect"
                @dragover.prevent="isDragOver = true"
                @dragleave.prevent="isDragOver = false"
                @drop.prevent="handleFileDrop"
              >
                <input
                  type="file"
                  ref="fileInput"
                  @change="handleFileSelect"
                  accept=".xlsx,.xls,.csv"
                  style="display: none"
                />

                <!-- 파일이 선택되지 않은 경우 -->
                <div v-if="!selectedFile" class="upload-placeholder">
                  <div class="upload-icon">
                    <svg width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
                      <path
                        d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
                      />
                      <path
                        d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"
                      />
                    </svg>
                  </div>
                  <h4>파일을 선택하거나 드래그하세요</h4>
                  <p>지원 형식: Excel (.xlsx, .xls), CSV (.csv)</p>
                  <p>최대 크기: 10MB</p>
                </div>

                <!-- 파일이 선택된 경우 -->
                <div v-else class="file-info">
                  <div class="file-icon">
                    <svg width="32" height="32" fill="currentColor" viewBox="0 0 16 16">
                      <path
                        d="M14 14V4.5L9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2zM9.5 3A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h5.5v2z"
                      />
                    </svg>
                  </div>
                  <div class="file-details">
                    <h5>{{ selectedFile.name }}</h5>
                    <p>크기: {{ formatFileSize(selectedFile.size) }}</p>
                  </div>
                  <button @click.stop="removeSelectedFile" class="remove-file-btn">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                      <path
                        d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"
                      />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- 파일 검증 결과 -->
            <div v-if="validationWarnings.length > 0" class="validation-warnings">
              <h5>검증 결과</h5>
              <ul class="warning-list">
                <li
                  v-for="(warning, index) in validationWarnings"
                  :key="index"
                  :class="warning.includes('오류') ? 'error' : 'warning'"
                >
                  {{ warning }}
                </li>
              </ul>
            </div>

            <!-- 업로드 미리보기 -->
            <div v-if="uploadPreview.length > 0" class="upload-preview">
              <h5>업로드 미리보기 ({{ uploadPreview.length }}건)</h5>

              <!-- 통계 요약 -->
              <div class="preview-stats">
                <div class="stat-card">
                  <span class="stat-label">총 기록</span>
                  <span class="stat-value">{{ uploadPreview.length }}건</span>
                </div>
                <div class="stat-card success">
                  <span class="stat-label">성공 예상</span>
                  <span class="stat-value">{{ getSuccessCount() }}건</span>
                </div>
                <div class="stat-card failure">
                  <span class="stat-label">실패 예상</span>
                  <span class="stat-value">{{ getFailureCount() }}건</span>
                </div>
                <div class="stat-card neutral">
                  <span class="stat-label">무응답 예상</span>
                  <span class="stat-value">{{ getNoResponseCount() }}건</span>
                </div>
              </div>

              <!-- 샘플 데이터 테이블 -->
              <div class="preview-table">
                <table>
                  <thead>
                    <tr>
                      <th>이메일</th>
                      <th>메일발송시각</th>
                      <th>수행시각</th>
                      <th>로그유형</th>
                      <th>메일유형</th>
                      <th>예상 결과</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(record, index) in uploadPreview.slice(0, 5)" :key="index">
                      <td>{{ record.target_email }}</td>
                      <td>{{ formatDateTime(record.email_sent_time) }}</td>
                      <td>{{ formatDateTime(record.action_time) || '무응답' }}</td>
                      <td>{{ record.log_type || '-' }}</td>
                      <td>{{ record.mail_type || '-' }}</td>
                      <td>
                        <span class="result-badge" :class="record.predicted_result">
                          {{ getResultText(record.predicted_result) }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <p v-if="uploadPreview.length > 5" class="more-records">
                  ... 외 {{ uploadPreview.length - 5 }}건
                </p>
              </div>
            </div>
          </div>

          <!-- 업로드 진행 상태 -->
          <div v-if="uploading" class="upload-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
            </div>
            <p>업로드 중... {{ uploadProgress }}%</p>
          </div>

          <!-- 업로드 결과 -->
          <div v-if="uploadResult" class="upload-result">
            <h5>업로드 완료</h5>
            <div class="result-summary">
              <div class="result-item success">
                <span class="result-label">성공:</span>
                <span class="result-value">{{ uploadResult.success_count }}건</span>
              </div>
              <div class="result-item update" v-if="uploadResult.update_count > 0">
                <span class="result-label">업데이트:</span>
                <span class="result-value">{{ uploadResult.update_count }}건</span>
              </div>
              <div class="result-item error" v-if="uploadResult.error_count > 0">
                <span class="result-label">실패:</span>
                <span class="result-value">{{ uploadResult.error_count }}건</span>
              </div>
              <div class="result-item total">
                <span class="result-label">전체:</span>
                <span class="result-value">{{ uploadResult.total_rows }}건</span>
              </div>
            </div>

            <!-- 오류 상세 -->
            <div v-if="uploadResult.errors && uploadResult.errors.length > 0" class="error-details">
              <h6>오류 상세:</h6>
              <ul class="error-list">
                <li v-for="(error, index) in uploadResult.errors" :key="index">
                  {{ error }}
                </li>
              </ul>
            </div>
          </div>

          <!-- 모달 액션 버튼 -->
          <div class="modal-actions">
            <button
              type="button"
              @click="closeBulkUploadModal"
              class="cancel-button"
              :disabled="uploading"
            >
              {{ uploading ? '업로드 중...' : '닫기' }}
            </button>

            <button
              type="button"
              @click="executeUpload"
              class="upload-button"
              :disabled="!canUpload || uploading"
            >
              <svg
                v-if="uploading"
                width="16"
                height="16"
                fill="currentColor"
                viewBox="0 0 16 16"
                class="animate-spin"
              >
                <path
                  d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"
                />
                <path
                  fill-rule="evenodd"
                  d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"
                />
              </svg>
              <svg v-else width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
                />
                <path
                  d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"
                />
              </svg>
              {{ uploading ? '업로드 중...' : '업로드 시작' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <!-- 상세 통계 모달 -->
  </div>
</template>
<script setup>
import { ref, computed, onMounted, watch } from 'vue'

// ===== 반응형 데이터 =====
const loading = ref(false)
const selectedYear = ref(new Date().getFullYear())
const selectedTrainingType = ref('')
const selectedResult = ref('')
const searchQuery = ref('')

// 기간 관리 데이터
const periodStatus = ref({
  training_types: {},
})

// 기록 관리 데이터
const trainingRecords = ref([])
const filteredRecords = ref([])

// 모달 상태
const showPeriodModal = ref(false)
const showBulkUploadModal = ref(false)
const showDetailStatsModal = ref(false)
const editingPeriod = ref(null)
const saving = ref(false)

// 업로드 모달 관련
const selectedFile = ref(null)
const uploadPreview = ref([])
const selectedUploadPeriod = ref('')
const availablePeriodsForUpload = ref({})
const validationWarnings = ref([])
const isDragOver = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadResult = ref(null)

// 폼 데이터
const periodForm = ref({
  period_id: null,
  training_year: new Date().getFullYear(),
  period_name: '',
  training_type: '이메일 피싱',
  start_date: '',
  end_date: '',
  description: '',
  isEdit: false,
  auto_pass_setting: true,
})

const selectedPeriod = ref(null)

// 폼 유효성 검사
const isValidPeriodForm = computed(() => {
  return (
    periodForm.value.period_name.trim() &&
    periodForm.value.training_type &&
    periodForm.value.start_date &&
    periodForm.value.end_date &&
    new Date(periodForm.value.start_date) < new Date(periodForm.value.end_date)
  )
})

// 날짜 유효성 검사 메시지
const dateValidationMessage = computed(() => {
  if (!periodForm.value.start_date || !periodForm.value.end_date) {
    return ''
  }

  const startDate = new Date(periodForm.value.start_date)
  const endDate = new Date(periodForm.value.end_date)

  if (startDate >= endDate) {
    return '종료일은 시작일보다 늦어야 합니다.'
  }

  // 기간이 너무 짧은 경우
  const diffDays = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24))
  if (diffDays < 1) {
    return '훈련 기간은 최소 1일 이상이어야 합니다.'
  }

  // 기간이 너무 긴 경우
  if (diffDays > 365) {
    return '훈련 기간은 1년을 초과할 수 없습니다.'
  }

  return ''
})

// 중복 기간 체크
const duplicateWarning = computed(() => {
  if (
    !periodForm.value.period_name ||
    !periodForm.value.training_type ||
    !periodForm.value.training_year
  ) {
    return ''
  }

  // 현재 기간들 중에서 중복 체크
  const currentPeriods = []
  Object.values(periodStatus.value.training_types || {}).forEach((typeData) => {
    if (typeData.periods) {
      currentPeriods.push(...typeData.periods)
    }
  })

  const duplicate = currentPeriods.find((period) => {
    // 수정 중인 경우 자기 자신은 제외
    if (editingPeriod.value && period.period_id === editingPeriod.value.period_id) {
      return false
    }

    return (
      period.training_year === periodForm.value.training_year &&
      period.period_name === periodForm.value.period_name &&
      period.training_type === periodForm.value.training_type
    )
  })

  if (duplicate) {
    return `동일한 연도(${periodForm.value.training_year})에 같은 이름의 ${periodForm.value.training_type} 기간이 이미 존재합니다.`
  }

  return ''
})

// ===== 계산된 속성 =====
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 6 }, (_, i) => currentYear - i)
})

const trainingTypes = ['이메일 피싱', 'SMS 피싱', '전화 피싱', '웹사이트 피싱']

// ===== 라이프사이클 =====
onMounted(() => {
  loadPeriodStatus()
  loadTrainingData()
})

// ===== 데이터 로딩 메서드 =====
const loadPeriodStatus = async () => {
  loading.value = true
  try {
    const response = await fetch(`/api/phishing/admin/periods?year=${selectedYear.value}`, {
      credentials: 'include',
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()

    // 데이터를 교육 관리와 동일한 구조로 변환
    const trainingTypes = {}

    if (data.periods && data.periods.length > 0) {
      data.periods.forEach((typeGroup) => {
        trainingTypes[typeGroup.type_name] = {
          total_participants: typeGroup.total_participants || 0,
          total_success: typeGroup.total_success || 0,
          total_failure: typeGroup.total_failure || 0,
          periods: typeGroup.periods || [],
        }
      })
    }

    periodStatus.value = { training_types: trainingTypes }
  } catch (error) {
    console.error('기간 상태 로딩 오류:', error)
    displayToast('기간 상태를 불러오는데 실패했습니다.', 'error')
    periodStatus.value = { training_types: {} }
  } finally {
    loading.value = false
  }
}

const loadTrainingData = async () => {
  try {
    const params = new URLSearchParams({
      year: selectedYear.value,
      ...(selectedTrainingType.value && { training_type: selectedTrainingType.value }),
      ...(selectedResult.value && { result: selectedResult.value }),
    })

    const response = await fetch(`/api/phishing/admin/records?${params}`, {
      credentials: 'include',
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    trainingRecords.value = data.records || []
    applyFilters()
  } catch (error) {
    console.error('훈련 데이터 로딩 오류:', error)
    displayToast('훈련 데이터를 불러오는데 실패했습니다.', 'error')
    trainingRecords.value = []
    filteredRecords.value = []
  }
}

// ===== 기간 관리 메서드 =====
const openPeriodModal = () => {
  editingPeriod.value = null
  periodForm.value = {
    training_year: selectedYear.value,
    period_name: '',
    training_type: '이메일 피싱',
    start_date: '',
    end_date: '',
    description: '',
    auto_pass_setting: true,
  }
  showPeriodModal.value = true
}

const resetPeriodForm = () => {
  periodForm.value = {
    period_id: null,
    training_year: selectedYear.value,
    period_name: '',
    training_type: '이메일 피싱',
    start_date: '',
    end_date: '',
    description: '',
    isEdit: false,
  }
}

/**
 * 기간 편집 모달 열기
 */
const editPeriod = (period) => {
  console.log('[DEBUG] 수정할 기간 데이터:', period)

  editingPeriod.value = period
  periodForm.value = {
    training_year: period.training_year,
    period_name: period.period_name,
    training_type: period.training_type,
    start_date: period.start_date,
    end_date: period.end_date,
    description: period.description || '',
    auto_pass_setting: period.auto_pass_setting === 1 || period.auto_pass_setting === true,
  }

  console.log('[DEBUG] 폼에 설정된 값들:', periodForm.value)
  showPeriodModal.value = true
}

/**
 * 기간 저장 (추가/수정)
 */
const savePeriod = async () => {
  if (!isValidPeriodForm.value || saving.value) {
    return
  }

  // 중복 체크
  if (duplicateWarning.value) {
    displayToast(duplicateWarning.value, 'error')
    return
  }

  saving.value = true

  try {
    console.log('[DEBUG] 기간 저장 요청:', periodForm.value)

    const method = editingPeriod.value ? 'PUT' : 'POST'
    const url = editingPeriod.value
      ? `/api/phishing/admin/periods/${editingPeriod.value.period_id}`
      : '/api/phishing/admin/periods'

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(periodForm.value),
    })

    const result = await response.json()
    console.log('[DEBUG] 서버 응답:', result)

    if (!response.ok) {
      // 완료된 기간 수정 시 특별 처리
      if (result.message && result.message.includes('완료된 훈련 기간은 수정할 수 없습니다')) {
        const confirmReopen = confirm(
          `이 기간은 완료 상태입니다.\n\n완료 상태를 해제하고 수정하시겠습니까?\n\n` +
            `※ 완료 상태 해제 시 자동 통과 처리된 데이터가 삭제될 수 있습니다.`,
        )

        if (confirmReopen) {
          await reopenAndEdit()
          return
        } else {
          displayToast('수정이 취소되었습니다.', 'info')
          return
        }
      }

      throw new Error(result.error || result.message || '저장 실패')
    }

    displayToast(
      editingPeriod.value ? '훈련 기간이 수정되었습니다.' : '훈련 기간이 생성되었습니다.',
      'success',
    )

    closePeriodModal()
    await loadPeriodStatus() // 기간 목록 새로고침
  } catch (error) {
    console.error('기간 저장 오류:', error)
    displayToast(error.message, 'error')
  } finally {
    saving.value = false
  }
}

/**
 * 기간 재개 후 수정
 */
const reopenAndEdit = async () => {
  try {
    // 먼저 기간 재개
    const reopenResponse = await fetch(
      `/api/phishing/admin/periods/${editingPeriod.value.period_id}/reopen`,
      {
        method: 'POST',
        credentials: 'include',
      },
    )

    if (!reopenResponse.ok) {
      const reopenResult = await reopenResponse.json()
      throw new Error(reopenResult.error || '기간 재개 실패')
    }

    // 재개 후 수정 진행
    const updateResponse = await fetch(
      `/api/phishing/admin/periods/${editingPeriod.value.period_id}`,
      {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(periodForm.value),
      },
    )

    if (!updateResponse.ok) {
      const updateResult = await updateResponse.json()
      throw new Error(updateResult.error || '수정 실패')
    }

    displayToast('기간이 재개되고 수정되었습니다.', 'success')
    closePeriodModal()
    await loadPeriodStatus()
  } catch (error) {
    console.error('재개 후 수정 오류:', error)
    displayToast(error.message, 'error')
  }
}

const completePeriod = async (period) => {
  if (!confirm(`"${period.period_name}" 기간을 완료 처리하시겠습니까?`)) {
    return
  }

  try {
    const response = await fetch(`/api/phishing/admin/periods/${period.period_id}/complete`, {
      method: 'POST',
      credentials: 'include',
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || '완료 처리에 실패했습니다.')
    }

    displayToast('기간이 완료 처리되었습니다.', 'success')
    await loadPeriodStatus()
  } catch (error) {
    console.error('기간 완료 오류:', error)
    displayToast(error.message, 'error')
  }
}

const reopenPeriod = async (period) => {
  if (!confirm(`"${period.period_name}" 기간을 재개하시겠습니까?`)) {
    return
  }

  try {
    const response = await fetch(`/api/phishing/admin/periods/${period.period_id}/reopen`, {
      method: 'POST',
      credentials: 'include',
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || '재개 처리에 실패했습니다.')
    }

    displayToast('기간이 재개되었습니다.', 'success')
    await loadPeriodStatus()
  } catch (error) {
    console.error('기간 재개 오류:', error)
    displayToast(error.message, 'error')
  }
}

const deletePeriod = async (period) => {
  if (
    !confirm(`"${period.period_name}" 기간을 삭제하시겠습니까?\n\n관련된 모든 데이터가 삭제됩니다.`)
  ) {
    return
  }

  try {
    const response = await fetch(`/api/phishing/admin/periods/${period.period_id}`, {
      method: 'DELETE',
      credentials: 'include',
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || '삭제에 실패했습니다.')
    }

    displayToast('기간이 삭제되었습니다.', 'success')
    await loadPeriodStatus()
  } catch (error) {
    console.error('기간 삭제 오류:', error)
    displayToast(error.message, 'error')
  }
}

// ===== 업로드 관리 =====
const openUploadModal = (period) => {
  selectedPeriod.value = period
  showBulkUploadModal.value = true
}

// ===== 상세 통계 =====
const viewDetailStats = (period) => {
  selectedPeriod.value = period
  showDetailStatsModal.value = true
}

// ===== 필터링 =====
const applyFilters = () => {
  let filtered = trainingRecords.value

  // 검색어 필터
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(
      (record) =>
        record.username?.toLowerCase().includes(query) ||
        record.department?.toLowerCase().includes(query) ||
        record.email?.toLowerCase().includes(query),
    )
  }

  filteredRecords.value = filtered
}

const searchTrainingData = () => {
  applyFilters()
}

// ===== 템플릿 다운로드 =====
const downloadTemplate = async () => {
  try {
    const response = await fetch('/api/phishing/admin/template/download', {
      credentials: 'include',
    })

    if (!response.ok) throw new Error('템플릿 다운로드 실패')

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = '피싱훈련_업로드_템플릿.csv'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)

    displayToast('템플릿이 다운로드되었습니다.', 'success')
  } catch (error) {
    console.error('템플릿 다운로드 오류:', error)
    displayToast('템플릿 다운로드에 실패했습니다.', 'error')
  }
}

/**
 * 기간 모달 닫기
 */
const closePeriodModal = () => {
  showPeriodModal.value = false
  editingPeriod.value = null
  saving.value = false

  // 폼 초기화
  periodForm.value = {
    training_year: selectedYear.value,
    period_name: '',
    training_type: '이메일 피싱',
    start_date: '',
    end_date: '',
    description: '',
    auto_pass_setting: true,
  }
}

const closeBulkUploadModal = () => {
  showBulkUploadModal.value = false
  selectedPeriod.value = null
}

const closeDetailStatsModal = () => {
  showDetailStatsModal.value = false
  selectedPeriod.value = null
}

// ===== 유틸리티 메서드 =====

/**
 * 최소 날짜 계산 (오늘 또는 과거 데이터 허용)
 */
const getMinDate = () => {
  // 과거 데이터도 입력할 수 있도록 1년 전부터 허용
  const oneYearAgo = new Date()
  oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1)
  return oneYearAgo.toISOString().split('T')[0]
}

/**
 * 기간 상태 텍스트 반환
 */
const getPeriodStatusText = (period) => {
  if (period.is_completed) return '완료됨'

  const today = new Date()
  const startDate = new Date(period.start_date)
  const endDate = new Date(period.end_date)

  if (today < startDate) return '예정됨'
  if (today >= startDate && today <= endDate) return '진행중'
  if (today > endDate) return '종료됨'

  return '설정됨'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  try {
    return new Date(dateString).toLocaleDateString('ko-KR')
  } catch {
    return dateString
  }
}

const formatDateRange = (startDate, endDate) => {
  const start = formatDate(startDate)
  const end = formatDate(endDate)
  return `${start} ~ ${end}`
}

const getTypeSuccessRate = (typeData) => {
  if (typeData.total_participants === 0) return 0
  return Math.round((typeData.total_success / typeData.total_participants) * 100)
}

const getRateClass = (rate) => {
  if (rate >= 90) return 'rate-excellent'
  if (rate >= 80) return 'rate-good'
  if (rate >= 70) return 'rate-warning'
  return 'rate-poor'
}

const getCardHeaderStatusClass = (status) => {
  const statusMap = {
    완료됨: 'card-status-completed',
    진행중: 'card-status-in-progress',
    예정됨: 'card-status-not-started',
    종료됨: 'card-status-expired',
    설정됨: 'card-status-default',
  }
  return statusMap[status] || 'card-status-unknown'
}

// ===== 알림 시스템 =====
const displayToast = (message, type = 'success') => {
  // 실제 구현에서는 toast 라이브러리 사용
  if (type === 'error') {
    alert(`오류: ${message}`)
  } else {
    alert(message)
  }
}

// ===== 감시자 =====
watch(selectedYear, () => {
  loadPeriodStatus()
  loadTrainingData()
})

watch([selectedTrainingType, selectedResult], () => {
  loadTrainingData()
})

// 시작일 변경 시 종료일 최소값 업데이트
watch(
  () => periodForm.value.start_date,
  (newStartDate) => {
    if (newStartDate && periodForm.value.end_date) {
      const startDate = new Date(newStartDate)
      const endDate = new Date(periodForm.value.end_date)

      // 종료일이 시작일보다 이전이면 시작일 다음날로 설정
      if (endDate <= startDate) {
        const nextDay = new Date(startDate)
        nextDay.setDate(nextDay.getDate() + 1)
        periodForm.value.end_date = nextDay.toISOString().split('T')[0]
      }
    }
  },
)

// 훈련 유형 변경 시 기간명 자동 제안
watch(
  () => periodForm.value.training_type,
  (newType) => {
    if (!editingPeriod.value && newType) {
      // 새 기간 생성 시에만 자동 제안
      const existingPeriods = []
      Object.values(periodStatus.value.training_types || {}).forEach((typeData) => {
        if (typeData.periods) {
          existingPeriods.push(...typeData.periods.filter((p) => p.training_type === newType))
        }
      })

      const nextNumber = existingPeriods.length + 1
      const suggestedName = `${nextNumber}차 ${newType} 훈련`

      if (!periodForm.value.period_name) {
        periodForm.value.period_name = suggestedName
      }
    }
  },
)
</script>

<style scoped>
@import '../styles/AdminPhishingTrainingManagement.css';
</style>
