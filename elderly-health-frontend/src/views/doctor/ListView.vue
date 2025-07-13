<template>
  <div>
    <h1>医生管理</h1>
    <el-button type="primary" @click="showAddDialog">新增医生</el-button>

    <el-table :data="doctors" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="80"></el-table-column>
      <el-table-column prop="name" label="姓名"></el-table-column>
      <el-table-column prop="department" label="科室"></el-table-column>
      <el-table-column prop="contact" label="联系方式"></el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="scope">
          <el-button size="small" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加医生对话框 -->
    <el-dialog v-model="dialogVisible" title="新增医生">
      <el-form :model="form" label-width="80px">
        <el-form-item label="姓名">
          <el-input v-model="form.name"></el-input>
        </el-form-item>
        <el-form-item label="科室">
          <el-input v-model="form.department"></el-input>
        </el-form-item>
        <el-form-item label="联系方式">
          <el-input v-model="form.contact"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDoctors, createDoctor, deleteDoctor } from '@/api/followUp'

const doctors = ref([])
const dialogVisible = ref(false)
const form = ref({
  name: '',
  department: '全科',
  contact: ''
})

onMounted(() => {
  fetchDoctors()
})

const fetchDoctors = async () => {
  try {
    const res = await getDoctors()
    doctors.value = res.data
  } catch (error) {
    console.error(error)
  }
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
    await deleteDoctor(row.id)  // 确保这里调用的是 deleteDoctor
    fetchDoctors()
  } catch (error) {
    console.error(error)
  }
}
</script>
