<!-- src/App.vue -->
<template>
  <!-- 路由视图：所有页面（Login/Register/Home）都会渲染到这里 -->
  <router-view />
</template>

<script setup>
// 你的项目暂时不需要额外逻辑，这里留空即可
</script>

<style>
/* 全局样式：作用于整个项目（不加 scoped） */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: "Microsoft YaHei", sans-serif;
}

/* 去掉 Element Plus 按钮/输入框的默认边框聚焦样式（可选优化） */
.el-input__wrapper:focus-within {
  box-shadow: none !important;
}
.el-button:focus {
  outline: none !important;
}
</style>