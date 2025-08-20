<template>
  <div class="container">
    <div class="header">
      <h2>研究生成绩排名查询系统</h2>
    </div>

    <div class="links-container">
      <el-button type="primary" @click="goToRanking('total')">按总分排名</el-button>
      <el-button type="primary" @click="goToRanking('net')">按除政治后总分排名</el-button>
    </div>

    <!-- 桌面端表格视图 -->
    <div class="score-container desktop-only">
      <h3>考生信息</h3>
      <el-table 
        :data="[userInfo]" 
        border 
        style="width: 100%"
        :cell-style="{ textAlign: 'center' }"
        :header-cell-style="{ textAlign: 'center', backgroundColor: '#f5f7fa' }"
        class="score-table"
      >
        <el-table-column prop="kaohao" label="准考证号" min-width="120"></el-table-column>
        <el-table-column prop="college" label="学院" min-width="120"></el-table-column>
        <el-table-column prop="major" label="专业" min-width="120"></el-table-column>
        <el-table-column :prop="'subject1_code'" :label="userInfo.subject1_code" min-width="100"></el-table-column>
        <el-table-column :prop="'subject2_code'" :label="userInfo.subject2_code" min-width="100"></el-table-column>
        <el-table-column :prop="'subject3_code'" :label="userInfo.subject3_code" min-width="100"></el-table-column>
        <el-table-column :prop="'subject4_code'" :label="userInfo.subject4_code" min-width="100"></el-table-column>
        <el-table-column prop="net_score" label="除政治后总分" min-width="120"></el-table-column>
        <el-table-column prop="total_score" label="总分" min-width="100"></el-table-column>
      </el-table>
    </div>

    <!-- 移动端卡片视图 -->
    <div class="score-container mobile-only">
      <div class="score-cards">
        <!-- 基本信息卡片 -->
        <div class="score-card">
          <div class="card-header">
            <i class="el-icon-user"></i>
            <span>基本信息</span>
          </div>
          <div class="card-body">
            <div class="info-item">
              <span class="info-label">准考证号</span>
              <span class="info-value">{{ userInfo.kaohao }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">学院</span>
              <span class="info-value">{{ userInfo.college }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">专业</span>
              <span class="info-value">{{ userInfo.major }}</span>
            </div>
          </div>
        </div>

        <!-- 总分卡片 -->
        <div class="score-card total-score-card">
          <div class="card-header">
            <i class="el-icon-trophy"></i>
            <span>总分</span>
          </div>
          <div class="card-body">
            <div class="total-score-display">
              <span class="total-score-value">{{ userInfo.total_score }}</span>
              <span class="total-score-label">分</span>
            </div>
            <div class="net-score-display">
              <span class="net-score-label">除政治后总分:</span>
              <span class="net-score-value">{{ userInfo.net_score }}</span>
            </div>
          </div>
        </div>

        <!-- 科目成绩卡片 -->
        <div class="score-card">
          <div class="card-header">
            <i class="el-icon-document"></i>
            <span>科目成绩</span>
          </div>
          <div class="card-body">
            <div class="subject-item">
              <span class="subject-name">{{ userInfo.subject1_code }}</span>
              <span class="subject-score">{{ userInfo.subject1_score }}</span>
            </div>
            <div class="subject-item">
              <span class="subject-name">{{ userInfo.subject2_code }}</span>
              <span class="subject-score">{{ userInfo.subject2_score }}</span>
            </div>
            <div class="subject-item">
              <span class="subject-name">{{ userInfo.subject3_code }}</span>
              <span class="subject-score">{{ userInfo.subject3_score }}</span>
            </div>
            <div class="subject-item">
              <span class="subject-name">{{ userInfo.subject4_code }}</span>
              <span class="subject-score">{{ userInfo.subject4_score }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="common-rankings">
      <h3>常用排名</h3>
      <div class="ranking-links">
        <div class="ranking-row">
          <span class="ranking-label">总分排名:</span>
          <el-link type="primary" @click="goToSpecificRanking('total', '225软件学院', '085400电子信息')">软件学院专硕</el-link>
          <el-link type="primary" @click="goToSpecificRanking('total', '225软件学院', '083500软件工程')">软件学院学硕</el-link>
          <el-link type="primary" @click="goToSpecificRanking('total', '215计算机科学与技术学院', '085400电子信息')">计院专硕</el-link>
          <el-link type="primary" @click="goToSpecificRanking('total', '215计算机科学与技术学院', '081200计算机科学与技术')">计院学硕</el-link>
          <el-link type="primary" @click="goToSpecificRanking('total', '218先进技术研究院', '085400电子信息')">先进院专硕</el-link>
          <el-link type="primary" @click="goToSpecificRanking('total', '168研究生院科学岛分院', '085400电子信息')">科学岛专硕</el-link>
        </div>
        <div class="ranking-row">
          <span class="ranking-label">净分排名:</span>
          <el-link type="primary" @click="goToSpecificRanking('net', '225软件学院', '085400电子信息')">软件学院专硕</el-link>
          <el-link type="primary" @click="goToSpecificRanking('net', '225软件学院', '083500软件工程')">软件学院学硕</el-link>
          <el-link type="primary" @click="goToSpecificRanking('net', '215计算机科学与技术学院', '085400电子信息')">计院专硕</el-link>
          <el-link type="primary" @click="goToSpecificRanking('net', '215计算机科学与技术学院', '081200计算机科学与技术')">计院学硕</el-link>
          <el-link type="primary" @click="goToSpecificRanking('net', '218先进技术研究院', '085400电子信息')">先进院专硕</el-link>
          <el-link type="primary" @click="goToSpecificRanking('net', '168研究生院科学岛分院', '085400电子信息')">科学岛专硕</el-link>
        </div>
      </div>
    </div>

    <div class="actions">
      <el-button type="warning" @click="goToResetPassword">修改密码</el-button>
      <el-button type="danger" @click="logout">退出登录</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { userApi } from '@/api'

const router = useRouter()
const userInfo = ref({
  kaohao: '',
  college: '',
  major: '',
  subject1_code: '',
  subject1_score: 0,
  subject2_code: '',
  subject2_score: 0,
  subject3_code: '',
  subject3_score: 0,
  subject4_code: '',
  subject4_score: 0,
  net_score: 0,
  total_score: 0
})

onMounted(async () => {
  try {
    const response = await userApi.getScore()
    userInfo.value = response.user
  } catch (error) {
    ElMessage.error('获取成绩信息失败，请重新登录')
    router.push('/')
  }
})

const goToRanking = (type) => {
  const params = {
    college: userInfo.value.college,
    major: userInfo.value.major,
    type
  }
  router.push({
    name: 'Ranking',
    query: params
  })
}

const goToSpecificRanking = (type, college, major) => {
  const params = {
    college,
    major,
    type
  }
  router.push({
    name: 'Ranking',
    query: params
  })
}

const goToResetPassword = () => {
  router.push('/reset-password')
}

const logout = async () => {
  try {
    await userApi.logout()
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    ElMessage.success('已安全退出登录')
    router.push('/')
  } catch (error) {
    ElMessage.error('退出登录失败')
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

.links-container {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
  gap: 10px;
}

.score-container {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.score-table {
  margin-top: 15px;
}

.common-rankings {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.ranking-links {
  margin-top: 15px;
}

.ranking-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 10px;
}

.ranking-label {
  font-weight: bold;
  margin-right: 10px;
  min-width: 80px;
}

.el-link {
  margin-right: 15px;
  margin-bottom: 5px;
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

/* 移动端卡片样式 */
.score-cards {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.score-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
  font-weight: bold;
  font-size: 16px;
}

.card-header i {
  margin-right: 8px;
  color: #409EFF;
}

.card-body {
  padding: 15px;
}

.info-item, .subject-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #ebeef5;
}

.info-item:last-child, .subject-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.info-label, .subject-name {
  color: #606266;
}

.info-value, .subject-score {
  font-weight: bold;
}

.total-score-card .card-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 15px;
}

.total-score-display {
  display: flex;
  align-items: baseline;
  margin-bottom: 15px;
}

.total-score-value {
  font-size: 36px;
  font-weight: bold;
  color: #f56c6c;
}

.total-score-label {
  font-size: 16px;
  margin-left: 5px;
}

.net-score-display {
  display: flex;
  align-items: center;
}

.net-score-label {
  margin-right: 5px;
  color: #606266;
}

.net-score-value {
  font-weight: bold;
  color: #409EFF;
}

@media screen and (max-width: 768px) {
  .desktop-only {
    display: none;
  }
  
  .mobile-only {
    display: block;
  }
  
  .score-container, .common-rankings {
    padding: 15px;
  }
  
  .ranking-row {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .ranking-label {
    margin-bottom: 10px;
  }
  
  .el-link {
    margin-bottom: 10px;
  }
  
  .links-container {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
    padding: 0 15px;
  }
  
  .links-container .el-button {
    width: 100%;
    margin-left: 0 !important;
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
}
</style>