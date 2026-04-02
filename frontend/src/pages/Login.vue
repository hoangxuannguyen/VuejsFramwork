<template>
  <q-page class="flex flex-center bg-light-blue-1">
    <q-card style="width: 100%; max-width: 400px" class="q-pa-md shadow-2">
      <q-card-section>
        <div class="text-h5 text-bold text-center q-mb-md color-primary">
          🔐 Đăng nhập Hệ thống Bảo hiểm
        </div>

        <q-form @submit="login" class="q-gutter-y-md">
          <q-input v-model="email" label="Email" outlined dense type="email" autofocus>
            <template v-slot:prepend>
              <q-icon name="email" />
            </template>
          </q-input>

          <q-input v-model="password" label="Mật khẩu" outlined dense type="password">
            <template v-slot:prepend>
              <q-icon name="lock" />
            </template>
          </q-input>

          <div>
            <q-btn
              label="Đăng nhập"
              type="submit"
              color="primary"
              class="full-width q-mt-sm"
              rounded
              unelevated
            />
          </div>
        </q-form>
      </q-card-section>

      <q-card-section class="text-center q-pt-none">
        <div class="text-grey-7 cursor-pointer">Quên mật khẩu?</div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { ref } from 'vue';

const email = ref('');
const password = ref('');

const authStore = useAuthStore();
const router = useRouter();

const login = async () => {
  try {
    await authStore.login(email.value, password.value);
    void router.push('/profiles'); // hoặc '/users' tùy bạn muốn vào trang nào
  } catch (err: unknown) {
    if (err instanceof Error) {
      alert(err.message);
    } else {
      alert('An unknown error occurred');
    }
  }
};
</script>
