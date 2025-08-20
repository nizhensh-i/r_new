<template>
  <div class="container">
    <div class="header">
      <h2>研究生成绩排名查询系统</h2>
      <h3>{{ college }} {{ major }} {{ isTotal ? '按总分排名' : '按除政治后总分排名' }}</h3>
    </div>

    <!-- 桌面端表格视图 -->
    <div class="ranking-container desktop-only">
      <el-table 
        :data="rankingData" 
        border 
        style="width: 100%"
        :cell-style="getCellStyle"
        :header-cell-style="{ textAlign: 'center', backgroundColor: '#f5f7fa' }"
        class="ranking-table"
      >
        <el-table-column prop="rank" label="排名" width="80"></el-table-column>
        <el-table-column prop="kaohao" label="准考证号" min-width="120"></el-table-column>
        <el-table-column prop="total_score" label="总分" width="80"></el-table-column>
        <el-table-column :prop="'subject1_score'" :label="subjectLabels.subject1_code" width="100"></el-table-column>
        <el-table-column :prop="'subject2_score'" :label="subjectLabels.subject2_code" width="100"></el-table-column>
        <el-table-column :prop="'subject3_score'" :label="subjectLabels.subject3_code" width="100"></el-table-column>
        <el-table-column :prop="'subject4_score'" :label="subjectLabels.subject4_code" width="100"></el-table-column>
        <el-table-column v-if="!isTotal" prop="net_score" label="除政治后总分" width="120"></el-table-column>
      </el-table>
    </div>

    <!-- 移动端优化表格视图 -->
    <div class="ranking-container mobile-only">
      <div class="mobile-table-container">
        <div class="mobile-table-wrapper">
          <table class="mobile-table">
            <thead>
              <tr>
                <th class="fixed-column rank-th">排名</th>
                <th class="fixed-column score-th">总分</th>
                <th class="scrollable-columns">
                  <div class="scrollable-header">
                    <span v-if="!isTotal" class="header-cell">除政治</span>
                    <span class="header-cell">{{ subjectLabels.subject1_code }}</span>
                    <span class="header-cell">{{ subjectLabels.subject2_code }}</span>
                    <span class="header-cell">{{ subjectLabels.subject3_code }}</span>
                    <span class="header-cell">{{ subjectLabels.subject4_code }}</span>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="(item, index) in rankingData" 
                :key="index"
                :class="{ 'current-user-row': currentUser && item.kaohao === currentUser.kaohao }"
              >
                <td class="fixed-column rank-cell">
                  <span class="rank-number">{{ item.rank }}</span>
                  <span class="kaohao-mini">{{ item.kaohao.substring(0, 6) }}...</span>
                </td>
                <td class="fixed-column total-score-cell">{{ item.total_score }}</td>
                <td class="scrollable-columns">
                  <div class="scrollable-data">
                    <span v-if="!isTotal" class="data-cell">{{ item.net_score }}</span>
                    <span class="data-cell">{{ item.subject1_score }}</span>
                    <span class="data-cell">{{ item.subject2_score }}</span>
                    <span class="data-cell">{{ item.subject3_score }}</span>
                    <span class="data-cell">{{ item.subject4_score }}</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="scroll-hint">← 左右滑动查看更多科目分数 →</div>
      </div>
      
      <!-- 表格/卡片切换按钮 -->
      <div class="view-toggle">
        <el-button size="small" @click="toggleViewMode">
          {{ isCardView ? '切换到表格视图' : '切换到卡片视图' }}
        </el-button>
      </div>
      
      <!-- 卡片视图（可选切换） -->
      <div v-if="isCardView" class="card-view">
        <div 
          v-for="(item, index) in rankingData" 
          :key="index" 
          class="ranking-card"
          :class="{ 'current-user-card': currentUser && item.kaohao === currentUser.kaohao }"
        >
          <div class="ranking-card-header">
            <span class="rank-badge">{{ item.rank }}</span>
            <span class="kaohao">{{ item.kaohao }}</span>
            <span class="total-score">总分: {{ item.total_score }}</span>
          </div>
          <div class="ranking-card-body">
            <div class="score-item">
              <span class="subject-name">{{ subjectLabels.subject1_code }}</span>
              <span class="subject-score">{{ item.subject1_score }}</span>
            </div>
            <div class="score-item">
              <span class="subject-name">{{ subjectLabels.subject2_code }}</span>
              <span class="subject-score">{{ item.subject2_score }}</span>
            </div>
            <div class="score-item">
              <span class="subject-name">{{ subjectLabels.subject3_code }}</span>
              <span class="subject-score">{{ item.subject3_score }}</span>
            </div>
            <div class="score-item">
              <span class="subject-name">{{ subjectLabels.subject4_code }}</span>
              <span class="subject-score">{{ item.subject4_score }}</span>
            </div>
            <div v-if="!isTotal" class="score-item">
              <span class="subject-name">除政治后总分</span>
              <span class="subject-score">{{ item.net_score }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="pagination-container">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="total"
          :page-size="pageSize"
          :pager-count="5"
          :current-page="currentPage"
          @current-change="handlePageChange"
        ></el-pagination>
      </div>
    </div>

    <div class="actions">
      <el-button @click="goBack">返回个人成绩</el-button>
      <el-button type="primary" @click="toggleRankingType">切换到{{ isTotal ? '除政治后总分' : '总分' }}排名</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { rankingApi } from '@/api'

const router = useRouter()
const route = useRoute()

const college = ref('')
const major = ref('')
const rankingType = ref('')
const rankingData = ref([])
const currentPage = ref(1)
const pageSize = ref(100)
const total = ref(0)
const currentUser = ref(null)
const isCardView = ref(false) // 默认使用表格视图
const subjectLabels = ref({
  subject1_code: '科目1',
  subject2_code: '科目2',
  subject3_code: '科目3',
  subject4_code: '科目4'
})

// 判断是按总分排名还是按除政治后总分排名
const isTotal = computed(() => rankingType.value === 'total')

// 从路由参数中获取排名类型和学院专业信息
onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    currentUser.value = JSON.parse(userStr)
    
    // 设置科目名称
    if (currentUser.value) {
      subjectLabels.value = {
        subject1_code: currentUser.value.subject1_code || '科目1',
        subject2_code: currentUser.value.subject2_code || '科目2',
        subject3_code: currentUser.value.subject3_code || '科目3',
        subject4_code: currentUser.value.subject4_code || '科目4'
      }
    }
  }
  
  const { type, college: routeCollege, major: routeMajor } = route.query
  
  rankingType.value = type || 'total'
  college.value = routeCollege || (currentUser.value ? currentUser.value.college : '')
  major.value = routeMajor || (currentUser.value ? currentUser.value.major : '')
  
  // 检测屏幕宽度，在小屏幕上默认使用表格视图
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
  
  fetchRankingData()
})

// 监听路由参数变化，重新获取排名数据
watch(() => route.query, (newQuery) => {
  const { type, college: routeCollege, major: routeMajor } = newQuery
  
  if (type) rankingType.value = type
  if (routeCollege) college.value = routeCollege
  if (routeMajor) major.value = routeMajor
  
  currentPage.value = 1
  fetchRankingData()
}, { deep: true })

// 获取排名数据
const fetchRankingData = async () => {
  if (!college.value || !major.value) {
    ElMessage.error('缺少学院或专业信息')
    return
  }
  
  try {
    let response
    if (isTotal.value) {
      response = await rankingApi.getRankingByTotal(college.value, major.value, currentPage.value)
    } else {
      response = await rankingApi.getRankingByNet(college.value, major.value, currentPage.value)
    }
    
    rankingData.value = response.users.map((user, index) => {
      return {
        ...user,
        rank: (currentPage.value - 1) * pageSize.value + index + 1
      }
    })
    
    total.value = response.total
  } catch (error) {
    ElMessage.error('获取排名数据失败')
  }
}

// 处理分页变化
const handlePageChange = (page) => {
  currentPage.value = page
  fetchRankingData()
}

// 切换排名类型
const toggleRankingType = () => {
  rankingType.value = isTotal.value ? 'net' : 'total'
  currentPage.value = 1
  
  router.push({
    query: {
      ...route.query,
      type: rankingType.value
    }
  })
}

// 返回个人成绩页面
const goBack = () => {
  router.push('/score')
}

// 设置单元格样式，高亮当前用户
const getCellStyle = ({ row }) => {
  if (currentUser.value && row.kaohao === currentUser.value.kaohao) {
    return {
      backgroundColor: '#e6f7ff',
      textAlign: 'center'
    }
  }
  return {
    textAlign: 'center'
  }
}

// 检测屏幕宽度，在小屏幕上默认使用表格视图
const checkScreenSize = () => {
  // 在小屏幕上默认使用表格视图，因为我们已经优化了表格
  isCardView.value = false
}

// 切换视图模式
const toggleViewMode = () => {
  isCardView.value = !isCardView.value
}
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 20px;
}

.ranking-container {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.ranking-table {
  margin-top: 15px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 10px;
}

/* 桌面端和移动端视图切换 */
.desktop-only {
  display: block;
}

.mobile-only {
  display: none;
}

/* 移动端表格样式 */
.mobile-table-container {
  position: relative;
  margin-bottom: 15px;
}

.mobile-table-wrapper {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.mobile-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.mobile-table th,
.mobile-table td {
  padding: 10px;
  text-align: center;
  border: 1px solid #ebeef5;
}

.fixed-column {
  position: sticky;
  left: 0;
  z-index: 2;
  background-color: #fff;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
}

.rank-th, .score-th {
  width: 70px;
}

.scrollable-columns {
  padding: 0 !important;
}

.scrollable-header, .scrollable-data {
  display: flex;
  min-width: 400px; /* 确保有足够的宽度可以滚动 */
}

.header-cell, .data-cell {
  flex: 1;
  min-width: 80px;
  padding: 10px;
  text-align: center;
  border-right: 1px solid #ebeef5;
}

.header-cell:last-child, .data-cell:last-child {
  border-right: none;
}

.rank-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.rank-number {
  font-weight: bold;
  font-size: 16px;
  color: #409EFF;
}

.kaohao-mini {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.total-score-cell {
  font-weight: bold;
  color: #f56c6c;
}

.scroll-hint {
  text-align: center;
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}

.view-toggle {
  display: flex;
  justify-content: center;
  margin: 15px 0;
}

/* 当前用户高亮 */
.current-user-row {
  background-color: #ecf5ff !important;
}

/* 移动端卡片样式 */
.ranking-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 15px;
  overflow: hidden;
}

.current-user-card {
  border: 2px solid #409EFF;
  background-color: #ecf5ff;
}

.ranking-card-header {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
}

.rank-badge {
  background-color: #409EFF;
  color: white;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 10px;
}

.kaohao {
  flex: 1;
  font-size: 14px;
}

.total-score {
  font-weight: bold;
  color: #f56c6c;
  font-size: 16px;
}

.ranking-card-body {
  padding: 12px 15px;
}

.score-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #ebeef5;
}

.score-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.subject-name {
  color: #606266;
}

.subject-score {
  font-weight: bold;
}

@media screen and (max-width: 768px) {
  .desktop-only {
    display: none;
  }
  
  .mobile-only {
    display: block;
  }
  
  .ranking-container {
    padding: 15px;
  }
  
  .actions {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
    padding: 0 15px;
  }
  
  .actions .el-button {
    width: 100%;
    margin-left: 0 !important;
  }
  
  .pagination-container .el-pagination {
    justify-content: center;
    flex-wrap: wrap;
  }
}
</style>