// src/utils/request.js

import axios from 'axios';

const instance = axios.create({
  baseURL: import.meta.env.VITE_APP_API_URL, // 根据环境变量设置基础URL
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json'
  }
});

export default instance;
