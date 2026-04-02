import { defineRouter } from '#q-app/wrappers';
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router';
import routes from './routes';
import { useAuthStore } from '../stores/auth'; // Đảm bảo đúng path tới auth store

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default defineRouter(function (/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : process.env.VUE_ROUTER_MODE === 'history'
      ? createWebHistory
      : createWebHashHistory;

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(process.env.VUE_ROUTER_BASE),
  });

  Router.beforeEach((to) => {
    const auth = useAuthStore();

    // Nếu route yêu cầu auth mà user chưa đăng nhập (không có token)
    if (to.meta.requiresAuth && !auth.token) {
      // Lưu lại trang định vào để sau khi login xong có thể quay lại (tùy chọn)
      return {
        name: 'login',
        query: { redirect: to.fullPath },
      };
    }

    // Nếu đã đăng nhập mà cố tình vào trang login thì đẩy về trang chủ
    if (to.path === '/login' && auth.token) {
      return { path: '/' };
    }
  });

  return Router;
});
