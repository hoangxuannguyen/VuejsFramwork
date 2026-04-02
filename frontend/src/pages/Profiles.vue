<template>
  <q-page class="q-pa-md">
    <q-btn-group outline>
      <q-btn color="primary" icon="add" label="Thêm mới" @click="openAddDialog" />
      <q-btn color="green" icon="upload" label="Import CSV" @click="triggerImport" />
      <q-btn color="amber" icon="download" label="Export CSV" @click="store.exportCSV()" />
      <q-btn
        color="negative"
        icon="delete"
        label="Xóa đã chọn"
        @click="deleteSelected"
        :disable="!selected.length"
      />
    </q-btn-group>

    <q-input v-model="filter" placeholder="Tìm kiếm hồ sơ..." class="q-mt-md" outlined dense>
      <template v-slot:append>
        <q-icon name="search" />
      </template>
    </q-input>

    <q-table
      class="q-mt-md"
      :rows="store.profiles || []"
      :columns="columns"
      row-key="id"
      v-model:pagination="pagination"
      :filter="filter"
      selection="multiple"
      v-model:selected="selected"
      :loading="store.isLoading"
    >
      <template v-slot:body="props">
        <q-tr :props="props">
          <q-td auto-width>
            <q-checkbox v-model="props.selected" />
          </q-td>
          <q-td
            v-for="col in columns.filter((c) => c.name !== 'actions')"
            :key="col.name"
            :props="props"
          >
            {{ props.row[col.name as keyof Profile] }}
          </q-td>
          <q-td align="center">
            <q-btn flat round icon="edit" color="primary" @click="editRow(props.row)" />
            <q-btn flat round icon="delete" color="negative" @click="deleteRow(props.row.id)" />
          </q-td>
        </q-tr>
      </template>
    </q-table>

    <q-dialog v-model="showDialog" persistent>
      <ProfileForm :profile="editingProfile" @save="saveProfile" @cancel="closeDialog" />
    </q-dialog>

    <input
      ref="importInput"
      type="file"
      accept=".csv"
      style="display: none"
      @change="handleImport"
    />
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useProfilesStore, type Profile } from '../stores/profiles';
import ProfileForm from '../components/ProfileForm.vue';
import { useQuasar } from 'quasar';

const $q = useQuasar();
const store = useProfilesStore();

const columns = [
  { name: 'stt', label: 'STT', field: 'stt', align: 'left' as const },
  { name: 'ho_ten', label: 'Họ tên', field: 'ho_ten', align: 'left' as const }, // Sửa hoTen -> ho_ten
  { name: 'ngay_sinh', label: 'Ngày sinh', field: 'ngay_sinh', align: 'left' as const }, // Sửa ngaySinh -> ngay_sinh
  { name: 'gioi_tinh', label: 'Giới tính', field: 'gioi_tinh', align: 'left' as const },
  { name: 'cccd', label: 'CCCD', field: 'cccd', align: 'left' as const },
  { name: 'dia_chi', label: 'Địa chỉ', field: 'dia_chi', align: 'left' as const },
  { name: 'actions', label: 'Thao tác', field: 'id', align: 'center' as const },
];

const filter = ref('');
const selected = ref<Profile[]>([]);
const showDialog = ref(false);
const editingProfile = ref<Profile | null>(null);
const importInput = ref<HTMLInputElement | null>(null);
const pagination = ref({ rowsPerPage: 10 });

onMounted(async () => {
  try {
    await store.fetchProfiles();
  } catch (err: unknown) {
    // FIX: Sử dụng biến err hoặc đổi thành _err để hết lỗi 'defined but never used'
    console.error('Lỗi tải dữ liệu:', err);
  }
});

const openAddDialog = () => {
  editingProfile.value = null;
  showDialog.value = true;
};

const closeDialog = () => {
  showDialog.value = false;
  editingProfile.value = null;
};

const editRow = (row: Profile) => {
  editingProfile.value = { ...row };
  showDialog.value = true;
};

const saveProfile = async (p: Profile) => {
  try {
    if (p.id) {
      // Đảm bảo tên hàm là updateProfile khớp với Store
      await store.updateProfile(p.id, p);
    } else {
      await store.createProfile({
        ho_ten: p.ho_ten,
        ngay_sinh: p.ngay_sinh,
        gioi_tinh: p.gioi_tinh,
        cccd: p.cccd,
        ngay_tham_gia: p.ngay_tham_gia,
        dia_chi: p.dia_chi,
      });
    }
    closeDialog();
    $q.notify({ type: 'positive', message: 'Thành công' });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : 'Lỗi không xác định';
    $q.notify({ type: 'negative', message: msg });
  }
};

const deleteRow = async (id: number) => {
  try {
    await store.deleteProfile(id);
  } catch (_err: unknown) {
    // Không dùng err thì đặt tên là _err
    console.error('Lỗi xóa hồ sơ:', _err);
  }
};

// FIX: Xử lý lỗi 'Promise returned where void was expected' bằng cách tách hàm xử lý async
const performDeleteSelected = async () => {
  try {
    for (const item of selected.value) {
      await store.deleteProfile(item.id);
    }
    selected.value = [];
    $q.notify({ type: 'positive', message: 'Đã xóa các mục đã chọn' });
  } catch (err: unknown) {
    console.error(err);
  }
};

const deleteSelected = () => {
  if (selected.value.length === 0) return;

  $q.dialog({
    title: 'Xác nhận',
    message: `Xóa ${selected.value.length} hồ sơ?`,
    cancel: true,
  }).onOk(() => {
    // Gọi hàm async từ callback void của Quasar
    void performDeleteSelected();
  });
};

const triggerImport = () => {
  importInput.value?.click();
};

const handleImport = async (e: Event) => {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    try {
      await store.importCSV(file);
    } catch (err: unknown) {
      console.error(err);
    } finally {
      target.value = '';
    }
  }
};
</script>
