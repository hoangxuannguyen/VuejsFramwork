<template>
  <q-page class="q-pa-md">
    <div class="row q-gutter-sm q-mb-md">
      <q-btn color="primary" icon="add" label="Thêm User" @click="openAddDialog" />
    </div>

    <q-table
      :rows="store.users"
      :columns="columns"
      row-key="id"
      :loading="store.isLoading"
      flat
      bordered
    >
      <template v-slot:body-cell-is_active="props">
        <q-td :props="props">
          <q-chip :color="props.value ? 'green' : 'red'" text-color="white" dense>
            {{ props.value ? 'Active' : 'Inactive' }}
          </q-chip>
        </q-td>
      </template>

      <template v-slot:body-cell-actions="props">
        <q-td :props="props" align="center">
          <q-btn flat round icon="edit" color="primary" @click="editUser(props.row)" />
          <q-btn flat round icon="delete" color="negative" @click="confirmDelete(props.row.id)" />
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="showDialog" persistent>
      <UserForm :user="editingUser" @save="saveUser" @cancel="showDialog = false" />
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useUsersStore, type User } from '../stores/users';
import UserForm from '../components/UserForm.vue';
import { useQuasar } from 'quasar';

const store = useUsersStore();
const $q = useQuasar();

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' as const, sortable: true },
  { name: 'email', label: 'Email', field: 'email', align: 'left' as const, sortable: true },
  { name: 'is_active', label: 'Trạng thái', field: 'is_active', align: 'center' as const },
  { name: 'actions', label: 'Thao tác', field: 'id', align: 'center' as const },
];

const showDialog = ref(false);
const editingUser = ref<User | null>(null);

onMounted(() => store.fetchUsers());

const openAddDialog = () => {
  editingUser.value = null;
  showDialog.value = true;
};

const editUser = (user: User) => {
  editingUser.value = { ...user };
  showDialog.value = true;
};

const saveUser = async (data: Partial<User>) => {
  try {
    if (editingUser.value?.id) {
      await store.updateUser(editingUser.value.id, data);
    } else {
      await store.createUser(data);
    }
    showDialog.value = false;
    $q.notify({ type: 'positive', message: 'Cập nhật thành công' });
  } catch (e) {
    console.error(e);
    $q.notify({ type: 'negative', message: 'Có lỗi xảy ra' });
  }
};

const performDelete = async (id: number) => {
  try {
    await store.deleteUser(id);
    $q.notify({ type: 'positive', message: 'Đã xóa' });
  } catch (error) {
    console.error(error);
  }
};

const confirmDelete = (id: number) => {
  $q.dialog({
    title: 'Xác nhận',
    message: 'Bạn có chắc chắn muốn xóa user này?',
    cancel: true,
  }).onOk(() => {
    // Chỉ đơn giản là gọi hàm, không dùng async/await trực tiếp ở đây
    void performDelete(id);
  });
};
</script>
