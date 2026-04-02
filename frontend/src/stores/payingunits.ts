import { defineStore } from 'pinia';
import axios from 'axios';
import Papa from 'papaparse';
import { useAuthStore } from './auth';

const API_BASE = process.env.API_URL || 'http://localhost:8000';

export interface Payingunit {
  id: number;
  ten_cong_ty: string;
  ma_so_thue: string;
  nguoi_dai_dien: string;
  dia_chi: string;
  loai_cong_ty: string;
}

interface PayingunitResponse {
  data: Payingunit[];
  total: number;
}

type CSVPayingunitRow = Omit<Payingunit, 'id'>;

interface PayingunitState {
  items: Payingunit[];
  isLoading: boolean;
  error: string | null;
}

export const usePayingunitsStore = defineStore('payingunits', {
  state: (): PayingunitState => ({
    items: [] as Payingunit[],
    isLoading: false,
    error: null,
  }),

  actions: {
    getAuthHeader() {
      const authStore = useAuthStore();
      if (!authStore.token) throw new Error('Không có token xác thực');
      return {
        headers: { Authorization: `Bearer ${authStore.token}` },
      };
    },

    async fetchPayingunits(): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.get<PayingunitResponse | Payingunit[]>(
          `${API_BASE}/paying-units/`,
          this.getAuthHeader(),
        );

        if (Array.isArray(response.data)) {
          this.items = response.data;
        } else if (response.data && 'data' in response.data) {
          this.items = response.data.data;
        }
      } catch (err: unknown) {
        this.handleError(err, 'Lỗi tải danh sách payingunit');
      } finally {
        this.isLoading = false;
      }
    },

    async createPayingunit(data: CSVPayingunitRow): Promise<void> {
      this.isLoading = true;
      try {
        await axios.post(`${API_BASE}/paying-units/`, { id: 0, ...data }, this.getAuthHeader());
        await this.fetchPayingunits();
      } catch (err: unknown) {
        this.handleError(err, 'Lỗi khi tạo mới');
      } finally {
        this.isLoading = false;
      }
    },

    async updatePayingunit(id: number, data: Partial<CSVPayingunitRow>): Promise<void> {
      this.isLoading = true;
      try {
        await axios.put(`${API_BASE}/paying-units/${id}`, data, this.getAuthHeader());
        await this.fetchPayingunits();
      } catch (err: unknown) {
        this.handleError(err, 'Lỗi khi cập nhật');
      } finally {
        this.isLoading = false;
      }
    },

    async deletePayingunit(id: number): Promise<void> {
      this.isLoading = true;
      try {
        await axios.delete(`${API_BASE}/paying-units/${id}`, this.getAuthHeader());
        this.items = this.items.filter((item) => item.id !== id);
      } catch (err: unknown) {
        this.handleError(err, 'Lỗi khi xóa');
      } finally {
        this.isLoading = false;
      }
    },

    async importCSV(file: File): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        await new Promise<void>((resolve, reject) => {
          Papa.parse(file, {
            header: true,
            skipEmptyLines: true,
            complete: (result) => {
              const processRows = async () => {
                try {
                  // Thay thế any[] bằng Record để tránh lỗi ESLint "Unexpected any"
                  const rows = result.data as Record<string, string>[];
                  for (const row of rows) {
                    const payload = {
                      ten_cong_ty: row.ten_cong_ty || '',
                      ma_so_thue: row.ma_so_thue || '',
                      nguoi_dai_dien: row.nguoi_dai_dien || '',
                      dia_chi: row.dia_chi || '',
                      loai_cong_ty: row.loai_cong_ty || '',
                    };
                    await axios.post(
                      `${API_BASE}/paying-units/`,
                      { id: 0, ...payload },
                      this.getAuthHeader(),
                    );
                  }
                  resolve();
                } catch (err) {
                  // Đảm bảo reject luôn trả về một Error object
                  reject(err instanceof Error ? err : new Error(String(err)));
                }
              };
              void processRows();
            },
            error: (error: Error) => reject(error),
          });
        });
        await this.fetchPayingunits();
      } catch (err: unknown) {
        this.handleError(err, 'Lỗi Import CSV');
      } finally {
        this.isLoading = false;
      }
    },

    exportCSV(): void {
      if (this.items.length === 0) return alert('Không có dữ liệu!');
      const exportData = this.items.map(
        (item): CSVPayingunitRow => ({
          ten_cong_ty: item.ten_cong_ty,
          ma_so_thue: item.ma_so_thue,
          nguoi_dai_dien: item.nguoi_dai_dien,
          dia_chi: item.dia_chi,
          loai_cong_ty: item.loai_cong_ty,
        }),
      );
      const csv = Papa.unparse(exportData);
      const blob = new Blob([new Uint8Array([0xef, 0xbb, 0xbf]), csv], {
        type: 'text/csv;charset=utf-8;',
      });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `payingunits_export.csv`;
      link.click();
      URL.revokeObjectURL(link.href);
    },

    handleError(err: unknown, defaultMsg: string) {
      let message = defaultMsg;
      if (axios.isAxiosError(err)) {
        // Ép kiểu cục bộ để truy cập data mà không cần import AxiosError toàn cục
        const responseData = err.response?.data as { detail?: string } | undefined;
        message = responseData?.detail || err.message || defaultMsg;
        if (err.response?.status === 401) useAuthStore().logout();
      } else if (err instanceof Error) {
        message = err.message;
      }
      this.error = message;
      // Không ném lỗi (throw) ở đây nếu bạn muốn UI chỉ hiển thị thông báo lỗi qua state.error
      // Nếu vẫn muốn throw, hãy đảm bảo component bắt được nó.
    },
  },
});
