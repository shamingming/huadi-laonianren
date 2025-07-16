<template>
  <div class="app-container">
    <div class="header">
      <h1 class="system-title">医生随访管理系统</h1>
      <el-menu
        :router="true"
        mode="horizontal"
        background-color="#007BFF"
        text-color="#fff"
        active-text-color="#FFC107"
        class="nav-menu"
      >
        <el-menu-item index="/elderly">老人管理</el-menu-item>
        <el-menu-item index="/doctors">医生管理</el-menu-item>
        <el-menu-item index="/follow-ups">随访管理</el-menu-item>
      </el-menu>
    </div>
    <router-view />
  </div>
</template>

<script setup>
// 这里可以添加需要的逻辑
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background-color: #f8f9fa;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header {
  background-color: #007BFF;
  color: white;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  padding: 20px 0;
}

.system-title {
  text-align: center;
  font-size: 32px;
  font-weight: bold;
  margin: 0;
  padding-bottom: 20px;
  letter-spacing: 2px;
}

.nav-menu {
  display: flex;
  justify-content: center;
  border-bottom: none;
}

.nav-menu .el-menu-item {
  font-size: 18px;
  height: 50px;
  line-height: 50px;
  transition: background-color 0.3s ease;
}

.nav-menu .el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1) !important;
}
</style>