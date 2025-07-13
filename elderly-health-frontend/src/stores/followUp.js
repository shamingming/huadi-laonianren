import { defineStore } from 'pinia'
import followUpApi from '@/api/followUp'

export const useFollowUpStore = defineStore('followUp', {
  state: () => ({
    list: [],
    loading: false
  }),

  actions: {
    async loadFollowUps(params = {}) {
      this.loading = true
      try {
        this.list = await followUpApi.getFollowUps(params)
      } finally {
        this.loading = false
      }
    },

    async addFollowUp(data) {
      const newItem = await followUpApi.createFollowUp(data)
      this.list.unshift(newItem)
      return newItem
    }
  }
})