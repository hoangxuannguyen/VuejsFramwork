<template>
  <q-card style="min-width: 450px; max-width: 600px">
    <q-card-section class="row items-center q-pb-none">
      <div class="text-h6">
        {{ isEdit ? 'Chỉnh sửa Payingunit' : 'Thêm Payingunit mới' }}
      </div>
      <q-space />
      <q-btn icon="close" flat round dense v-close-popup @click="$emit('cancel')" />
    </q-card-section>

    <q-card-section class="q-gutter-y-md">
      <q-input v-model="form.ten_cong_ty" label="Tên công ty" outlined dense />
      <q-input v-model="form.ma_so_thue" label="Mã số thuế" outlined dense />
      <q-input v-model="form.nguoi_dai_dien" label="Người đại diện" outlined dense />
      <q-input v-model="form.dia_chi" label="Địa chỉ" outlined dense />
      
      <q-select 
        v-model="form.loai_cong_ty" 
        :options="['Cổ phần', 'TNHH', 'Nhà nước', 'Tư nhân']" 
        label="Loại công ty" 
        outlined 
        dense 
      />
    </q-card-section>

    <q-card-actions align="right" class="bg-grey-1 text-primary q-pa-md">
      <q-btn 
        flat 
        label="Hủy bỏ" 
        color="grey-7" 
        @click="$emit('cancel')" 
        v-close-popup 
      />
      <q-btn 
        label="Lưu dữ liệu" 
        color="primary" 
        icon="save"
        @click="onSave" 
      />
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import type { Payingunit } from '../stores/payingunits';

const props = defineProps<{ 
  payingunit: Payingunit | null 
}>();

const emit = defineEmits<{
  (e: 'save', data: Payingunit): void;
  (e: 'cancel'): void;
}>();

const isEdit = computed(() => !!props.payingunit?.id);

const getDefaultForm = (): Payingunit => ({
  id: 0,
  ten_cong_ty: '',
  ma_so_thue: '',
  nguoi_dai_dien: '',
  dia_chi: '',
  loai_cong_ty: '',
} as Payingunit);

const form = ref<Payingunit>(getDefaultForm());

watch(
  () => props.payingunit,
  (newVal) => {
    if (newVal) {
      form.value = { ...newVal };
    } else {
      form.value = getDefaultForm();
    }
  },
  { immediate: true, deep: true }
);

const onSave = () => {
  emit('save', { ...form.value });
};
</script>

<style scoped>
.q-card-section.q-gutter-y-md {
  max-height: 70vh;
  overflow-y: auto;
}
</style>