<template>
  <div class="elderly-container">
    <h1 class="page-title">老人管理</h1>
    <div class="card-header">
      <div class="action-buttons">
        <el-input
          v-model="searchQuery"
          placeholder="输入老人姓名搜索"
          clearable
          style="width: 300px; margin-right: 10px"
          @clear="handleSearchClear"
          @keyup.enter="handleSearch"
        />
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button type="primary" @click="showAddDialog">新增老人</el-button>
      </div>
    </div>

    <el-table :data="filteredElderlies" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="80"></el-table-column>
      <el-table-column prop="name" label="姓名"></el-table-column>
      <el-table-column label="性别">
        <template #default="{ row }">
          {{ row.gender === 1 ? '男' : '女' }}
        </template>
      </el-table-column>
      <el-table-column prop="age" label="年龄"></el-table-column>
      <el-table-column prop="contact" label="联系方式"></el-table-column>
      <el-table-column prop="address" label="地址" width="200"></el-table-column>
      <el-table-column prop="birth_date" label="出生日期" width="120">
        <template #default="{ row }">
          {{ formatDate(row.birth_date) }}
        </template>
      </el-table-column>
      <el-table-column prop="birth_place" label="出生地"></el-table-column>
      <el-table-column prop="education" label="教育程度"></el-table-column>
      <el-table-column prop="occupation" label="职业"></el-table-column>
      <el-table-column label="操作" width="180" v-if="$route.path.includes('elderly')">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row, 'elderly')">编辑</el-button>
          <el-button size="small" type="primary" @click="viewFollowUps(row.id)">查看随访</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id, 'elderly')">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <EditDialog ref="editDialog" type="elderly" @updated="handleUpdated" />

    <!-- 添加老人对话框 -->
    <el-dialog v-model="dialogVisible" title="新增老人">
      <el-form :model="form" label-width="80px">
        <el-form-item label="姓名">
          <el-input v-model="form.name"></el-input>
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="form.gender">
            <el-radio :label="1">男</el-radio>
            <el-radio :label="0">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="年龄">
          <el-input-number v-model="form.age" :min="60"></el-input-number>
        </el-form-item>
        <el-form-item label="联系方式">
          <el-input v-model="form.contact"></el-input>
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" type="textarea"></el-input>
        </el-form-item>
        <el-form-item label="出生日期">
          <el-date-picker v-model="form.birth_date" type="date" placeholder="选择日期"></el-date-picker>
        </el-form-item>
        <el-form-item label="出生地">
          <el-input v-model="form.birth_place"></el-input>
        </el-form-item>
        <el-form-item label="教育程度">
          <el-input v-model="form.education"></el-input>
        </el-form-item>
        <el-form-item label="职业">
          <el-input v-model="form.occupation"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 随访记录对话框 -->
    <el-dialog v-model="followUpDialogVisible" :title="`${currentElderlyName}的随访记录`" width="80%">
      <el-table :data="elderlyFollowUps" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="医生" width="120">
          <template #default="{ row }">
            {{ row.doctor.name }}
          </template>
        </el-table-column>
        <el-table-column label="随访日期" width="180">
          <template #default="{ row }">
            {{ formatDate(row.follow_up_date) }}
          </template>
        </el-table-column>
        <el-table-column label="下次随访日期" width="180">
          <template #default="{ row }">
            {{ row.next_follow_up_date ? formatDate(row.next_follow_up_date) : '无' }}
          </template>
        </el-table-column>
        <el-table-column label="随访内容" prop="content" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" @click="viewReport(row.id)">查看报告</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getElderlies, createElderly, deleteElderly, getFollowUpsByElderly, generateReport } from '@/api/followUp'
import { formatDate } from '@/utils/date'
import { ElMessage } from 'element-plus'
import EditDialog from '@/views/follow-up/EditDialog.vue'

const elderlies = ref([])
const searchQuery = ref('')
const dialogVisible = ref(false)
const followUpDialogVisible = ref(false)
const elderlyFollowUps = ref([])
const currentElderlyName = ref('')
const form = ref({
  name: '',
  gender: 1,
  age: 60,
  contact: '',
  address: '',
  birth_date: '',
  birth_place: '',
  education: '',
  occupation: ''
})

// 计算属性实现搜索过滤
const filteredElderlies = computed(() => {
  if (!searchQuery.value) return elderlies.value
  return elderlies.value.filter(elderly =>
    elderly.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

onMounted(() => {
  fetchElderlies()
})

const fetchElderlies = async () => {
  try {
    const res = await getElderlies({
      search: searchQuery.value,
      skip: 0,
      limit: 100 // 根据需要调整
    })
    elderlies.value = res.data
  } catch (error) {
    console.error('获取老人列表失败:', error)
    ElMessage.error('获取老人列表失败')
  }
}

const handleSearch = () => {
  fetchElderlies()
}

const handleSearchClear = () => {
  searchQuery.value = ''
  fetchElderlies()
}

const viewFollowUps = async (elderlyId) => {
  try {
    const elderly = elderlies.value.find(e => e.id === elderlyId)
    if (elderly) {
      currentElderlyName.value = elderly.name
    }

    const res = await getFollowUpsByElderly(elderlyId)
    const followUpsData = Array.isArray(res.data) ? res.data : [res.data]

    elderlyFollowUps.value = followUpsData.map(item => {
      const doctorInfo = item.doctor || { name: '未知医生', department: '未知科室' }
      const elderlyInfo = item.elderly || { name: currentElderlyName.value }

      const formatDate = (dateStr) => {
        if (!dateStr) return ''
        const date = new Date(dateStr)
        return date.toString() === 'Invalid Date' ? dateStr : date
      }

      return {
        ...item,
        doctor: doctorInfo,
        elderly: elderlyInfo,
        follow_up_date: formatDate(item.follow_up_date),
        next_follow_up_date: formatDate(item.next_follow_up_date)
      }
    })

    followUpDialogVisible.value = true
  } catch (error) {
    console.error('获取随访记录错误:', error)
    ElMessage.error(`获取随访记录失败: ${error.response?.data?.detail || error.message}`)
  }
}

const viewReport = async (followUpId) => {
  try {
    const res = await generateReport(followUpId)
    if (!res.data) {
      throw new Error('报告数据为空')
    }

    const blob = new Blob([res.data], { type: 'text/html' })
    const url = URL.createObjectURL(blob)

    const newWindow = window.open('', '_blank')
    if (newWindow) {
      newWindow.location.href = url
    } else {
      ElMessage.warning('请允许弹出窗口以查看报告')
      const a = document.createElement('a')
      a.href = url
      a.download = `随访报告_${followUpId}.html`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
    }
  } catch (error) {
    ElMessage.error(`生成报告失败: ${error.message}`)
    console.error('生成报告失败:', error)
  }
}

const showAddDialog = () => {
  form.value = {
    name: '',
    gender: 1,
    age: 60,
    contact: '',
    address: '',
    birth_date: '',
    birth_place: '',
    education: '',
    occupation: ''
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await createElderly(form.value)
    dialogVisible.value = false
    fetchElderlies()
  } catch (error) {
    console.error(error)
  }
}

const handleDelete = async (row) => {
  try {
    await deleteElderly(row.id)
    fetchElderlies()
  } catch (error) {
    console.error(error)
  }
}

const editDialog = ref()

const handleEdit = (row) => {
  editDialog.value.open(row)
}

const handleUpdated = (updatedData) => {
  const index = elderlies.value.findIndex(item => item.id === updatedData.id)
  if (index !== -1) {
    elderlies.value[index] = updatedData
  }
}
</script>

<style scoped>
.elderly-container {
  padding: 40px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  gap: 10px;
  align-items: center;
}

.el-table {
  margin-top: 20px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.el-table::before {
  display: none;
}

.el-table--border {
  border-radius: 8px;
}

.el-dialog {
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.el-form-item__label {
  font-weight: bold;
}

@media (max-width: 768px) {
  .el-table {
    overflow-x: auto;
  }

  .el-dialog {
    width: 95%;
  }
}
</style>