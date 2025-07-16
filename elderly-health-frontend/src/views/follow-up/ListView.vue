<template>
  <div style="background-color: #f4f7fa; padding: 20px;">
    <el-card style="border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
      <template #header>
        <div class="card-header" style="display: flex; justify-content: space-between; align-items: center; color: #0066cc;">
          <span>随访记录管理</span>
          <el-button type="primary" style="background-color: #0066cc; border-color: #0066cc; border-radius: 4px;" @click="showCreateDialog">新增随访</el-button>
        </div>
      </template>
      <div class="search-container" style="margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 10px;">
    <!-- 老人姓名搜索 -->
    <el-input
      v-model="searchParams.elderlyName"
      placeholder="老人姓名"
      clearable      style="width: 200px"
    />

    <!-- 医生姓名搜索 -->
    <el-input
      v-model="searchParams.doctorName"
      placeholder="医生姓名"
      clearable      style="width: 200px"
    />

    <!-- 日期范围选择 -->
    <el-date-picker
      v-model="searchParams.dateRange"
      type="daterange"
      range-separator="至"
      start-placeholder="开始日期"
      end-placeholder="结束日期"      style="width: 350px"
    />

    <el-button
      type="primary"
      @click="handleSearch"
      :loading="searchLoading"
    >
      搜索
    </el-button>

    <el-button @click="resetSearch">重置</el-button>
  </div>

      <el-table :data="followUps" border style="width: 100%; background-color: #fff; border-radius: 8px;">
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
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button size="small" style="background-color: #0066cc; border-color: #0066cc; border-radius: 4px;" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" style="background-color: #0066cc; border-color: #0066cc; border-radius: 4px;" @click="viewReport(row.id)">查看报告</el-button>
            <el-button size="small" type="danger" style="border-radius: 4px;" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <EditDialog ref="editDialog" type="follow-up" @updated="handleUpdated" />

    <!-- 新增对话框 -->
    <el-dialog v-model="dialogVisible" title="新增随访记录" style="border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
      <el-form :model="formData" label-width="120px">
        <el-form-item label="老人" required>
          <el-select v-model="formData.elderly_id" placeholder="请选择老人" clearable style="border-radius: 4px; border: 1px solid #ccc;">
            <el-option
              v-for="elderly in elderlies"
              :key="elderly.id"
              :label="elderly.name"
              :value="elderly.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="医生" required>
          <el-select v-model="formData.doctor_id" placeholder="请选择医生" clearable style="border-radius: 4px; border: 1px solid #ccc;">
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
            style="border-radius: 4px; border: 1px solid #ccc;"
          />
        </el-form-item>
        <el-form-item label="排期策略">
          <el-radio-group v-model="formData.schedule_strategy">
            <el-radio label="manual">手动指定</el-radio>
            <el-radio label="automated">自动排期</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="下次随访时间" v-if="formData.schedule_strategy === 'manual'">
          <el-date-picker v-model="formData.next_follow_up_date" type="datetime" style="border-radius: 4px; border: 1px solid #ccc;" />
        </el-form-item>

        <el-form-item label="自动排期间隔" v-if="formData.schedule_strategy === 'automated'">
          <el-input-number v-model="formData.schedule_interval" :min="1" :max="365" style="border-radius: 4px; border: 1px solid #ccc;" />
          <span style="margin-left:10px">天</span>
        </el-form-item>
        <el-form-item label="随访内容">
          <el-input v-model="formData.content" type="textarea" rows="4" style="border-radius: 4px; border: 1px solid #ccc;"></el-input>
        </el-form-item>
        <el-form-item label="用药禁忌">
          <el-input v-model="formData.medication_warning" type="textarea" rows="2" placeholder="请输入老人的用药禁忌或注意事项" style="border-radius: 4px; border: 1px solid #ccc;"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false" style="border-radius: 4px;">取消</el-button>
        <el-button type="primary" style="background-color: #0066cc; border-color: #0066cc; border-radius: 4px;" @click="submitForm">提交</el-button>
      </template>
    </el-dialog>
  </div>
   <el-pagination
    v-model:current-page="pagination.page"
    v-model:page-size="pagination.per_page"
    :page-sizes="[10, 20, 50, 100]"
    :total="pagination.total"
    layout="total, sizes, prev, pager, next, jumper"
    @size-change="handleSizeChange"
    @current-change="handleCurrentChange"    style="margin-top: 20px; justify-content: flex-end;"
  />
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getFollowUps, createFollowUp, deleteFollowUp, getElderlies, getDoctors, generateReport } from '@/api/followUp'
import { formatDate } from '@/utils/date'
import { ElMessage } from 'element-plus'
import EditDialog from './EditDialog.vue'
import { formatDateToBackend } from '@/utils/date'
// 分页状态
const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})
const followUps = ref([])
const doctors = ref([])
const elderlies = ref([])
const dialogVisible = ref(false)
const formData = ref({
  elderly_id: '',
  doctor_id: '',
  follow_up_date: '',
  content: '',
  schedule_strategy: 'manual', // 默认手动
  schedule_interval: 30, // 默认30天
  is_recurring: false,
  medication_warning: '' // 新增用药禁忌字段
})

onMounted(async () => {
  try {
    await fetchFollowUpsWithSearch()
    // 添加调试日志：打印完整的随访数据
    console.log('随访数据加载完成:', {
          items: followUps.value,
          pagination: {...pagination}
        })
    await fetchDoctors()
    await fetchElderlies()
  } catch (error) {
    console.error('初始化失败:', error)
  }
})

// 搜索参数
const searchParams = reactive({
  elderlyName: '',
  doctorName: '',
  dateRange: []
})
// 在 ListView.vue 中添加方法将姓名转换为ID
const getElderlyIdByName = async (name) => {
  const res = await getElderlies({ name })
  return res.data[0]?.id
}

const getDoctorIdByName = async (name) => {
  const res = await getDoctors({ name })
  return res.data[0]?.id
}
const searchLoading = ref(false)
// 搜索方法
// 修改 ListView.vue 中的 handleSearch 方法
// 修改后的 handleSearch 方法
const handleSearch = async () => {
  searchLoading.value = true
  try {
    // 重置到第一页
    pagination.page = 1
    await fetchFollowUpsWithSearch()
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    searchLoading.value = false
  }
}


// 页面加载时获取医生数据
onMounted(async () => {
  try {
    // 调用获取医生列表的接口
    const res = await getDoctors()
    // 检查接口返回格式是否正确
    if (res && Array.isArray(res.data)) {
      doctors.value = res.data
      console.log('[DEBUG] 医生数据加载成功:', doctors.value)
    } else {
      doctors.value = []
      console.warn('[WARNING] 医生数据格式不正确:', res)
    }
  } catch (error) {
    console.error('[ERROR] 获取医生列表失败:', error)
    ElMessage.error('加载医生列表失败，请刷新页面重试')
  }
})



// 重置搜索
const resetSearch = () => {
  searchParams.elderlyName = ''
  searchParams.doctorName = ''
  searchParams.dateRange = []
  handleSearch() // 重新加载数据
}
const fetchFollowUps = async () => {
  try {
    const res = await getFollowUps({
      page: pagination.page,
      per_page: pagination.per_page
    })
    console.log('API完整响应:', res) // 添加调试日志

    // 处理两种可能的响应格式
    if (res.data?.items) {
      // 分页格式
      followUps.value = res.data.items
      pagination.total = res.data.total
    } else if (Array.isArray(res.data)) {
      // 普通数组格式
      followUps.value = res.data
      pagination.total = res.data.length
    } else {
      followUps.value = []
      pagination.total = 0
    }
  } catch (error) {
    console.error('API错误详情:', {
      error: error,
      response: error.response,
      config: error.config
    })
    ElMessage.error('获取数据失败: ' + (error.response?.data?.detail || error.message))
  }
}



// 分页事件处理
// 修改分页处理方法
const handleSizeChange = (val) => {
  pagination.per_page = val
  pagination.page = 1 // 重置到第一页
  fetchFollowUpsWithSearch() // 使用带搜索条件的方法
}

const handleCurrentChange = (val) => {
  pagination.page = val
  fetchFollowUpsWithSearch() // 使用带搜索条件的方法
}

// 新增方法：带搜索条件的获取数据
const fetchFollowUpsWithSearch = async () => {
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      elderly_name: searchParams.elderlyName,  // 携带搜索条件
      doctor_name: searchParams.doctorName,    // 携带搜索条件
    }

    // 处理日期范围
    if (searchParams.dateRange && searchParams.dateRange.length === 2) {
      params.start_date = formatDateToBackend(searchParams.dateRange[0])
      params.end_date = formatDateToBackend(searchParams.dateRange[1])
    }

    const res = await getFollowUps(params)
    followUps.value = res.data.items
    pagination.total = res.data.total
  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error('获取数据失败: ' + (error.response?.data?.detail || error.message))
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
    schedule_strategy: 'manual', // 默认手动
    schedule_interval: 30, // 默认30天
    is_recurring: false,
    medication_warning: '' // 新增用药禁忌字段
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
      schedule_strategy: formData.value.schedule_strategy,
      schedule_interval: formData.value.schedule_interval,
      is_recurring: formData.value.is_recurring,
      medication_warning: formData.value.medication_warning || '',
      next_follow_up_date: formData.value.schedule_strategy === 'manual'
        ? formData.value.next_follow_up_date
        : (formData.value.schedule_strategy === 'automated'
          ? new Date(new Date(formData.value.follow_up_date).getTime() + formData.value.schedule_interval * 86400000).toISOString()
          : null)
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
const editDialog = ref()

const handleEdit = (row) => {
  editDialog.value.open(row)
}

const handleUpdated = (updatedData) => {
  const index = followUps.value.findIndex(item => item.id === updatedData.id)
  if (index !== -1) {
    followUps.value[index] = updatedData
  }
}
</script>