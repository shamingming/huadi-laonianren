<template>
  <div style="background-color: #f4f7fa; padding: 20px;">
    <h1 style="color: #0066cc; font-size: 28px; margin-bottom: 20px;">医生管理</h1>
    <div class="search-container" style="display: flex; align-items: center; margin-bottom: 20px;">
      <el-input
        v-model="searchQuery"
        placeholder="输入医生姓名搜索"
        clearable
        style="width: 300px; margin-right: 10px; border-radius: 4px; border: 1px solid #ccc;"
        @clear="handleSearchClear"
        @keyup.enter="handleSearch"
      />
      <el-button type="primary" style="background-color: #0066cc; border-color: #0066cc; border-radius: 4px;" @click="handleSearch">搜索</el-button>
      <el-button type="primary" style="background-color: #0066cc; border-color: #0066cc; border-radius: 4px;" @click="showAddDialog">新增医生</el-button>
    </div>

    <el-table :data="filteredDoctors" border style="width: 100%; background-color: #fff; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
      <el-table-column prop="id" label="ID" width="80"></el-table-column>
      <el-table-column prop="name" label="姓名"></el-table-column>
      <el-table-column prop="department" label="科室"></el-table-column>
      <el-table-column prop="contact" label="联系方式"></el-table-column>
      <el-table-column label="操作" width="180" v-if="$route.path.includes('doctors')">
        <template #default="{ row }">
          <el-button size="small" style="background-color: #0066cc; border-color: #0066cc; border-radius: 4px;" @click="handleEdit(row, 'doctor')">编辑</el-button>
          <el-button size="small" type="danger" style="border-radius: 4px;" @click="handleDelete(row.id, 'doctor')">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <EditDialog ref="editDialog" type="doctor" @updated="handleUpdated" />

    <!-- 添加医生对话框 -->
    <el-dialog v-model="dialogVisible" title="新增医生" style="border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
      <el-form :model="form" label-width="80px">
        <el-form-item label="姓名">
          <el-input v-model="form.name" style="border-radius: 4px; border: 1px solid #ccc;"></el-input>
        </el-form-item>
        <el-form-item label="科室">
          <el-input v-model="form.department" style="border-radius: 4px; border: 1px solid #ccc;"></el-input>
        </el-form-item>
        <el-form-item label="联系方式">
          <el-input v-model="form.contact" style="border-radius: 4px; border: 1px solid #ccc;"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false" style="border-radius: 4px;">取消</el-button>
        <el-button type="primary" style="background-color: #0066cc; border-color: #0066cc; border-radius: 4px;" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import {ref, computed, onMounted} from 'vue'
import {getDoctors, createDoctor, deleteDoctor} from '@/api/followUp'
import EditDialog from '@/views/follow-up/EditDialog.vue'

const doctors = ref([])
const searchQuery = ref('')
const dialogVisible = ref(false)
const form = ref({
  name: '',
  department: '全科',
  contact: ''
})

// 计算属性实现搜索过滤
const filteredDoctors = computed(() => {
  if (!searchQuery.value) return doctors.value
  return doctors.value.filter(doctor =>
      doctor.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

onMounted(() => {
  fetchDoctors()
})

const fetchDoctors = async () => {
  try {
    const res = await getDoctors({search: searchQuery.value})
    doctors.value = res.data
  } catch (error) {
    console.error(error)
  }
}


const handleSearch = () => {
  // 计算属性会自动处理，这里只需保持逻辑
}

const handleSearchClear = () => {
  searchQuery.value = ''
}

const showAddDialog = () => {
  form.value = {
    name: '',
    department: '全科',
    contact: ''
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await createDoctor(form.value)
    dialogVisible.value = false
    fetchDoctors()
  } catch (error) {
    console.error(error)
  }
}

const handleDelete = async (row) => {
  try {
    await deleteDoctor(row.id)
    fetchDoctors()
  } catch (error) {
    console.error(error)
  }
}

const editDialog = ref()

const handleEdit = (row) => {
  editDialog.value.open(row)
}

const handleUpdated = (updatedData) => {
  const index = doctors.value.findIndex(item => item.id === updatedData.id)
  if (index !== -1) {
    doctors.value[index] = updatedData
  }
}
</script>

