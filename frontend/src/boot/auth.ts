import { boot } from 'quasar/wrappers';
import { useAuthStore } from 'src/stores/auth';

export default boot(async () => {
  const auth = useAuthStore();
  await auth.init();
});
