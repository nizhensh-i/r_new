<template>
  <div class="container">
    <div class="header">
      <h2>研究生成绩排名查询系统</h2>
      <h3>{{ college }} {{ major }} {{ isTotal ? '按总分排名' : '按除政治后总分排名' }}</h3>
    </div>

    <div class="ranking-container">
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

      <div class="pagination-container">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="total"
          :page-size="pageSize"
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

@media screen and (max-width: 768px) {
  .ranking-container {
    padding: 15px;
    overflow-x: auto;
  }
  
  .ranking-table {
    min-width: 600px;
  }
}
</style>