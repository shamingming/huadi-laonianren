<template>
  <div class="follow-up-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>随访记录管理</span>
          <el-button type="primary" @click="showCreateDialog">新增随访</el-button>
        </div>
      </template>

      <el-table :data="followUps" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />

        <el-table-column label="老人姓名">
          <template #default="{ row }">
            {{ row.elderly?.name || '未知' }}
          </template>
        </el-table-column>

        <el-table-column label="医生">
          <template #default="{ row }">
            {{ row.doctor?.name || '未知' }}
          </template>
        </el-table-column>
        <el-table-column prop="follow_up_date" label="随访日期" width="180">
          <template #default="{ row }">
            {{ formatDate(row.follow_up_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="content" label="随访内容" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" @click="viewReport(row.id)">查看报告</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增对话框 -->
    <el-dialog v-model="dialogVisible" title="新增随访记录">
    <el-form :model="formData" label-width="120px">
      <el-form-item label="老人" required>
        <el-select v-model="formData.elderly_id" placeholder="请选择老人" clearable>
          <el-option
            v-for="elderly in elderlies"
            :key="elderly.id"
            :label="elderly.name"
            :value="elderly.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="医生" required>
        <el-select v-model="formData.doctor_id" placeholder="请选择医生" clearable>
          <el-option
            v-for="doctor in doctors"
            :key="doctor.id"
            :label="doctor.name"
            :value="doctor.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="随访日期" required>
        <el-date-picker
          v-model="formData.follow_up_date"
          type="datetime"
          placeholder="选择日期时间"
          value-format="YYYY-MM-DD HH:mm:ss"
        />
      </el-form-item>
        <el-form-item label="随访内容">
          <el-input v-model="formData.content" type="textarea" rows="4" />
        </el-form-item>
        <el-form-item label="随访结果">
          <el-input v-model="formData.result" type="textarea" rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getFollowUps, createFollowUp, deleteFollowUp, getElderlies, getDoctors,generateReport } from '@/api/followUp'
import { formatDate } from '@/utils/date'
import { ElMessage } from 'element-plus'


const followUps = ref([])
const doctors = ref([])
const elderlies = ref([])
const dialogVisible = ref(false)
const formData = ref({
  elderly_id: '',
  doctor_id: '',
  follow_up_date: '',
  content: '',
  result: ''
})

onMounted(async () => {
  try {
    await fetchFollowUps()
    console.log('followUps value:', JSON.stringify(followUps.value, null, 2))  // 添加调试信息
    await fetchDoctors()
    await fetchElderlies()
  } catch (error) {
    console.error('初始化失败:', error)
  }
})



const fetchFollowUps = async () => {
  try {
    const res = await getFollowUps()
    console.log('fetchFollowUps response data:', JSON.stringify(res.data, null, 2))  // 添加调试信息
    followUps.value = res.data
  } catch (error) {
    ElMessage.error('获取随访记录失败')
    console.error(error)
  }
}




const fetchDoctors = async () => {
  try {
    const res = await getDoctors()
    doctors.value = res.data
  } catch (error) {
    console.error(error)
  }
}

const fetchElderlies = async () => {
  try {
    const res = await getElderlies()
    elderlies.value = res.data
  } catch (error) {
    console.error(error)
  }
}

const showCreateDialog = () => {
  formData.value = {
    elderly_id: '',
    doctor_id: '',
    follow_up_date: '',
    content: '',
    result: ''
  }
  dialogVisible.value = true
}

const submitForm = async () => {
  try {
    // 验证必填字段
    if (!formData.value.elderly_id || !formData.value.doctor_id || !formData.value.follow_up_date) {
      ElMessage.error('请填写所有必填字段')
      return
    }

    const payload = {
      elderly_id: Number(formData.value.elderly_id),
      doctor_id: Number(formData.value.doctor_id),
      follow_up_date: formData.value.follow_up_date,
      content: formData.value.content || '',
      result: formData.value.result || ''
    }

    console.log('提交数据:', payload) // 调试用
    await createFollowUp(payload)
    dialogVisible.value = false
    ElMessage.success('创建成功')
    await fetchFollowUps()
  } catch (error) {
    ElMessage.error(`创建失败: ${error.response?.data?.detail || error.message}`)
    console.error('创建失败详情:', error.response?.data)
  }
}

const viewReport = async (id) => {
  try {
    console.log('开始生成报告，ID:', id)
    const res = await generateReport(id)
    console.log('报告响应:', res)

    if (!res.data) {
      throw new Error('报告数据为空')
    }

    const blob = new Blob([res.data], { type: 'text/html' })
    const url = URL.createObjectURL(blob)

    // 解决浏览器可能拦截弹出窗口的问题
    const newWindow = window.open('', '_blank')
    if (newWindow) {
      newWindow.location.href = url
    } else {
      ElMessage.warning('请允许弹出窗口以查看报告')
      // 备用方案：下载文件
      const a = document.createElement('a')
      a.href = url
      a.download = `随访报告_${id}.html`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
    }
  } catch (error) {
    console.error('生成报告失败详情:', {
      error: error,
      response: error.response,
      request: error.request
    })
    ElMessage.error(`生成报告失败: ${error.message}`)
  }
}



const handleDelete = async (id) => {
  try {
    await deleteFollowUp(id)
    ElMessage.success('删除成功')
    await fetchFollowUps() // 刷新列表
  } catch (error) {
    console.error('删除失败详情:', error.response)
    ElMessage.error(`删除失败: ${error.response?.data?.detail || error.message}`)
  }
}

</script>

<style scoped>
.follow-up-container {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
