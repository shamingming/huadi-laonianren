import { createRouter, createWebHistory } from 'vue-router'
import FollowUpListView from '../views/follow-up/ListView.vue'

const routes = [
  {
    path: '/',
    redirect: '/follow-ups'
  },
  {
    path: '/follow-ups',
    name: 'follow-up-list',
    component: FollowUpListView,
    meta: { title: '随访记录管理' }
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