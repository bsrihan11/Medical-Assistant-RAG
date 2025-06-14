import { createRouter, createWebHistory } from 'vue-router'
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import(/* webpackChunkName: "User Login" */ '../views/LoginView.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import(/* webpackChunkName: "User Registration" */ '../views/RegisterView.vue')
  },
  {
    path: '/chat',
    component: () => import(/* webpackChunkName: "Medical Assistant" */ '../views/MedicalAssistantView.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'new',
        name: 'NewChat',
        component: () => import(/* webpackChunkName: "Medical Assistant" */ '../views/MedicalAssistantView.vue'),
        props: true
      },
      {
        path: ':chatId',
        name: 'ChatById',
        component: () => import(/* webpackChunkName: "Medical Assistant" */ '../views/MedicalAssistantView.vue'),
        props: true
      }
    ]
  },
  // fallback or redirect
  { path: '/:pathMatch(.*)*', redirect: '/chat/new' },

]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

import store from '@/store'

router.beforeEach(async (to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (!requiresAuth) return next()

  // Check if user is already in store
  let user = store.getters.getUser

  // If not, try to initialize (e.g., fetch from backend using token)
  if (!user) {
    try {
      await store.dispatch('init')
      user = store.getters.getUser
    } catch (err) {
      console.error('Error during user init:', err)
    }
  }

  // If user is still not loaded, redirect to login
  if (!user) {
    return next({ name: 'Login' })
  }

  next()
})

export default router
