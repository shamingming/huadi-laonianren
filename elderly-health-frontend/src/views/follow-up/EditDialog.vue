<template>
  <el-dialog v-model="visible" :title="title">
    <el-form :model="formData" label-width="120px">
      <!-- 老人编辑表单 -->
      <template v-if="type === 'elderly'">
        <el-form-item label="姓名" required>
          <el-input v-model="formData.name"></el-input>
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="formData.gender" placeholder="请选择">
            <el-option label="男" value="男"></el-option>
            <el-option label="女" value="女"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="年龄">
          <el-input-number v-model="formData.age" :min="60"></el-input-number>
        </el-form-item>
        <el-form-item label="联系方式">
          <el-input v-model="formData.contact"></el-input>
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="formData.address" type="textarea"></el-input>
        </el-form-item>
      </template>

      <!-- 医生编辑表单 -->
      <template v-else-if="type === 'doctor'">
        <el-form-item label="姓名" required>
          <el-input v-model="formData.name"></el-input>
        </el-form-item>
        <el-form-item label="科室">
          <el-input v-model="formData.department"></el-input>
        </el-form-item>
        <el-form-item label="联系方式">
          <el-input v-model="formData.contact"></el-input>
        </el-form-item>
      </template>

      <!-- 随访编辑表单 -->
      <template v-else>
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
          <el-date-picker v-model="formData.next_follow_up_date" type="datetime" value-format="YYYY-MM-DD HH:mm:ss"/>
        </el-form-item>
        <el-form-item label="自动排期间隔" v-if="formData.schedule_strategy === 'automated'">
          <el-input-number v-model="formData.schedule_interval" :min="1" :max="365"/>
          <span style="margin-left:10px">天</span>
        </el-form-item>
        <el-form-item label="随访内容">
          <el-input v-model="formData.content" type="textarea" rows="4"/>
        </el-form-item>>
        <el-form-item label="用药禁忌">
          <el-input v-model="formData.medication_warning" type="textarea" rows="2"/>
        </el-form-item>
      </template>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  updateElderly,
  updateDoctor,
  updateFollowUp,
  getElderlies,
  getDoctors
} from '@/api/followUp'
import { ElMessage } from 'element-plus'

const props = defineProps({
  type: {
    type: String,
    required: true,
    validator: value => ['elderly', 'doctor', 'follow-up'].includes(value)
  }
})

const emit = defineEmits(['updated'])

const visible = ref(false)
const formData = ref({})
const elderlies = ref([])
const doctors = ref([])
const currentId = ref(null)

const title = computed(() => {
  return `编辑${
    props.type === 'elderly' ? '老人' :
    props.type === 'doctor' ? '医生' : '随访记录'
  }信息`
})

const open = async (data) => {
  currentId.value = data.id
  formData.value = JSON.parse(JSON.stringify(data))

  if (props.type === 'follow-up') {
    // 加载老人和医生列表
    try {
      const [elderlyRes, doctorRes] = await Promise.all([
        getElderlies({ skip: 0, limit: 100 }), // 添加分页参数
        getDoctors({ skip: 0, limit: 100 })    // 添加分页参数
      ])
      elderlies.value = elderlyRes.data
      doctors.value = doctorRes.data
    } catch (error) {
      console.error('加载数据失败:', error)
      ElMessage.error('加载老人和医生列表失败')
    }
  }

  visible.value = true
}

const handleSubmit = async () => {
  try {
    let res
    switch (props.type) {
      case 'elderly':
        res = await updateElderly(currentId.value, formData.value)
        break
      case 'doctor':
        res = await updateDoctor(currentId.value, formData.value)
        break
      case 'follow-up':
        // 处理随访数据
        const payload = {
          ...formData.value,
          elderly_id: Number(formData.value.elderly_id),
          doctor_id: Number(formData.value.doctor_id),
          next_follow_up_date: formData.value.schedule_strategy === 'manual'
            ? formData.value.next_follow_up_date
            : formData.value.schedule_strategy === 'automated'
              ? new Date(new Date(formData.value.follow_up_date).getTime() +
                formData.value.schedule_interval * 86400000).toISOString()
              : null
        }
        res = await updateFollowUp(currentId.value, payload)
        break
    }

    ElMessage.success('更新成功')
    visible.value = false
    emit('updated', res.data)
  } catch (error) {
    ElMessage.error(`更新失败: ${error.response?.data?.detail || error.message}`)
    console.error('更新失败详情:', error)
  }
}

defineExpose({ open })
</script>

<style scoped>
.el-dialog {
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.el-form-item__label {
  font-weight: bold;
}

.el-form-item {
  margin-bottom: 20px;
}
</style>