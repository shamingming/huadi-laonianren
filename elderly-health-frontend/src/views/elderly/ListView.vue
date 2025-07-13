<template>
  <div>
    <h1>老人管理</h1>
    <el-button type="primary" @click="showAddDialog">新增老人</el-button>

    <el-table :data="elderlies" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="80"></el-table-column>
      <el-table-column prop="name" label="姓名"></el-table-column>
      <el-table-column prop="gender" label="性别"></el-table-column>
      <el-table-column prop="age" label="年龄"></el-table-column>
      <el-table-column prop="contact" label="联系方式"></el-table-column>
      <el-table-column prop="address" label="地址" width="200"></el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="scope">
          <el-button size="small" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加老人对话框 -->
    <el-dialog v-model="dialogVisible" title="新增老人">
      <el-form :model="form" label-width="80px">
        <el-form-item label="姓名">
          <el-input v-model="form.name"></el-input>
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="form.gender" placeholder="请选择">
            <el-option label="男" value="男"></el-option>
            <el-option label="女" value="女"></el-option>
          </el-select>
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
import { getElderlies, createElderly, deleteElderly } from '@/api/followUp'

const elderlies = ref([])
const dialogVisible = ref(false)
const form = ref({
  name: '',
  gender: '男',
  age: 60,
  contact: '',
  address: ''
})

onMounted(() => {
  fetchElderlies()
})

const fetchElderlies = async () => {
  try {
    const res = await getElderlies()
    elderlies.value = res.data
  } catch (error) {
    console.error(error)
  }
}

const showAddDialog = () => {
  form.value = {
    name: '',
    gender: '男',
    age: 60,
    contact: '',
    address: ''
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
</script>
