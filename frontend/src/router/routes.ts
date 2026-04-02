import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '/', redirect: '/profiles' },
      { path: '', component: () => import('pages/IndexPage.vue') },
      {
        path: '/login',
        name: 'login',
        component: () => import('pages/Login.vue'),
        meta: { requiresAuth: false },
      },
      {
        path: '/profiles',
        name: 'profiles',
        component: () => import('pages/Profiles.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: '/users',
        name: 'users',
        component: () => import('pages/UsersPage.vue'),
        meta: { requiresAuth: true },
      },
      { path: 'payingunits', component: () => import('pages/PayingunitPage.vue') },
      // %GENERATED_ROUTES_HERE%
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
