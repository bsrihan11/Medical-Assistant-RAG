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
    children: [
      {
        path: 'new',
        name: 'NewChat',
        component: () => import(/* webpackChunkName: "Medical Assistant" */ '../views/MedicalAssistantView.vue'),
        props: { isNew: true }
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

export default router
