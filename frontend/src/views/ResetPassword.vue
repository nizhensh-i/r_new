<template>
  <div class="container">
    <div class="header">
      <h2>研究生成绩排名查询系统</h2>
    </div>

    <div class="form-container">
      <h3>{{ isLoggedIn ? '修改密码' : '找回密码' }}</h3>
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="120px"
        class="reset-form"
      >
        <template v-if="!isLoggedIn">
          <el-form-item label="准考证号" prop="kaohao">
            <el-input v-model="form.kaohao" placeholder="请输入准考证号"></el-input>
          </el-form-item>
          <el-form-item label="考生姓名" prop="name">
            <el-input v-model="form.name" placeholder="请输入姓名"></el-input>
          </el-form-item>
          <el-form-item label="身份证号" prop="id">
            <el-input v-model="form.id" placeholder="请输入身份证号"></el-input>
          </el-form-item>
          <el-form-item label="验证码" prop="code">
            <div class="captcha-container">
              <el-input v-model="form.code" placeholder="请输入验证码"></el-input>
              <img :src="captchaUrl" @click="refreshCaptcha" class="captcha-img" alt="验证码">
            </div>
          </el-form-item>
        </template>
        <el-form-item label="新密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入新密码"></el-input>
        </el-form-item>
        <el-form-item label="确认新密码" prop="password2">
          <el-input v-model="form.password2" type="password" placeholder="请再次输入新密码"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm">{{ isLoggedIn ? '修改密码' : '重置密码' }}</el-button>
          <el-button @click="goToLogin">返回登录</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { userApi } from '@/api'

const router = useRouter()
const formRef = ref(null)
const captchaUrl = ref('')

// 判断是否已登录
const isLoggedIn = computed(() => {
  return localStorage.getItem('token') !== null
})

const form = reactive({
  kaohao: '',
  name: '',
  id: '',
  code: '',
  password: '',
  password2: ''
})

// 根据登录状态动态设置验证规则
const rules = computed(() => {
  const baseRules = {
    password: [
      { required: true, message: '请输入新密码', trigger: 'blur' },
      { min: 6, max: 20, message: '密码长度必须在6-20位之间', trigger: 'blur' }
    ],
    password2: [
      { required: true, message: '请再次输入新密码', trigger: 'blur' },
      { min: 6, max: 20, message: '密码长度必须在6-20位之间', trigger: 'blur' },
      { 
        validator: (rule, value, callback) => {
          if (value !== form.password) {
            callback(new Error('两次输入的密码不一致'))
          } else {
            callback()
          }
        }, 
        trigger: 'blur' 
      }
    ]
  }

  // 如果未登录，添加额外的验证规则
  if (!isLoggedIn.value) {
    return {
      ...baseRules,
      kaohao: [
        { required: true, message: '请输入准考证号', trigger: 'blur' },
        { min: 15, max: 15, message: '准考证号长度必须为15位', trigger: 'blur' }
      ],
      name: [
        { required: true, message: '请输入姓名', trigger: 'blur' },
        { min: 1, max: 5, message: '姓名长度必须在1-5位之间', trigger: 'blur' }
      ],
      id: [
        { required: true, message: '请输入身份证号', trigger: 'blur' },
        { min: 18, max: 18, message: '身份证号长度必须为18位', trigger: 'blur' }
      ],
      code: [
        { required: true, message: '请输入验证码', trigger: 'blur' },
        { min: 4, max: 4, message: '验证码长度必须为4位', trigger: 'blur' }
      ]
    }
  }

  return baseRules
})

const refreshCaptcha = () => {
  if (!isLoggedIn.value) {
    captchaUrl.value = userApi.getCaptcha()
  }
}

onMounted(() => {
  refreshCaptcha()
})

const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await userApi.resetPassword(form)
        ElMessage.success('密码修改成功，请重新登录')
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        router.push('/')
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '密码修改失败，请检查输入信息')
        refreshCaptcha()
      }
    } else {
      refreshCaptcha()
    }
  })
}

const goToLogin = () => {
  router.push('/')
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

.form-container {
  max-width: 500px;
  margin: 0 auto;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.reset-form {
  margin-top: 20px;
}

.captcha-container {
  display: flex;
  align-items: center;
}

.captcha-img {
  height: 40px;
  margin-left: 10px;
  cursor: pointer;
}

@media screen and (max-width: 768px) {
  .form-container {
    max-width: 100%;
    padding: 15px;
  }
  
  .el-form-item {
    margin-bottom: 15px;
  }
  
  .captcha-container {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .captcha-img {
    margin-left: 0;
    margin-top: 10px;
  }
}
</style>