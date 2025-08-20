<template>
  <div class="container">
    <div class="header">
      <h2>研究生成绩排名查询系统</h2>
    </div>

    <div class="links-container">
      <el-button type="primary" @click="goToRanking('total')">按总分排名</el-button>
      <el-button type="primary" @click="goToRanking('net')">按除政治后总分排名</el-button>
    </div>

    <div class="score-container">
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

@media screen and (max-width: 768px) {
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
  
  .score-table {
    width: 100%;
    overflow-x: auto;
  }
}
</style>