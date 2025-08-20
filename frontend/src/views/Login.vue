<template>
  <div class="container">
    <div class="header">
      <h2>研究生成绩排名查询系统</h2>
      <p>1. 网站仅保存准考证号，所报学院专业及分数情况，请不要担心隐私泄露</p>
      <p>2. 报考的所有同学均可登录查分，查分后可查看本专业排名，人数越多，数据越准确</p>
      <p>3. <span class="warning">本网站数据为考生所有，未经书面许可，任何人不得以任何方式盗用转载相关数据</span></p>
      <p>4. 仅供学习交流使用，使用造成的一切不良后果由用户承担，与作者无关</p>
    </div>

    <div class="form-container">
      <h3>登录</h3>
      <el-form 
        ref="loginForm" 
        :model="loginForm" 
        :rules="loginRules" 
        label-width="100px"
        class="login-form"
      >
        <el-form-item label="准考证号" prop="kaohao">
          <el-input v-model="loginForm.kaohao" placeholder="请输入准考证号"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm">登录</el-button>
          <el-button @click="goToRegister">注册查分</el-button>
          <el-button @click="goToResetPassword">找回密码</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { userApi } from '@/api'

const router = useRouter()
const loginForm = reactive({
  kaohao: '',
  password: ''
})

const loginRules = {
  kaohao: [
    { required: true, message: '请输入准考证号', trigger: 'blur' },
    { min: 15, max: 15, message: '准考证号长度必须为15位', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度必须在6-20位之间', trigger: 'blur' }
  ]
}

const formRef = ref(null)

const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const response = await userApi.login(loginForm)
        localStorage.setItem('token', response.token)
        localStorage.setItem('user', JSON.stringify(response.user))
        ElMessage.success('登录成功')
        router.push('/score')
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '登录失败，请检查准考证号和密码')
      }
    }
  })
}

const goToRegister = () => {
  router.push('/register')
}

const goToResetPassword = () => {
  router.push('/reset-password')
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
  margin-bottom: 30px;
}

.warning {
  color: red;
  font-size: 16px;
  font-weight: bold;
}

.form-container {
  max-width: 500px;
  margin: 0 auto;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-form {
  margin-top: 20px;
}

@media screen and (max-width: 768px) {
  .form-container {
    max-width: 100%;
    padding: 15px;
  }
  
  .el-form-item {
    margin-bottom: 15px;
  }
}
</style>