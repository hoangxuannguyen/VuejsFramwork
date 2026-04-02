import { defineStore } from 'pinia';
import axios, { type AxiosError } from 'axios';
import Papa from 'papaparse';
import { useAuthStore } from './auth';

const API_BASE = 'http://localhost:8000';

export interface Profile {
  id: number;
  stt: number;
  ho_ten: string;
  ngay_sinh: string;
  gioi_tinh: 'Nam' | 'Nữ';
  cccd: string;
  ngay_tham_gia: string;
  dia_chi: string;
}

interface ProfileResponse {
  data: Profile[]; // Đây mới là mảng 2 người bạn thấy trong console
  total: number;
}

// CSVProfileRow đồng nhất hoàn toàn với các trường dữ liệu thực tế của Profile (trừ id, stt)
type CSVProfileRow = Omit<Profile, 'id' | 'stt'>;

interface ProfilesState {
  profiles: Profile[];
  isLoading: boolean;
  error: string | null;
}

export const useProfilesStore = defineStore('profiles', {
  state: (): ProfilesState => ({
    profiles: [] as Profile[],
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

    async fetchProfiles(): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.get<ProfileResponse>(
          `${API_BASE}/profile/`,
          this.getAuthHeader(),
        );
        if (response.data && Array.isArray(response.data.data)) {
          // Chúng ta cần lấy cái mảng nằm bên trong biến 'data'
          this.profiles = response.data.data;
        } else {
          this.profiles = [];
        }

        console.log('Dữ liệu đã gán vào store:', this.profiles);
      } catch (err: unknown) {
        this.handleError(err, 'Lỗi tải danh sách hồ sơ');
      } finally {
        this.isLoading = false;
      }
    },

    // 1. CREATE
    async createProfile(profileData: CSVProfileRow): Promise<void> {
      this.isLoading = true;
      try {
        console.log(profileData);
        await axios.post(`${API_BASE}/profile/`, profileData, this.getAuthHeader());
        await this.fetchProfiles(); // Tải lại danh sách mới
      } catch (err: unknown) {
        this.handleError(err, 'Lỗi khi thêm hồ sơ mới');
      } finally {
        this.isLoading = false;
      }
    },

    // 2. UPDATE
    async updateProfile(id: number, profileData: Partial<CSVProfileRow>): Promise<void> {
      this.isLoading = true;
      try {
        await axios.put(`${API_BASE}/profile/${id}`, profileData, this.getAuthHeader());
        await this.fetchProfiles(); // Tải lại danh sách sau khi cập nhật
      } catch (err: unknown) {
        this.handleError(err, 'Lỗi khi cập nhật hồ sơ');
      } finally {
        this.isLoading = false;
      }
    },

    // 3. DELETE
    async deleteProfile(id: number): Promise<void> {
      this.isLoading = true;
      try {
        await axios.delete(`${API_BASE}/profile/${id}`, this.getAuthHeader());
        // Tối ưu: Xóa trực tiếp trên state để không phải gọi lại fetchProfiles (giảm tải Server)
        this.profiles = this.profiles.filter((p) => p.id !== id);
      } catch (err: unknown) {
        this.handleError(err, 'Lỗi khi xóa hồ sơ');
      } finally {
        this.isLoading = false;
      }
    },

    // 5. IMPORT CSV
    async importCSV(file: File): Promise<void> {
      this.isLoading = true;
      this.error = null;

      try {
        await new Promise<void>((resolve, reject) => {
          Papa.parse(file, {
            header: true,
            skipEmptyLines: true,
            // FIX: Bỏ async ở đây để thỏa mãn 'void return expected'
            complete: (result) => {
              // Tạo một hàm async nội bộ để xử lý logic
              const processRows = async () => {
                try {
                  const rows = result.data as CSVProfileRow[];
                  for (const row of rows) {
                    const profileData: CSVProfileRow = {
                      ho_ten: row.ho_ten || '',
                      ngay_sinh: row.ngay_sinh || '',
                      gioi_tinh: row.gioi_tinh === 'Nữ' ? 'Nữ' : 'Nam',
                      cccd: row.cccd || '',
                      ngay_tham_gia: row.ngay_tham_gia || '',
                      dia_chi: row.dia_chi || '',
                    };
                    console.log(profileData);
                    await axios.post(`${API_BASE}/profile/`, profileData, this.getAuthHeader());
                  }
                  resolve();
                } catch (err: unknown) {
                  reject(err instanceof Error ? err : new Error('Lỗi lưu dữ liệu API'));
                }
              };

              // Gọi hàm processRows và đánh dấu là void
              void processRows();
            },
            error: (error: Error) => {
              reject(new Error(error.message));
            },
          });
        });

        await this.fetchProfiles();
        // Thay alert bằng thông báo nếu cần, hoặc để Profiles.vue xử lý
      } catch (err: unknown) {
        this.handleError(err, 'Lỗi quá trình Import CSV');
      } finally {
        this.isLoading = false;
      }
    },

    // 6. EXPORT CSV
    exportCSV(): void {
      if (this.profiles.length === 0) {
        alert('Không có dữ liệu để xuất!');
        return;
      }

      const csvData = this.profiles.map(
        (p): CSVProfileRow => ({
          ho_ten: p.ho_ten,
          ngay_sinh: p.ngay_sinh,
          gioi_tinh: p.gioi_tinh,
          cccd: p.cccd,
          ngay_tham_gia: p.ngay_tham_gia,
          dia_chi: p.dia_chi,
        }),
      );

      const csv = Papa.unparse(csvData);

      const blob = new Blob([new Uint8Array([0xef, 0xbb, 0xbf]), csv], {
        type: 'text/csv;charset=utf-8;',
      });

      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `profiles_export_${new Date().getTime()}.csv`;
      link.click();
      URL.revokeObjectURL(link.href);
    },

    handleError(err: unknown, defaultMsg: string) {
      let message = defaultMsg;
      if (axios.isAxiosError(err)) {
        const axiosErr = err as AxiosError<{ detail?: string }>;
        message = axiosErr.response?.data?.detail || axiosErr.message || defaultMsg;
        if (axiosErr.response?.status === 401) useAuthStore().logout();
      } else if (err instanceof Error) {
        message = err.message;
      }
      this.error = message;
      console.error(`[ProfilesStore]: ${message}`);
      throw new Error(message);
    },
  },
});
