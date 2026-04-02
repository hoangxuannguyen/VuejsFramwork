<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated class="bg-teal-7">
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleMiniMode" />

        <q-toolbar-title> Insurance management </q-toolbar-title>

        <q-btn
          v-if="authStore.isLoggedIn"
          flat
          round
          dense
          icon="logout"
          label="Logout"
          @click="handleLogout"
        />
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      :mini="miniState"
      :width="250"
      :mini-width="70"
      class="bg-grey-2"
    >
      <q-list>
        <q-item class="non-clickable text-teal-9 text-weight-bold" style="opacity: 1">
          <q-item-section avatar>
            <q-icon name="list" />
          </q-item-section>

          <q-item-section>
            <q-item-label>QUẢN LÝ</q-item-label>
          </q-item-section>
        </q-item>

        <q-separator v-if="!miniState" />

        <EssentialLink v-for="link in linksList" :key="link.title" v-bind="link" />
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import EssentialLink, { type EssentialLinkProps } from 'components/EssentialLink.vue';
import { useRouter } from 'vue-router';
const linksList: EssentialLinkProps[] = [
  { title: 'Users', caption: 'Quản lý người dùng', icon: 'group', link: '/users' },
  { title: 'Profiles', caption: 'Thông tin cá nhân', icon: 'person', link: '/profiles' },
  { title: 'Đơn vị Nộp Tiền', caption: 'Đơn vị Nộp Tiền', icon: 'group', link: '/payingunits' },
];

const router = useRouter();
const authStore = useAuthStore();
console.log(authStore.isLoggedIn);
const leftDrawerOpen = ref(true);
// Mặc định mở rộng
const miniState = ref(false);

function toggleMiniMode() {
  miniState.value = !miniState.value;
}

function handleLogout() {
  try {
    // 1. Gọi hàm logout từ store (xóa token, state...)
    authStore.logout();
    void router.push('/login');
  } catch (error) {
    console.error('Lỗi khi đăng xuất:', error);
  }
}
</script>

<style scoped>
/* Class CSS nhỏ để làm cho 'item' tiêu đề không có hiệu ứng hover của nút bấm */
.non-clickable {
  cursor: default !important;
  pointer-events: none; /* Ngăn chặn hover effect */
}
</style>
