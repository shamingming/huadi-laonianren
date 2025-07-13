import { createRouter, createWebHistory } from 'vue-router'
import ElderlyListView from '@/views/elderly/ListView.vue'
import DoctorListView from '@/views/doctor/ListView.vue'
import FollowUpListView from '@/views/follow-up/ListView.vue'

const routes = [
  {
    path: '/',
    redirect: '/elderly'
  },
  {
    path: '/elderly',
    name: 'ElderlyList',
    component: ElderlyListView
  },
  {
    path: '/doctors',
    name: 'DoctorList',
    component: DoctorListView
  },
  {
    path: '/follow-ups',
    name: 'FollowUpList',
    component: FollowUpListView
  }
]


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 设置页面标题
router.beforeEach((to) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - 老年人健康管理系统`
  }
})

export default router