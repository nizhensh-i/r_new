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
      <h3 class="title">登录</h3>
      <el-form 
        ref="formRef" 
        :model="loginForm" 
        :rules="loginRules" 
        label-width="auto"
        class="login-form"
      >
        <el-form-item label="准考证号" prop="kaohao">
          <el-input v-model="loginForm.kaohao" placeholder="请输入准考证号"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" show-password></el-input>
        </el-form-item>
        <el-form-item >
          <el-checkbox v-model="rememberMe">记住账号密码</el-checkbox>
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { userApi } from '@/api'
import CryptoJS from 'crypto-js'

const router = useRouter()
const loginForm = reactive({
  kaohao: '',
  password: ''
})
const rememberMe = ref(false)

// 加密密钥，实际应用中应该使用更安全的方式存储
const SECRET_KEY = 'rank_system_secret_key'

// 加密函数
const encrypt = (text) => {
  return CryptoJS.AES.encrypt(text, SECRET_KEY).toString()
}

// 解密函数
const decrypt = (ciphertext) => {
  const bytes = CryptoJS.AES.decrypt(ciphertext, SECRET_KEY)
  return bytes.toString(CryptoJS.enc.Utf8)
}

// 页面加载时检查是否有保存的账号密码
onMounted(() => {
  console.log('')
  const savedCredentials = localStorage.getItem('savedCredentials')
  if (savedCredentials) {
    try {
      const decrypted = decrypt(savedCredentials)
      const credentials = JSON.parse(decrypted)
      loginForm.kaohao = credentials.kaohao
      loginForm.password = credentials.password
      rememberMe.value = true
    } catch (error) {
      console.error('解密保存的凭证失败', error)
      // 如果解密失败，清除保存的凭证
      localStorage.removeItem('savedCredentials')
    }
  }
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
        
        // 如果选择了记住账号密码，则保存到本地存储
        if (rememberMe.value) {
          const credentials = {
            kaohao: loginForm.kaohao,
            password: loginForm.password
          }
          const encrypted = encrypt(JSON.stringify(credentials))
          localStorage.setItem('savedCredentials', encrypted)
        } else {
          // 如果取消了记住账号密码，则清除本地存储
          localStorage.removeItem('savedCredentials')
        }
        
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
.title {
  text-align: center;
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
  
  /* 修复移动端按钮对齐问题 */
  /* .el-form-item .el-form-item__content {
    display: flex;
    flex-direction: column;
    align-items: stretch;
  } */
  
  .el-form-item .el-button {
    margin-left: 0 !important;
    margin-top: 10px;
    width: 100%;
  }
  
  .el-form-item .el-button:first-child {
    margin-top: 0;
  }
}
</style>