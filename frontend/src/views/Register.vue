<template>
  <div class="container">
    <div class="header">
      <h2>研究生成绩排名查询系统</h2>
    </div>

    <div class="form-container">
      <h3>查询成绩</h3>
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="120px"
        class="register-form"
      >
        <el-form-item label="准考证号" prop="kaohao">
          <el-input v-model="form.kaohao" placeholder="请输入准考证号"></el-input>
        </el-form-item>
        <!-- <el-form-item label="考生姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名"></el-input>
        </el-form-item> -->
        <el-form-item label="身份证号" prop="id">
          <el-input v-model="form.id" placeholder="请输入身份证号"></el-input>
        </el-form-item>
        <el-form-item label="学院" prop="college">
          <el-select
            v-model="form.college"
            placeholder="请选择学院"
            filterable
            :loading="collegesLoading"
          >
            <el-option
              v-for="item in colleges"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="查询密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="设置6-20位密码，用于后续登录"></el-input>
        </el-form-item>
        <el-form-item label="验证码" prop="code">
          <div class="captcha-container">
            <el-input v-model="form.code" placeholder="请输入验证码"></el-input>
            <img :src="captchaUrl" @click="refreshCaptcha" class="captcha-img" alt="验证码">
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm">查询成绩</el-button>
          <el-button @click="goToLogin">返回登录</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { userApi } from '@/api'

const router = useRouter()
const formRef = ref(null)
const captchaUrl = ref('')
const colleges = ref([])
const collegesLoading = ref(false)

const form = reactive({
  kaohao: '103586210000204',
  // name: '',
  id: '340881200012205596',
  college: '',
  password: '123456',
  code: ''
})

const rules = {
  kaohao: [
    { required: true, message: '请输入准考证号', trigger: 'blur' },
    { min: 15, max: 15, message: '准考证号长度必须为15位', trigger: 'blur' }
  ],
  // name: [
  //   { required: true, message: '请输入姓名', trigger: 'blur' },
  //   { min: 1, max: 5, message: '姓名长度必须在1-5位之间', trigger: 'blur' }
  // ],
  id: [
    { required: true, message: '请输入身份证号', trigger: 'blur' },
    { min: 18, max: 18, message: '身份证号长度必须为18位', trigger: 'blur' }
  ],
  college: [
    { required: true, message: '请选择学院', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请设置查询密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度必须在6-20位之间', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { min: 4, max: 4, message: '验证码长度必须为4位', trigger: 'blur' }
  ]
}

const refreshCaptcha = () => {
  captchaUrl.value = userApi.getCaptcha()
}

onMounted(() => {
  refreshCaptcha()
  loadColleges()
})

const loadColleges = async () => {
  collegesLoading.value = true
  try {
    const response = await userApi.getColleges()
    colleges.value = response.colleges || []
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '学院列表获取失败，请刷新重试')
  } finally {
    collegesLoading.value = false
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await ElMessageBox.confirm(
          `学院选择后不可更改。<br/>当前选择：<strong>${form.college}</strong>`,
          '确认学院',
          {
            confirmButtonText: '确认',
            cancelButtonText: '返回修改',
            type: 'warning',
            dangerouslyUseHTMLString: true
          }
        )
      } catch (confirmError) {
        return
      }
      try {
        const response = await userApi.register(form)
        localStorage.setItem('token', response.token)
        localStorage.setItem('user', JSON.stringify(response.user))
        ElMessage.success('成绩查询成功')
        router.push('/score')
      } catch (error) {
        console.log('11', error)
        ElMessage.error(error.response?.data?.message || '查询失败，请检查输入信息')
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

.register-form {
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
