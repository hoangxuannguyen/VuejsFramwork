<template>
  <q-page class="q-pa-md">
    <q-btn-group outline class="q-mb-md">
      <q-btn color="primary" icon="add" label="Thêm mới" @click="openAddDialog" />
      <q-btn color="green" icon="upload" label="Import CSV" @click="triggerImport" />
      <q-btn color="amber" icon="download" label="Export CSV" @click="store.exportCSV()" />
      <q-btn
        color="negative"
        icon="delete"
        label="Xóa đã chọn"
        @click="deleteSelected"
        :disable="!selected.length || store.isLoading"
      />
    </q-btn-group>

    <q-input v-model="filter" placeholder="Tìm kiếm nhanh..." outlined dense clearable>
      <template v-slot:append>
        <q-icon name="search" />
      </template>
    </q-input>

    <q-table
      class="q-mt-md"
      :rows="store.items"
      :columns="columns"
      row-key="id"
      v-model:pagination="pagination"
      :filter="filter"
      selection="multiple"
      v-model:selected="selected"
      :loading="store.isLoading"
      no-data-label="Không có dữ liệu"
      rows-per-page-label="Số dòng mỗi trang:"
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
            {{ props.row[col.name as keyof Payingunit] }}
          </q-td>

          <q-td align="center">
            <q-btn flat round icon="edit" color="primary" @click="editRow(props.row)">
              <q-tooltip>Chỉnh sửa</q-tooltip>
            </q-btn>
            <q-btn flat round icon="delete" color="negative" @click="confirmDelete(props.row.id)">
              <q-tooltip>Xóa</q-tooltip>
            </q-btn>
          </q-td>
        </q-tr>
      </template>
    </q-table>

    <q-dialog v-model="showDialog" persistent>
      <PayingunitForm :payingunit="editingData" @save="handleSave" @cancel="closeDialog" />
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
import { useQuasar, type QTableColumn } from 'quasar';
import { usePayingunitsStore, type Payingunit } from '../stores/payingunits';
import PayingunitForm from '../components/PayingunitForm.vue';

const $q = useQuasar();
const store = usePayingunitsStore();

const columns: QTableColumn[] = [
  { name: 'ten_cong_ty', label: 'Tên công ty', field: 'ten_cong_ty', align: 'left' as const },
  { name: 'ma_so_thue', label: 'Mã số thuế', field: 'ma_so_thue', align: 'left' as const },
  {
    name: 'nguoi_dai_dien',
    label: 'Người đại diện',
    field: 'nguoi_dai_dien',
    align: 'left' as const,
  },
  { name: 'dia_chi', label: 'Địa chỉ', field: 'dia_chi', align: 'left' as const },
  { name: 'loai_cong_ty', label: 'Loại công ty', field: 'loai_cong_ty', align: 'left' as const },
  { name: 'actions', label: 'Thao tác', field: 'id', align: 'center' },
];

const filter = ref('');
const selected = ref<Payingunit[]>([]);
const showDialog = ref(false);
const editingData = ref<Payingunit | null>(null);
const importInput = ref<HTMLInputElement | null>(null);
const pagination = ref({ rowsPerPage: 10, sortBy: 'id', descending: true });

onMounted(() => {
  void store.fetchPayingunits();
});

const openAddDialog = () => {
  editingData.value = null;
  showDialog.value = true;
};

const editRow = (row: Payingunit) => {
  editingData.value = { ...row };
  showDialog.value = true;
};

const closeDialog = () => {
  showDialog.value = false;
  editingData.value = null;
};

const handleSave = async (data: Payingunit) => {
  try {
    if (data.id && data.id !== 0) {
      await store.updatePayingunit(data.id, data);
      $q.notify({ type: 'positive', message: 'Cập nhật thành công' });
    } else {
      const payload = { ...data } as Partial<Payingunit>;
      delete payload.id;

      await store.createPayingunit(payload as Omit<Payingunit, 'id'>);
      $q.notify({ type: 'positive', message: 'Thêm mới thành công' });
    }
    closeDialog();
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : 'Lỗi lưu dữ liệu';
    $q.notify({ type: 'negative', message: msg });
  }
};

const confirmDelete = (id: number) => {
  $q.dialog({
    title: 'Xác nhận xóa',
    message: 'Bạn có chắc chắn muốn xóa mục này?',
    cancel: true,
    persistent: true,
  }).onOk(() => {
    void (async () => {
      try {
        await store.deletePayingunit(id);
        $q.notify({ type: 'positive', message: 'Đã xóa mục thành công' });
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Lỗi khi xóa';
        $q.notify({ type: 'negative', message: msg });
      }
    })();
  });
};

const deleteSelected = () => {
  if (selected.value.length === 0) return;

  $q.dialog({
    title: 'Xác nhận xóa nhiều',
    message: `Bạn có chắc chắn muốn xóa ${selected.value.length} mục đã chọn?`,
    cancel: true,
    persistent: true,
  }).onOk(() => {
    void (async () => {
      try {
        $q.loading.show({ message: 'Đang xử lý...' });
        for (const item of selected.value) {
          await store.deletePayingunit(item.id);
        }
        selected.value = [];
        $q.notify({ type: 'positive', message: 'Đã xóa các mục đã chọn' });
      } catch (err: unknown) {
        // FIX: Sử dụng err để lấy tin nhắn lỗi, giúp tránh lỗi 'err' is defined but never used
        const msg = err instanceof Error ? err.message : 'Có lỗi xảy ra trong quá trình xóa';
        $q.notify({ type: 'negative', message: msg });
      } finally {
        $q.loading.hide();
      }
    })();
  });
};

const triggerImport = () => {
  importInput.value?.click();
};

const handleImport = (e: Event) => {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    void (async () => {
      try {
        $q.loading.show({ message: 'Đang import dữ liệu CSV...' });
        await store.importCSV(file);
        $q.notify({ type: 'positive', message: 'Import hoàn tất' });
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Lỗi Import';
        $q.notify({ type: 'negative', message: msg });
      } finally {
        target.value = '';
        $q.loading.hide();
      }
    })();
  }
};
</script>
