import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'


// (async () => {
//   await store.dispatch('init');
//   createApp(App).use(store).use(router).mount('#app');
// })();

createApp(App).use(store).use(router).mount('#app');