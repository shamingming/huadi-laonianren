<template>
  <el-container>
    <el-header>
      <el-menu mode="horizontal" router>
        <el-menu-item index="/elderly">老人管理</el-menu-item>
        <el-menu-item index="/doctors">医生管理</el-menu-item>
        <el-menu-item index="/follow-ups">随访管理</el-menu-item>
      </el-menu>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { RouterView } from 'vue-router'
import { createRouter, createWebHistory } from 'vue-router'

</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin: 0;
  padding: 0;
}

.el-header {
  padding: 0;
}
</style>
