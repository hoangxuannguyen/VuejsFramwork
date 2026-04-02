<template>
  <q-card style="width: 500px">
    <q-card-section>
      <q-input v-model="form.ho_ten" label="Họ tên" />
      <q-input v-model="form.ngay_sinh" type="date" label="Ngày sinh" />
      <q-select v-model="form.gioi_tinh" :options="['Nam', 'Nữ']" label="Giới tính" />
      <q-input v-model="form.cccd" label="Số CCCD" />
      <q-input v-model="form.ngay_tham_gia" type="date" label="Ngày tham gia BH" />
      <q-input v-model="form.dia_chi" label="Địa chỉ" />
    </q-card-section>
    <q-card-actions>
      <q-btn flat label="Hủy" color="negative" @click="$emit('cancel')" />
      <q-btn label="Lưu" color="primary" @click="save" />
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { Profile } from '../stores/profiles';

const props = defineProps<{ profile: Profile | null }>();
const emit = defineEmits(['save', 'cancel']);

const form = ref({
  id: props.profile?.id || 0,
  stt: props.profile?.stt || 0,
  ho_ten: props.profile?.ho_ten || '',
  ngay_sinh: props.profile?.ngay_sinh || '',
  gioi_tinh: props.profile?.gioi_tinh || 'Nam',
  cccd: props.profile?.cccd || '',
  ngay_tham_gia: props.profile?.ngay_tham_gia || '',
  dia_chi: props.profile?.dia_chi || '',
});

const save = () => emit('save', form.value);
</script>
