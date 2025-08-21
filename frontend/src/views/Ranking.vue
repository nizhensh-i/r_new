<template>
  <div class="container">
    <div class="header mobile-optimized">
      <h3 class="system-title">研究生成绩排名查询系统</h3>
      <h4 class="ranking-info">{{ college }} {{ major }} {{ isTotal ? '按总分排名' : '按除政治后总分排名' }}</h4>
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
        v-loading="loading"
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
      
      <div class="pagination-container">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :total="total"
          :page-size="pageSize"
          :pager-count="5"
          :current-page="currentPage"
          @current-change="handlePageChange"
        ></el-pagination>
      </div>
    </div>

    <!-- 移动端优化表格视图 -->
    <div class="ranking-container mobile-only">
      <div class="mobile-table-container">
        <el-table
          :data="rankingData"
          :row-class-name="getRowClassName"
          :header-cell-style="{padding: '0px'}"
          @row-click="showKaohaoDetail"
          :height="tableHeight"
          v-loading="loading"
          class="mobile-el-table"
        >
          <!-- 固定列 -->
          <el-table-column fixed prop="rank" label="排名" width="50" />
          <el-table-column 
            fixed 
            label="考号" 
            width="100"
            :show-overflow-tooltip="true"
          >
            <template #default="{ row }">
              <span class="kaohao-mini">...{{ row.kaohao.slice(-4) }}</span>
            </template>
          </el-table-column>
          <el-table-column fixed prop="total_score" label="总分" width="50" />
          
          <!-- 可滚动列 -->
          <el-table-column v-if="!isTotal" prop="net_score" label="除政治后总分" width="60" />
          <el-table-column :prop="'subject1_score'" :label="subjectLabels.subject1_code" width="60" />
          <el-table-column :prop="'subject2_score'" :label="subjectLabels.subject2_code" width="50" />
          <el-table-column :prop="'subject3_score'" :label="subjectLabels.subject3_code" width="50" />
          <el-table-column :prop="'subject4_score'" :label="subjectLabels.subject4_code" width="60" />
        </el-table>
        <div class="scroll-hint">← 左右滑动查看更多科目分数 →</div>
      </div>

      <div class="pagination-container">
        <el-pagination
          background
         layout="prev, pager, next"
          :total="total"
          :page-size="pageSize"
          :pager-count="4"
          :current-page="currentPage"
          @current-change="handlePageChange"
        ></el-pagination>
      </div>
    </div>

    <div class="actions">
      <el-button @click="goBack">返回个人成绩</el-button>
      <el-button type="primary" @click="toggleRankingType">切换到{{ isTotal ? '除政治后总分' : '总分' }}排名</el-button>
    </div>
    
    <!-- 考号详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="考生详情"
      width="90%"
      center
      align-center
      destroy-on-close
      class="kaohao-detail-dialog"
    >
      <div v-if="selectedItem" class="detail-content">
        <div class="detail-header">
          <div class="detail-rank">排名: <span>{{ selectedItem.rank }}</span></div>
          <div class="detail-kaohao">考号: <span>{{ selectedItem.kaohao }}</span></div>
        </div>
        
        <div class="detail-scores">
          <div class="detail-score-item">
            <div class="score-label">总分</div>
            <div class="score-value highlight">{{ selectedItem.total_score }}</div>
          </div>
          <div v-if="!isTotal" class="detail-score-item">
            <div class="score-label">除政治后总分</div>
            <div class="score-value">{{ selectedItem.net_score }}</div>
          </div>
          <div class="detail-score-item">
            <div class="score-label">{{ subjectLabels.subject1_code }}</div>
            <div class="score-value">{{ selectedItem.subject1_score }}</div>
          </div>
          <div class="detail-score-item">
            <div class="score-label">{{ subjectLabels.subject2_code }}</div>
            <div class="score-value">{{ selectedItem.subject2_score }}</div>
          </div>
          <div class="detail-score-item">
            <div class="score-label">{{ subjectLabels.subject3_code }}</div>
            <div class="score-value">{{ selectedItem.subject3_score }}</div>
          </div>
          <div class="detail-score-item">
            <div class="score-label">{{ subjectLabels.subject4_code }}</div>
            <div class="score-value">{{ selectedItem.subject4_score }}</div>
          </div>
        </div>
        
        <div class="detail-compare" v-if="currentUser && selectedItem.kaohao !== currentUser.kaohao">
          <h4>与我的成绩对比</h4>
          <div class="compare-item">
            <div class="compare-label">总分差距</div>
            <div class="compare-value" :class="getCompareClass(selectedItem.total_score, currentUser.total_score)">
              {{ getScoreDiff(selectedItem.total_score, currentUser.total_score) }}
            </div>
          </div>
          <div v-if="!isTotal" class="compare-item">
            <div class="compare-label">除政治后总分差距</div>
            <div class="compare-value" :class="getCompareClass(selectedItem.net_score, currentUser.net_score)">
              {{ getScoreDiff(selectedItem.net_score, currentUser.net_score) }}
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
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
const hoveredKaohao = ref('') // 用于跟踪当前悬停的考号
const selectedItem = ref(null) // 用于存储当前选中的项目
const showDetailDialog = ref(false) // 控制详情对话框的显示
const loading = ref(false) // 控制加载状态
const subjectLabels = ref({
  subject1_code: '科目1',
  subject2_code: '科目2',
  subject3_code: '科目3',
  subject4_code: '科目4'
})

// 动态计算表格高度
const tableHeight = ref('calc(100vh - 200px)')

// 判断是按总分排名还是按除政治后总分排名
const isTotal = computed(() => rankingType.value === 'total')

// 从路由参数中获取排名类型和学院专业信息
onMounted(() => {
  // 计算表格高度
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
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
  
  // 检测屏幕宽度
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
  
  loading.value = true
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
    console.error('获取排名数据失败:', error)
  } finally {
    loading.value = false
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

// 获取行的类名，用于高亮当前用户
const getRowClassName = ({ row }) => {
  if (currentUser.value && row.kaohao === currentUser.value.kaohao) {
    return 'current-user-row'
  }
  return ''
}

// 检测屏幕宽度
const checkScreenSize = () => {
  // 屏幕大小变化时重新计算表格高度
  calculateTableHeight()
}

// 计算表格高度
const calculateTableHeight = () => {
  // 获取视口高度
  const viewportHeight = window.innerHeight
  // 计算其他元素的高度总和（标题、分页、按钮等）
  const otherElementsHeight = 180 // 根据实际情况调整
  // 设置表格高度
  tableHeight.value = `${viewportHeight - otherElementsHeight - 55}px`
}

// 显示考号详情
const showKaohaoDetail = (row) => {
  selectedItem.value = row
  showDetailDialog.value = true
}

// 计算分数差距
const getScoreDiff = (score1, score2) => {
  const diff = score1 - score2
  return diff > 0 ? `+${diff}` : diff.toString()
}

// 获取比较样式类
const getCompareClass = (score1, score2) => {
  const diff = score1 - score2
  if (diff > 0) return 'better'
  if (diff < 0) return 'worse'
  return 'equal'
}
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 15px;
}

.header {
  text-align: center;
}

.header.mobile-optimized .system-title {
  font-size: 1.2rem;
  margin-bottom: 5px;
  margin-top: 0;
}

.header.mobile-optimized .ranking-info {
  font-size: 0.9rem;
  margin-top: 0;
  margin-bottom: 10px;
}

.ranking-container {
  background-color: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 5px;
}

.ranking-table {
  margin-top: 15px;
}

.pagination-container {
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
  margin-bottom: 10px;
}

.mobile-el-table {
  margin-bottom: 10px;
}

.mobile-el-table :deep(.el-table__body tr.current-user-row > td) {
  background-color: #ecf5ff !important;
}

.mobile-el-table :deep(.el-table__fixed) {
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
}

.mobile-el-table :deep(.el-table__header th) {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: bold;
  padding: 8px 0;
}

.mobile-el-table :deep(.el-table__row) {
  cursor: pointer;
}

.mobile-el-table :deep(.el-table__row:hover > td) {
  background-color: #f5f7fa;
}

.kaohao-mini {
  font-size: 13px;
  color: #606266;
  margin-right: 5px;
}

.info-icon {
  font-size: 14px;
  color: #909399;
  cursor: pointer;
  vertical-align: middle;
}

.info-icon:hover {
  color: #409EFF;
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

/* 当前用户高亮 */
.current-user-row td {
  background-color: #ecf5ff !important;
}

/* 详情对话框样式 */
.detail-content {
  padding: 10px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.detail-rank, .detail-kaohao {
  font-size: 16px;
}

.detail-rank span, .detail-kaohao span {
  font-weight: bold;
  color: #409EFF;
}

.detail-scores {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.detail-score-item {
  background-color: #f5f7fa;
  border-radius: 6px;
  padding: 12px;
  text-align: center;
}

.score-label {
  color: #606266;
  margin-bottom: 8px;
}

.score-value {
  font-size: 18px;
  font-weight: bold;
}

.score-value.highlight {
  color: #f56c6c;
  font-size: 20px;
}

.detail-compare {
  background-color: #f0f9eb;
  border-radius: 6px;
  padding: 15px;
  margin-top: 20px;
}

.detail-compare h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #67c23a;
}

.compare-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.compare-value {
  font-weight: bold;
}

.compare-value.better {
  color: #f56c6c;
}

.compare-value.worse {
  color: #67c23a;
}

.compare-value.equal {
  color: #909399;
}

@media screen and (max-width: 768px) {
  .desktop-only {
    display: none;
  }
  
  .mobile-only {
    display: block;
  }
  
  .ranking-container {
    padding: 10px;
  }
  
  .container {
    padding: 10px;
  }
  
  .actions {
    flex-direction: column;
    gap: 5px;
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
  
  .detail-scores {
    grid-template-columns: 1fr;
  }
  
  /* 让表格行在移动端可点击 */
  .mobile-table tbody tr {
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .mobile-table tbody tr:hover {
    background-color: #f5f7fa;
  }
  
  .mobile-table tbody tr:active {
    background-color: #e6f7ff;
  }
}
</style>