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
            {{ row.elderly.name }}
          </template>
        </el-table-column>

        <el-table-column label="医生">
          <template #default="{ row }">
            {{ row.doctor.name }}
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
      <el-form-item label="排期策略">
        <el-radio-group v-model="formData.schedule_strategy">
          <el-radio label="manual">手动指定</el-radio>
          <el-radio label="automated">自动排期</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="下次随访时间" v-if="formData.schedule_strategy === 'manual'">
        <el-date-picker v-model="formData.next_follow_up_date" type="datetime"/>
      </el-form-item>

      <el-form-item label="自动排期间隔" v-if="formData.schedule_strategy === 'automated'">
        <el-input-number v-model="formData.schedule_interval" :min="1" :max="365"/>
        <span style="margin-left:10px">天</span>
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
import { getFollowUps, createFollowUp, deleteFollowUp, getElderlies, getDoctors, generateReport } from '@/api/followUp'
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
    // 添加调试日志：打印完整的随访数据
    console.log('[DEBUG] 随访数据:', JSON.stringify(followUps.value, null, 2))
    await fetchDoctors()
    await fetchElderlies()
  } catch (error) {
    console.error('初始化失败:', error)
  }
})

const fetchFollowUps = async () => {
  try {
    const res = await getFollowUps()
    console.log('[DEBUG] 原始API响应数据:', JSON.stringify(res.data, null, 2))

    followUps.value = res.data.map(item => {
      // 处理老人信息（核心修改）
      let elderlyInfo = item.elderly || {};
      // 若老人信息存在但姓名为空，显示"未知老人"
      if (elderlyInfo && !elderlyInfo.name) {
        elderlyInfo.name = "未知老人";
        console.warn(`随访记录 ${item.id} 的老人姓名为空`);
      }
      // 若老人信息完全缺失（关联失败），显示"无关联老人"
      if (!item.elderly) {
        elderlyInfo = {
          id: item.elderly_id || 0,
          name: "无关联老人",
          gender: "",
          age: 0
        };
        console.warn(`随访记录 ${item.id} 缺失老人关联数据`);
      }

      // 处理医生信息（核心修改）
      let doctorInfo = item.doctor || {};
      // 若医生信息存在但姓名为空，显示"未知医生"
      if (doctorInfo && !doctorInfo.name) {
        doctorInfo.name = "未知医生";
        console.warn(`随访记录 ${item.id} 的医生姓名为空`);
      }
      // 若医生信息完全缺失（关联失败），显示"无关联医生"
      if (!item.doctor) {
        doctorInfo = {
          id: item.doctor_id || 0,
          name: "无关联医生",
          department: ""
        };
        console.warn(`随访记录 ${item.id} 缺失医生关联数据`);
      }

      return {
        ...item,
        elderly: elderlyInfo,
        doctor: doctorInfo
      };
    });
  } catch (error) {
    ElMessage.error('获取随访记录失败')
    console.error('获取随访记录失败详情:', error)
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

// ListView.vue 的showCreateDialog方法
const showCreateDialog = () => {
  formData.value = {
    elderly_id: '',
    doctor_id: '',
    follow_up_date: '',
    content: '',
    result: '',
    schedule_strategy: 'manual', // 默认手动
    schedule_interval: 30, // 默认30天
    is_recurring: false
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
      result: formData.value.result || '',
      schedule_strategy: formData.value.schedule_strategy,
      schedule_interval: formData.value.schedule_interval,
      is_recurring: formData.value.is_recurring,
      next_follow_up_date: formData.value.schedule_strategy === 'manual'
        ? formData.value.next_follow_up_date
        : null
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
