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
        <el-table-column prop="elderly.name" label="老人姓名" />
        <el-table-column prop="doctor.name" label="医生" />
        <el-table-column prop="follow_up_date" label="随访日期" width="180">
          <template #default="{row}">
            {{ formatDate(row.follow_up_date) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{row}">
            <el-button size="small" @click="viewReport(row.id)">查看报告</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增对话框 -->
    <el-dialog v-model="dialogVisible" title="新增随访记录" @close="resetForm">
      <el-form :model="formData" label-width="120px" ref="formRef">
        <el-form-item label="老人ID" required>
          <el-input v-model.number="formData.elderly_id" />
        </el-form-item>
        <el-form-item label="医生ID" prop="doctor_id" required>
          <el-input v-model.number="formData.doctor_id" />
        </el-form-item>
        <el-form-item label="随访日期" prop="follow_up_date" required>
          <el-date-picker
            v-model="formData.follow_up_date"
            type="datetime"
            placeholder="选择日期时间"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="随访内容" prop="content">
          <el-input v-model="formData.content" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useFollowUpStore } from '@/stores/followUp'
import { formatDate } from '@/utils/date'

const followUpStore = useFollowUpStore()
const dialogVisible = ref(false)
const formData = ref({
  elderly_id: '',
  doctor_id: '',
  follow_up_date: '',
  content: ''
})

// 获取列表数据
onMounted(async () => {
  await followUpStore.fetchFollowUps()
})

// 显示创建对话框
const showCreateDialog = () => {
  dialogVisible.value = true
}

// 提交表单
const submitForm = async () => {
  try {
    await followUpStore.createFollowUp(formData.value)
    dialogVisible.value = false
    ElMessage.success('创建成功')
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

// 查看报告
const viewReport = async (id) => {
  const res = await followUpApi.generateReport(id)
  const blob = new Blob([res.data], { type: 'text/html' })
  const url = URL.createObjectURL(blob)
  window.open(url, '_blank')
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