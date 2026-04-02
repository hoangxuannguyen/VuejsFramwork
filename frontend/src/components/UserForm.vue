<template>
  <q-card style="min-width: 350px">
    <q-card-section>
      <div class="text-h6">{{ user?.id ? 'Chỉnh sửa User' : 'Thêm User mới' }}</div>
    </q-card-section>

    <q-card-section class="q-pt-none">
      <q-input v-model="formData.email" label="Email" outlined dense class="q-mb-sm" />
      <q-input
        v-model="formData.password"
        label="Mật khẩu"
        type="password"
        outlined
        dense
        class="q-mb-sm"
        :placeholder="user?.id ? '(Để trống nếu không đổi)' : ''"
      />
      <q-toggle v-model="formData.is_active" label="Đang hoạt động" color="green" />
    </q-card-section>

    <q-card-actions align="right">
      <q-btn flat label="Hủy" color="primary" v-close-popup @click="$emit('cancel')" />
      <q-btn flat label="Lưu" color="primary" @click="onSave" />
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import type { User } from '../stores/users';

const props = defineProps<{ user: User | null }>();
const emit = defineEmits(['save', 'cancel']);

// Khởi tạo mặc định
const getDefaultForm = (): Partial<User> => ({
  email: '',
  password: '',
  is_active: true,
});

const formData = ref<Partial<User>>(getDefaultForm());

watch(
  () => props.user,
  (newVal) => {
    if (newVal) {
      // Khi chỉnh sửa: lấy toàn bộ dữ liệu cũ và reset password
      formData.value = { ...newVal, password: '' };
    } else {
      // Khi tạo mới: Reset về giá trị mặc định (có chứa id: 0)
      formData.value = getDefaultForm();
    }
  },
  { immediate: true },
);

const onSave = () => {
  // Tạo một bản sao để xử lý trước khi gửi
  const payload = { ...formData.value };

  // Đảm bảo luôn có id là số (number)
  if (payload.id === undefined || payload.id === null) {
    payload.id = 0;
  }

  emit('save', payload);
};
</script>
